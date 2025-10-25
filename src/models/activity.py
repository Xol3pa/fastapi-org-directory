from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.organization import Organization


class Activity(Base):
    """Вид деятельности в иерархическом справочнике (до 3 уровней)."""

    __tablename__ = "activities"

    __table_args__ = (
        CheckConstraint("level BETWEEN 1 AND 3", name="ck_activities_level"),
        UniqueConstraint("parent_id", "name", name="uq_activities_parent_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="SET NULL"),
        nullable=True,
    )

    parent: Mapped["Activity | None"] = relationship(
        back_populates="children",
        remote_side="Activity.id",
    )
    children: Mapped[list["Activity"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    organizations: Mapped[list["Organization"]] = relationship(
        secondary="organization_activities",
        back_populates="activities",
    )

