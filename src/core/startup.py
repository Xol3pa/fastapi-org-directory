from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from src.api import main_router
from src.config import settings
from src.db.session import AsyncSessionFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionFactory() as session:
        await session.execute(text("SELECT 1"))
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )
    app.include_router(main_router, prefix=settings.api_prefix + settings.api_v1_prefix)
    return app
