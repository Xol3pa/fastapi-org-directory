from __future__ import annotations

from typing import Iterable

from src.models import Activity
from src.schemas import ActivityTree


def map_activity_tree(activity: Activity) -> ActivityTree:
    children = sorted(activity.children, key=lambda item: item.name)
    return ActivityTree(
        id=activity.id,
        name=activity.name,
        level=activity.level,
        parent_id=activity.parent_id,
        children=[map_activity_tree(child) for child in children],
    )


def map_activity_tree_list(activities: Iterable[Activity]) -> list[ActivityTree]:
    return [map_activity_tree(activity) for activity in sorted(activities, key=lambda item: item.name)]

