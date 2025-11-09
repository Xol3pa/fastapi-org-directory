from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Building


class BuildingRepository:
    """Доступ к зданиям и адресам."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_all(self) -> list[Building]:
        result = await self._session.execute(select(Building))
        return list(result.scalars().all())

    async def get(self, building_id: UUID) -> Building | None:
        return await self._session.get(Building, building_id)

