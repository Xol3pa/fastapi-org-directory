from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

engine: AsyncEngine = create_async_engine(
    settings.database.async_url,
    echo=settings.log_sql,
    future=True,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


@asynccontextmanager
async def lifespan_session() -> AsyncGenerator[AsyncSession, None]:
    """Контекст для фоновых задач, когда нужен живой сеанс на всём жизненном цикле."""
    async with AsyncSessionFactory() as session:
        yield session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость FastAPI для выдачи сессии."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

