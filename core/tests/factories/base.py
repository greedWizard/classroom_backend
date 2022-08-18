import asyncio
import inspect

import factory

from core.common.repositories.base import CreateUpdateRepository


class AsyncRepositoryFactory(factory.Factory):
    __repository__: type[CreateUpdateRepository] = None

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        async def maker_coroutine():
            for key, value in kwargs.items():
                if inspect.isawaitable(value):
                    kwargs[key] = await value
            return await cls.__repository__.create(*args, **kwargs)

        return asyncio.create_task(maker_coroutine())

    @classmethod
    async def create_batch(cls, size, **kwargs):
        return [await cls.create(**kwargs) for _ in range(size)]
