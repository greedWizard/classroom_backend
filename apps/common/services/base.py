from typing import (
    Dict,
    List,
    NewType,
    Tuple,
    Type,
    Union,
)

from pydantic import BaseModel
from tortoise import models
from tortoise.transactions import atomic

from apps.common.models.base import BaseDBModel
from apps.common.repositories.base import (
    AbstractBaseRepository,
    CRUDRepository,
)
from apps.common.services.decorators import action
from apps.common.services.exceptions import ServiceMapException


CreateSchema = NewType('CreateSchemaType', BaseModel)
UpdateSchema = NewType('UpdateSchemaType', BaseModel)
DeleteSchema = NewType('DeleteSchemaType', BaseModel)
ResultTuple = NewType('ResultTuple', Tuple[bool, Union[Dict, None]])


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

    error_messages = {
        'does_not_exist': 'Not found.',
        'no_values_found': 'No values were found {values}.',
        'already_exists': 'Already exists.',
    }
    required_fields_map = {}
    _errors: Dict = {}

    @action
    async def create(
        self,
        createSchema: CreateSchema,
        exclude_unset: bool = False,
    ) -> Tuple[models.Model, Dict]:
        raise NotImplementedError()

    @action
    @atomic()
    async def bulk_update(
        self,
        updateSchema: UpdateSchema,
        filters: Dict = {},
        exclude_unset: bool = True,
    ) -> Tuple[models.Model, Dict]:
        raise NotImplementedError()

    @action
    @atomic()
    async def bulk_delete(
        self,
        deleteSchema: DeleteSchema,
        filters: Dict = {},
        exclude_unset: bool = True,
    ) -> Tuple[models.Model, Dict]:
        raise NotImplementedError()

    @action
    @atomic()
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

    async def validate(self, attrs: Dict = {}) -> Dict:
        """Method for prevalidating attrs before action."""
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
    ) -> Tuple[models.Model, Dict]:
        schema_dict = createSchema.dict(exclude_unset=exclude_unset)
        attrs, errors = await self._validate_values(**schema_dict)

        if errors:
            return None, errors

        created_object = await self._repository.create(**attrs)
        schema_object = self.wrap_object(created_object)
        return schema_object, {}

    @action
    @atomic
    async def bulk_create(
        self,
        listCreateSchema: List[CreateSchema],
    ):
        async with self._repository() as repo:
            return [
                self.create(createSchema=createSchema)
                for createSchema in listCreateSchema
            ]

    @action
    async def update(
        self,
        id: Union[int, str],
        updateSchema: UpdateSchema,
        exclude_unset: bool = True,
    ) -> Tuple[models.Model, Dict]:
        schema_dict = updateSchema.dict(exclude_unset=exclude_unset)
        attrs, errors = await self._validate_values(**schema_dict)

        if errors:
            return None, errors

        updated_instance = await self._repository.update_and_return(
            values=attrs,
            id=id,
        )
        return updated_instance, {}

    @action
    async def bulk_update(
        self,
        updateSchema: UpdateSchema,
        filters: Dict = {},
        exclude_unset: bool = True,
    ) -> Tuple[models.Model, Dict]:
        """Update multiple objects fitting assigned filters."""
        schema_dict = updateSchema.dict(exclude_unset=exclude_unset)
        errors = await self._validate_values(**schema_dict)

        if errors:
            return None, errors
        async with self._repository() as repo:
            return await repo.bulk_update(filters=filters, **schema_dict), {}


class RetrieveFetchServiceMixin(IServiceBase):
    async def fetch(
        self,
        _ordering: List = [],
        **filters,
    ):
        async with self._repository() as repo:
            return await repo.fetch(ordering=_ordering, **filters), None

    @action
    async def retrieve(self, **filters):
        return await self._repository.retrieve(**filters), {}

    @action
    async def exists(self, **filters):
        return await self.model.filter(**filters).exists()


class DeleteMixin(IServiceBase):
    async def _validate_delete(self, attrs: Dict):
        return attrs, {}

    async def _validate_bulk_delete(self, **kwargs):
        qs = await self.get_queryset(management=True)
        return await qs.filter(**kwargs).exists()

    @action
    async def delete(self, deleteSchema: DeleteSchema, exclude_unset: bool = True):
        delete_schema_dict = deleteSchema.dict(exclude_unset=exclude_unset)
        self._action_attributes[self.action] = delete_schema_dict
        attrs, errors = await self._validate_delete(self.current_action_attributes)

        if errors:
            return None, errors
        return await self.model.filter(**attrs).delete(), None

    @action
    async def delete_by_id(self, id: int):
        queryset = await self.get_queryset(management=True)

        if not len(await queryset):
            return False, {'id': 'Operation not allowed'}

        await queryset.filter(id=id).first().delete()
        return True, None

    @action
    async def bulk_delete(
        self,
        **kwargs,
    ) -> Tuple[models.Model, Dict]:
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
