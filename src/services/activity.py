from __future__ import annotations

from collections import deque
from typing import Iterable
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Activity


def _tree_stmt() -> Select[tuple[Activity]]:
    return select(Activity).options(selectinload(Activity.children))


async def get_activity(session: AsyncSession, activity_id: UUID) -> Activity | None:
    result = await session.execute(_tree_stmt().where(Activity.id == activity_id))
    return result.scalar_one_or_none()


async def collect_descendant_ids(session: AsyncSession, activity_id: UUID) -> list[UUID]:
    """Возвращает ID активности и всех её потомков."""
    root = await get_activity(session, activity_id)
    if root is None:
        return []

    ids: list[UUID] = []
    queue: deque[Activity] = deque([root])

    while queue:
        item = queue.popleft()
        ids.append(item.id)
        queue.extend(item.children)

    return ids


async def fetch_activity_tree(session: AsyncSession) -> list[Activity]:
    result = await session.execute(
        _tree_stmt().where(Activity.parent_id.is_(None))
    )
    return list(result.scalars().all())

