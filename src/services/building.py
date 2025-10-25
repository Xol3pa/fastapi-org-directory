from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Building


async def list_buildings(session: AsyncSession) -> list[Building]:
    result = await session.execute(select(Building))
    return list(result.scalars().all())


async def get_building(session: AsyncSession, building_id: UUID) -> Building | None:
    return await session.get(Building, building_id)

