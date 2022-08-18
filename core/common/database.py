from core.common.config import config

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker


engine = create_async_engine(config.DB_CONNECTION_STRING, future=True, echo=True)
test_engine = create_async_engine(
    config.DB_TEST_CONNECTION_STRING,
    future=True,
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
test_session = sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
