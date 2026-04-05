from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

_engine = None
_async_session_factory = None


def _get_engine():
    global _engine
    if _engine is None:
        from irp.config import settings
        _engine = create_async_engine(settings.database_url, echo=False)
    return _engine


def _get_async_session_factory():
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            _get_engine(), class_=AsyncSession, expire_on_commit=False, autocommit=False
        )
    return _async_session_factory


@asynccontextmanager
async def get_db():
    """异步数据库会话上下文管理器。
    
    用法：
        async with get_db() as session:
            # 使用 session
    """
    async_session_factory = _get_async_session_factory()
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
