from __future__ import annotations

import math
from typing import Iterable
from uuid import UUID

from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models import Activity, Building, Organization

EARTH_RADIUS_KM = 6371.0


def _base_stmt() -> Select[tuple[Organization]]:
    return (
        select(Organization)
        .options(
            selectinload(Organization.activities),
            selectinload(Organization.phone_numbers),
            joinedload(Organization.building),
        )
    )


async def get_by_id(session: AsyncSession, organization_id: UUID) -> Organization | None:
    result = await session.execute(
        _base_stmt().where(Organization.id == organization_id)
    )
    return result.scalar_one_or_none()


async def search_by_name(session: AsyncSession, name: str) -> list[Organization]:
    pattern = f"%{name.strip()}%"
    result = await session.execute(
        _base_stmt().where(Organization.name.ilike(pattern))
    )
    return list(result.scalars().all())


async def list_by_building(session: AsyncSession, building_id: UUID) -> list[Organization]:
    result = await session.execute(
        _base_stmt().where(Organization.building_id == building_id)
    )
    return list(result.scalars().all())


async def list_by_activity_ids(session: AsyncSession, activity_ids: Iterable[UUID]) -> list[Organization]:
    ids = list(activity_ids)
    if not ids:
        return []

    stmt = (
        _base_stmt()
        .join(Organization.activities)
        .where(Activity.id.in_(ids))
        .distinct()
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_KM * c


async def list_within_radius(
    session: AsyncSession,
    latitude: float,
    longitude: float,
    radius_km: float,
) -> list[Organization]:
    if radius_km <= 0:
        return []

    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * max(math.cos(math.radians(latitude)), 0.00001))

    stmt = _base_stmt().join(Organization.building).where(
        and_(
            Building.latitude.between(latitude - lat_delta, latitude + lat_delta),
            Building.longitude.between(longitude - lon_delta, longitude + lon_delta),
        )
    )

    result = await session.execute(stmt)
    candidates = list(result.scalars().all())

    return [
        organization
        for organization in candidates
        if _haversine(latitude, longitude, organization.building.latitude, organization.building.longitude)
        <= radius_km
    ]


async def list_in_bbox(
    session: AsyncSession,
    min_latitude: float,
    max_latitude: float,
    min_longitude: float,
    max_longitude: float,
) -> list[Organization]:
    stmt = (
        _base_stmt()
        .join(Organization.building)
        .where(
            and_(
                Building.latitude.between(min_latitude, max_latitude),
                Building.longitude.between(min_longitude, max_longitude),
            )
        )
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_all(session: AsyncSession) -> list[Organization]:
    result = await session.execute(_base_stmt())
    return list(result.scalars().all())

