from __future__ import annotations

from typing import Iterable

from src.models import Building
from src.schemas import BuildingRead


def map_building(building: Building) -> BuildingRead:
    return BuildingRead(
        id=building.id,
        address=building.address,
        latitude=building.latitude,
        longitude=building.longitude,
    )


def map_buildings(buildings: Iterable[Building]) -> list[BuildingRead]:
    return [map_building(building) for building in buildings]

