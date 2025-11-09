from __future__ import annotations

from typing import Iterable
from uuid import UUID

from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models import Activity, Building, Organization


class OrganizationRepository:
    """Работа с организациями и связанными сущностями."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _base_stmt(self) -> Select[tuple[Organization]]:
        return (
            select(Organization)
            .options(
                selectinload(Organization.activities),
                selectinload(Organization.phone_numbers),
                joinedload(Organization.building),
            )
        )

    async def get_by_id(self, organization_id: UUID) -> Organization | None:
        result = await self._session.execute(
            self._base_stmt().where(Organization.id == organization_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Organization]:
        result = await self._session.execute(self._base_stmt())
        return list(result.scalars().all())

    async def list_by_building(self, building_id: UUID) -> list[Organization]:
        result = await self._session.execute(
            self._base_stmt().where(Organization.building_id == building_id)
        )
        return list(result.scalars().all())

    async def list_by_activity_ids(self, activity_ids: Iterable[UUID]) -> list[Organization]:
        ids = list(activity_ids)
        if not ids:
            return []

        stmt = (
            self._base_stmt()
            .join(Organization.activities)
            .where(Activity.id.in_(ids))
            .distinct()
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name_pattern(self, pattern: str) -> list[Organization]:
        result = await self._session.execute(
            self._base_stmt().where(Organization.name.ilike(pattern))
        )
        return list(result.scalars().all())

    async def list_in_bbox(
        self,
        min_latitude: float,
        max_latitude: float,
        min_longitude: float,
        max_longitude: float,
    ) -> list[Organization]:
        stmt = (
            self._base_stmt()
            .join(Organization.building)
            .where(
                and_(
                    Building.latitude.between(min_latitude, max_latitude),
                    Building.longitude.between(min_longitude, max_longitude),
                )
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_in_lat_lon_window(
        self,
        latitude: float,
        longitude: float,
        lat_delta: float,
        lon_delta: float,
    ) -> list[Organization]:
        stmt = (
            self._base_stmt()
            .join(Organization.building)
            .where(
                and_(
                    Building.latitude.between(latitude - lat_delta, latitude + lat_delta),
                    Building.longitude.between(longitude - lon_delta, longitude + lon_delta),
                )
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
