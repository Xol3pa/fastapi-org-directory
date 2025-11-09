from __future__ import annotations

import uuid

import pytest

from src.models import Building, Organization
from src.services.organization import OrganizationService


def _organization(lat: float, lon: float, name: str) -> Organization:
    building = Building(
        id=uuid.uuid4(),
        address=f"{name} address",
        latitude=lat,
        longitude=lon,
    )
    organization = Organization(
        id=uuid.uuid4(),
        name=name,
        description=None,
        building_id=building.id,
    )
    organization.building = building
    organization.phone_numbers = []
    organization.activities = []
    return organization


class StubOrgRepository:
    def __init__(self, candidates: list[Organization]):
        self._candidates = candidates
        self.window_calls = 0

    async def list_in_lat_lon_window(self, **_: float) -> list[Organization]:
        self.window_calls += 1
        return self._candidates


class RejectingRepository:
    def __init__(self):
        self.called = False

    async def list_in_lat_lon_window(self, **_: float) -> list[Organization]:
        self.called = True
        raise AssertionError("Should not be called")


@pytest.mark.asyncio
async def test_list_within_radius_filters_with_haversine():
    inside = _organization(55.751, 37.618, "Inside")
    outside = _organization(55.80, 37.80, "Outside")
    repo = StubOrgRepository([inside, outside])

    service = OrganizationService(repo)

    results = await service.list_within_radius(latitude=55.751, longitude=37.618, radius_km=1.0)

    assert [org.name for org in results] == ["Inside"]
    assert repo.window_calls == 1


@pytest.mark.asyncio
async def test_list_within_radius_skips_query_for_non_positive_radius():
    repo = RejectingRepository()
    service = OrganizationService(repo)  # type: ignore[arg-type]

    results = await service.list_within_radius(latitude=0.0, longitude=0.0, radius_km=0.0)

    assert results == []
    assert repo.called is False

