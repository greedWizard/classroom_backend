from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
)

from apps.common.config import config
from apps.common.models import BaseMetaData


engine = create_async_engine(config.DB_CONNECTION_STRING, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
BaseModel = declarative_base(cls=BaseMetaData)
