from __future__ import annotations

import math
from typing import Iterable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Organization
from src.repositories.organization import OrganizationRepository

EARTH_RADIUS_KM = 6371.0


class OrganizationService:
    """Бизнес-операции над организациями."""

    def __init__(self, repository: OrganizationRepository):
        self._repository = repository

    async def get_by_id(self, organization_id: UUID) -> Organization | None:
        return await self._repository.get_by_id(organization_id)

    async def search_by_name(self, name: str) -> list[Organization]:
        pattern = f"%{name.strip()}%"
        return await self._repository.search_by_name_pattern(pattern)

    async def list_by_building(self, building_id: UUID) -> list[Organization]:
        return await self._repository.list_by_building(building_id)

    async def list_by_activity_ids(self, activity_ids: Iterable[UUID]) -> list[Organization]:
        return await self._repository.list_by_activity_ids(activity_ids)

    async def list_within_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
    ) -> list[Organization]:
        if radius_km <= 0:
            return []

        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * max(math.cos(math.radians(latitude)), 0.00001))

        candidates = await self._repository.list_in_lat_lon_window(
            latitude=latitude,
            longitude=longitude,
            lat_delta=lat_delta,
            lon_delta=lon_delta,
        )
        return [
            organization
            for organization in candidates
            if _haversine(latitude, longitude, organization.building.latitude, organization.building.longitude)
            <= radius_km
        ]

    async def list_in_bbox(
        self,
        min_latitude: float,
        max_latitude: float,
        min_longitude: float,
        max_longitude: float,
    ) -> list[Organization]:
        return await self._repository.list_in_bbox(min_latitude, max_latitude, min_longitude, max_longitude)

    async def list_all(self) -> list[Organization]:
        return await self._repository.list_all()


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_KM * c


def _service(session: AsyncSession) -> OrganizationService:
    return OrganizationService(OrganizationRepository(session))


async def get_by_id(session: AsyncSession, organization_id: UUID) -> Organization | None:
    service = _service(session)
    return await service.get_by_id(organization_id)


async def search_by_name(session: AsyncSession, name: str) -> list[Organization]:
    service = _service(session)
    return await service.search_by_name(name)


async def list_by_building(session: AsyncSession, building_id: UUID) -> list[Organization]:
    service = _service(session)
    return await service.list_by_building(building_id)


async def list_by_activity_ids(session: AsyncSession, activity_ids: Iterable[UUID]) -> list[Organization]:
    service = _service(session)
    return await service.list_by_activity_ids(activity_ids)


async def list_within_radius(
    session: AsyncSession,
    latitude: float,
    longitude: float,
    radius_km: float,
) -> list[Organization]:
    service = _service(session)
    return await service.list_within_radius(latitude=latitude, longitude=longitude, radius_km=radius_km)


async def list_in_bbox(
    session: AsyncSession,
    min_latitude: float,
    max_latitude: float,
    min_longitude: float,
    max_longitude: float,
) -> list[Organization]:
    service = _service(session)
    return await service.list_in_bbox(
        min_latitude=min_latitude,
        max_latitude=max_latitude,
        min_longitude=min_longitude,
        max_longitude=max_longitude,
    )


async def list_all(session: AsyncSession) -> list[Organization]:
    service = _service(session)
    return await service.list_all()

