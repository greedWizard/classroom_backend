from typing import (
    Any,
    Dict,
    List,
    NewType,
    Optional,
    Tuple,
    Type,
    Union,
)

from pydantic import BaseModel

from core.common.models.base import BaseDBModel
from core.common.repositories.base import (
    AbstractBaseRepository,
    CRUDRepository,
    ReadOnlyRepository,
)
from core.common.repositories.exceptions import ObjectAlreadyExistsException
from core.common.services.decorators import action
from core.common.services.exceptions import ServiceMapException


CreateSchema = NewType('CreateSchemaType', BaseModel)
UpdateSchema = NewType('UpdateSchemaType', BaseModel)
DeleteSchema = NewType('DeleteSchemaType', BaseModel)
ResultTuple = NewType('ResultTuple', Tuple[bool, Optional[str]])


class SchemaMapMixin:
    schema_map: dict[str, BaseModel] = {}
    schema_class: Type[BaseModel] = None
    action: str = None

    def get_schema_class(self) -> Type[BaseModel]:
        return self.schema_map.get(self.action, self.schema_class)

    def wrap_object(self, obj: BaseDBModel):
        """Returns pydantic BaseModel object instanced with the provided obj.

        The orm_mode object in schema_map with that action should be set
        to True.

        """
        try:
            return self.get_schema_class().from_orm(obj)
        except AttributeError:
            raise ServiceMapException(
                f'{type(self)} did not define a schema for action {self.action}',
            )

    def wrap_objects(self, objects: list[BaseDBModel]):
        """Returns pydantic BaseModel objects instanced from the provieded list
        of orm objects."""
        return [self.wrap_object(obj) for obj in objects]


class IServiceBase(SchemaMapMixin):
    _repository: AbstractBaseRepository = None
    _action_attributes: Dict = {}

    @property
    def current_action_attributes(self):
        return self._action_attributes.get(self.action, {})

    error_messages: dict[str, str] = {
        'create': 'Could not create new instance',
    }
    required_fields_map = {}
    _errors: Dict = {}

    @action
    async def create(
        self,
        createSchema: CreateSchema,
        exclude_unset: bool = False,
        join: list[str] = None,
    ) -> Tuple[BaseDBModel, Dict]:
        raise NotImplementedError()

    @action
    async def bulk_update(
        self,
        updateSchema: UpdateSchema,
        filters: Dict = {},
        exclude_unset: bool = True,
    ) -> Tuple[BaseDBModel, Dict]:
        raise NotImplementedError()

    @action
    async def bulk_delete(
        self,
        deleteSchema: DeleteSchema,
        filters: Dict = {},
        exclude_unset: bool = True,
    ) -> Tuple[BaseDBModel, Dict]:
        raise NotImplementedError()

    @action
    async def bulk_create(
        self,
        listCreateSchema: List[CreateSchema],
        exclude_unset: bool = True,
    ):
        raise NotImplementedError()

    @action
    async def fetch(
        self,
        filters: Dict = {},
        ordering: List = [],
        distinct: bool = True,
    ):
        raise NotImplementedError()

    @action
    async def retrieve(self, **kwargs):
        raise NotImplementedError()


