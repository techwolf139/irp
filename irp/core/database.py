from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

_engine = None
_async_session = None


def _get_engine():
    global _engine
    if _engine is None:
        from irp.config import settings
        _engine = create_async_engine(settings.database_url, echo=False)
    return _engine


def _get_async_session():
    global _async_session
    if _async_session is None:
        _async_session = async_sessionmaker(_get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _async_session


async def get_db():
    async with _get_async_session() as session:
        yield session
