from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Activity


class ActivityRepository:
    """Доступ к видам деятельности."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _tree_stmt(self) -> Select[tuple[Activity]]:
        return select(Activity).options(selectinload(Activity.children))

    async def get_with_children(self, activity_id: UUID) -> Activity | None:
        result = await self._session.execute(self._tree_stmt().where(Activity.id == activity_id))
        return result.scalar_one_or_none()

    async def list_roots(self) -> list[Activity]:
        result = await self._session.execute(
            self._tree_stmt().where(Activity.parent_id.is_(None))
        )
        return list(result.scalars().all())

