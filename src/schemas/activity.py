from __future__ import annotations

from uuid import UUID

from pydantic import Field

from src.schemas.base import ORMModel


class ActivityRead(ORMModel):
    id: UUID
    name: str = Field(max_length=120)
    level: int
    parent_id: UUID | None = None


class ActivityTree(ActivityRead):
    children: list["ActivityTree"] = Field(default_factory=list)

