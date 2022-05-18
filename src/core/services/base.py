from typing import Dict, List, NewType, Tuple, Type, Union
from warnings import filters
from attr import attrs
from pydantic import BaseModel

from tortoise import models
from tortoise.transactions import atomic

from core.services.decorators import action


CreateSchema = NewType('CreateSchemaType', BaseModel)
UpdateSchema = NewType('UpdateSchemaType', BaseModel)
DeleteSchema = NewType('DeleteSchemaType', BaseModel)
ResultTuple = NewType('ResultTuple', Tuple[bool, Union[Dict, None]])


class SchemaMapMixin:
    schema_map: Dict = {}
    schema_class: Type[BaseModel] = None

    async def get_schema_class(self) -> Type[BaseModel]:
        return self.schema_map.get(self.action, self.schema_class)

    async def get_schema(self, **kwargs) -> BaseModel:
        '''
            Returns pydantic schema of the action if it is in `schema_map` keys.
            Else returns async default `schema_class` instance.
        '''
        return await self.get_schema_class()(**kwargs)


class IServiceBase(SchemaMapMixin):
    model: Type[models.Model] = None
    _action_attributes: Dict = {}

    @property
    def current_action_attributes(self):
        return self._action_attributes.get(self.action, {})

    async def get_queryset(self, management: bool = False):
        return self.model.all()

    error_messages = {
        'does_not_exist': 'Not found.',
        'no_values_found': 'No values were found {values}.',
        'already_exists': 'Already exists.'
    }
    required_fields_map = {}
    _errors: Dict = {}

    @action
    async def create(self, createSchema: CreateSchema, exclude_unset: bool = False) -> Tuple[models.Model, Dict]:
        raise NotImplementedError()

    @action
    async def create(self, createSchema: CreateSchema, exclude_unset: bool = False) -> Tuple[models.Model, Dict]:
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
        raise NotImplemented()

    @action
    async def retrieve(self, **kwargs):
        raise NotImplemented()


class CreateUpdateServiceMixin(IServiceBase):
    required_fields_map: Dict[str, List] = {}

    async def validate(self, attrs: Dict = {}) -> Dict:
        ''' Method for prevalidating attrs before action '''
        return attrs

    async def _validate_values(self, **kwargs) -> None:
        '''
            Validates values before creating or updating `model` field instances.
        '''
        errors = {}
        self._action_attributes[self.action] = kwargs

        for required_field in self.required_fields_map.get(self.action, []):
            if required_field not in kwargs:
                errors[required_field] = 'This field is required.'

        for key, value in kwargs.items():
            validation_method = f'validate_{key}'

            if hasattr(self, validation_method):
                validation_success, validation_error = await getattr(self, validation_method)(value)

                if not validation_success:
                    errors[key] = validation_error

        attrs = await self.validate(kwargs) or kwargs
        return attrs, errors

    @action
    async def create(
        self,
        createSchema: CreateSchema,
        exclude_unset: bool = False,
        fetch_related: List[str] = [],
    ) -> Tuple[models.Model, Dict]:
        schema_dict = createSchema.dict(exclude_unset=exclude_unset)
        attrs, errors = await self._validate_values(**schema_dict)

        if errors:
            return None, errors
        obj = await self.model.create(**attrs)
        await obj.fetch_related(*fetch_related)
        return obj, {}

    @action
    @atomic
    async def bulk_create(
        self,
        listCreateSchema: List[CreateSchema],
    ):
        obj_list = []

        for createSchema in listCreateSchema:
            obj_list.append(
                await self.create(createSchema)
            )
        return obj_list

    @action
    async def update(
        self,
        id: int,
        updateSchema: UpdateSchema,
        exclude_unset: bool = True,
        fetch_related: List = [],
    ) -> Tuple[models.Model, Dict]:
        schema_dict = updateSchema.dict(exclude_unset=exclude_unset)
        attrs, errors = await self._validate_values(**schema_dict)

        if errors:
            return None, errors

        queryset = await self.get_queryset(management=True)
        queryset = queryset.filter(id=id).first()
        obj = await queryset

        if not obj:
            return None, self.error_messages.get('does_not_exist')

        for key, value in attrs.items():
            setattr(obj, key, value)
            await obj.save()

        await obj.fetch_related(*fetch_related)
        return obj, {}

    @action
    async def bulk_update(
        self,
        updateSchema: UpdateSchema,
        filters: Dict = {},
        exclude_unset: bool = True,
    ) -> Tuple[models.Model, Dict]:
        ''' Update multiple objects fitting assigned filters '''
        schema_dict = updateSchema.dict(exclude_unset=exclude_unset)
        errors = await self._validate_values(**schema_dict)

        queryset = await self.model.filter(**filters)

        if not await queryset.exists():
            return None, { 'error': self.error_messages.get('does_not_exist') }

        await queryset.update(schema_dict)

        if errors:
            return None, errors
        return queryset, {}


class RetrieveFetchServiceMixin(IServiceBase):
    # TODO: рефакторить, фильтры не должны передавать в дикте
    @action
    async def fetch(
        self,
        _filters: Dict = {},
        _ordering: List = [],
        _prefetch_related: List = [],
        _select_related: List = [],
        distinct: bool = True,
    ):
        qs = await self.get_queryset()
        queryset = qs.filter(**_filters).order_by(*_ordering)\
            .select_related(*_select_related)\
            .prefetch_related(*_prefetch_related)

        if distinct:
            queryset = queryset.distinct()
        return await queryset, None
    
    @action
    async def retrieve(
        self,
        _fetch_related: list = [],
        **kwargs,
    ):
        # TODO: чекнуть сколько запросов идёт в базу, скорее всего тут лишние запросы идут
        qs = await self.get_queryset()
        obj = await qs.filter(**kwargs).prefetch_related(*_fetch_related).first()

        if not obj:
            return None, self.error_messages.get('does_not_exist')
        return obj, {}


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

        if not queryset:
            return False, { 'id': 'Operation not allowed' }

        await queryset.filter(id=id).first().delete()
        return True, None

    @action
    async def bulk_delete(
        self,
        **kwargs,
    ) -> Tuple[models.Model, Dict]:
        if not await self._validate_bulk_delete(**kwargs):
            return { 'permission_error': 'You are not allowed to do that!' }
        qs = await self.get_queryset(management=True)
        await qs.filter(**kwargs).delete()
        return None


class CRUDService(CreateUpdateServiceMixin, RetrieveFetchServiceMixin, DeleteMixin):
    '''
        CrudService for performing CRUD operations and validation.
        ! All manager's operations only avaliable from that class and it's subclasses methods!
    '''
    def __init__(self) -> None:
        self.user = None
