from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.organization import Organization


class Building(Base):
    """Здание, в котором располагаются организации."""

    __tablename__ = "buildings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    address: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    organizations: Mapped[list["Organization"]] = relationship(
        back_populates="building",
        cascade="all, delete-orphan",
    )

