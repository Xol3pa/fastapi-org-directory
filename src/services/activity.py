from __future__ import annotations

from collections import deque
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Activity
from src.repositories.activity import ActivityRepository


class ActivityService:
    """Бизнес-операции над иерархией видов деятельности."""

    def __init__(self, repository: ActivityRepository):
        self._repository = repository

    async def get_activity(self, activity_id: UUID) -> Activity | None:
        return await self._repository.get_with_children(activity_id)

    async def collect_descendant_ids(self, activity_id: UUID) -> list[UUID]:
        """Возвращает ID активности и всех её потомков."""
        root = await self.get_activity(activity_id)
        if root is None:
            return []

        ids: list[UUID] = []
        queue: deque[Activity] = deque([root])

        while queue:
            item = queue.popleft()
            ids.append(item.id)
            queue.extend(item.children)

        return ids

    async def fetch_activity_tree(self) -> list[Activity]:
        return await self._repository.list_roots()


def _service(session: AsyncSession) -> ActivityService:
    return ActivityService(ActivityRepository(session))


async def get_activity(session: AsyncSession, activity_id: UUID) -> Activity | None:
    service = _service(session)
    return await service.get_activity(activity_id)


async def collect_descendant_ids(session: AsyncSession, activity_id: UUID) -> list[UUID]:
    service = _service(session)
    return await service.collect_descendant_ids(activity_id)


async def fetch_activity_tree(session: AsyncSession) -> list[Activity]:
    service = _service(session)
    return await service.fetch_activity_tree()

