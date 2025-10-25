from __future__ import annotations

from uuid import UUID

from pydantic import Field

from src.schemas.activity import ActivityRead
from src.schemas.base import ORMModel
from src.schemas.building import BuildingRead


class OrganizationPhoneRead(ORMModel):
    id: UUID
    phone_number: str = Field(max_length=30)


class OrganizationShort(ORMModel):
    id: UUID
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    building_id: UUID


class OrganizationDetail(OrganizationShort):
    building: BuildingRead
    phone_numbers: list[OrganizationPhoneRead]
    activities: list[ActivityRead]