class CreateUpdateService(IServiceBase):
    required_fields_map: Dict[str, List] = {}
    _repository: CRUDRepository

    async def validate(self, attrs: Dict = None) -> Dict:
        """Method for prevalidating attrs before action."""
        if not attrs:
            attrs = {}

        attrs = {
            field: value
            for field, value in attrs.items()
            if field in self._repository.model_fields
        }
        return attrs

    async def _validate_values(self, **kwargs) -> None:
        """Validates values before creating or updating `model` field
        instances."""
        # TODO: рефакторить
        errors = {}
        self._action_attributes[self.action] = kwargs

        for key, value in kwargs.items():
            validation_method = f'validate_{key}'

            if hasattr(self, validation_method):
                validation_success, validation_error = await getattr(
                    self,
                    validation_method,
                )(value)

                if not validation_success:
                    errors[key] = validation_error

        attrs = await self.validate(kwargs) or kwargs
        return attrs, errors

    @action
    async def create(
        self,
        createSchema: CreateSchema,
        exclude_unset: bool = False,
        join: list[str] = None,
    ) -> Tuple[BaseDBModel, Dict]:
        schema_dict = createSchema.dict(exclude_unset=exclude_unset)
        attrs, errors = await self._validate_values(**schema_dict)

        if errors:
            return None, errors

        try:
            created_object = await self._repository.create(join=join, **attrs)
        except ObjectAlreadyExistsException as e:
            return None, {'error': self.error_messages['create'], 'trace': str(e)}
        return created_object, None

    async def _get_bulk_create_result(
        self,
        listCreateSchema: List[CreateSchema],
    ) -> Tuple[list[BaseDBModel], list[dict[str, Any]]]:
        results = [
            await self.create(createSchema=createSchema)
            for createSchema in listCreateSchema
        ]

        errors = [error for _, error in results]
        created_objects = [obj for obj, _ in results]

        if not any(errors):
            errors = []
        if not any(created_objects):
            created_objects = []
        return created_objects, errors

    @action
    async def bulk_create(
        self,
        listCreateSchema: List[CreateSchema],
    ):
        created_objects, errors = await self._get_bulk_create_result(listCreateSchema)
        return created_objects, errors

    @action
    async def update(
        self,
        id: Union[int, str],
        updateSchema: UpdateSchema,
        join: list[str] = None,
        exclude_unset: bool = True,
    ) -> Tuple[BaseDBModel, Dict]:
        schema_dict = updateSchema.dict(exclude_unset=exclude_unset)
        attrs, errors = await self._validate_values(**schema_dict)

        if errors:
            return None, errors

        updated_instance = await self._repository.update_and_return_single(
            values=attrs,
            join=join,
            id=id,
        )
        return updated_instance, {}

    @action
    async def bulk_update(
        self,
        updateSchema: UpdateSchema,
        filters: Dict = {},
        exclude_unset: bool = True,
    ) -> Tuple[BaseDBModel, Dict]:
        """Update multiple objects fitting assigned filters."""
        schema_dict = updateSchema.dict(exclude_unset=exclude_unset)
        errors = await self._validate_values(**schema_dict)

        if errors:
            return None, errors
        async with self._repository() as repo:
            return await repo.bulk_update(filters=filters, **schema_dict), {}


class RetrieveFetchServiceMixin(IServiceBase):
    _repository: ReadOnlyRepository

    async def fetch(
        self,
        _ordering: List = [],
        join: list[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        **filters,
    ):
        return (
            await self._repository.fetch(
                _ordering,
                join,
                limit=limit,
                offset=offset,
                **filters,
            ),
            None,
        )

    @action
    async def retrieve(self, _join: Optional[list[str]] = None, **filters):
        return await self._repository.retrieve(join=_join, **filters), {}

    @action
    async def exists(self, **filters):
        return await self._repository.exists(**filters)


class DeleteMixin(IServiceBase):
    async def _validate_delete(self, attrs: Dict):
        return attrs, {}

    async def _validate_bulk_delete(self, **kwargs):
        qs = await self.get_queryset(management=True)
        return await qs.filter(**kwargs).exists()

    @action
    async def delete(self, **filters):
        return await self._repository.delete(**filters), None

    @action
    async def bulk_delete(
        self,
        **kwargs,
    ) -> Tuple[BaseDBModel, Dict]:
        if not await self._validate_bulk_delete(**kwargs):
            return {'permission_error': 'You are not allowed to do that!'}
        qs = await self.get_queryset(management=True)
        await qs.filter(**kwargs).delete()
        return None


class CRUDService(CreateUpdateService, RetrieveFetchServiceMixin, DeleteMixin):
    """CrudService for performing CRUD operations and validation.

    ! All manager's operations only avaliable from that class and it's
    subclasses methods!

    """

    def __init__(self) -> None:
        self.user = None
