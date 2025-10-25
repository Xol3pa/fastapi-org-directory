from __future__ import annotations

from uuid import UUID

from pydantic import Field

from src.schemas.base import ORMModel


class BuildingRead(ORMModel):
    id: UUID
    address: str = Field(max_length=255)
    latitude: float
    longitude: float

