from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Building
from src.repositories.building import BuildingRepository


class BuildingService:
    """Логика выборки зданий и их организаций."""

    def __init__(self, repository: BuildingRepository):
        self._repository = repository

    async def list_buildings(self) -> list[Building]:
        return await self._repository.list_all()

    async def get_building(self, building_id: UUID) -> Building | None:
        return await self._repository.get(building_id)


def _service(session: AsyncSession) -> BuildingService:
    return BuildingService(BuildingRepository(session))


async def list_buildings(session: AsyncSession) -> list[Building]:
    service = _service(session)
    return await service.list_buildings()


async def get_building(session: AsyncSession, building_id: UUID) -> Building | None:
    service = _service(session)
    return await service.get_building(building_id)

