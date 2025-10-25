from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.activity import Activity
    from src.models.building import Building


organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column(
        "organization_id",
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Organization(Base):
    """Организация каталога."""

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    building_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False,
    )

    building: Mapped["Building"] = relationship(back_populates="organizations")
    phone_numbers: Mapped[list["OrganizationPhone"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["Activity"]] = relationship(
        secondary=organization_activities,
        back_populates="organizations",
    )


class OrganizationPhone(Base):
    """Телефонный номер организации."""

    __tablename__ = "organization_phones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    phone_number: Mapped[str] = mapped_column(String(30), nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    organization: Mapped[Organization] = relationship(back_populates="phone_numbers")

