from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import verify_api_key
from src.db.session import get_session
from src.schemas import ActivityTree, OrganizationDetail
from src.services import activity as activity_service
from src.services import organization as organization_service

router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
    dependencies=[Depends(verify_api_key)],
)


def _serialize_activity(activity) -> ActivityTree:
    return ActivityTree(
        id=activity.id,
        name=activity.name,
        level=activity.level,
        parent_id=activity.parent_id,
        children=[
            _serialize_activity(child) for child in sorted(activity.children, key=lambda item: item.name)
        ],
    )


@router.get("/", response_model=list[ActivityTree])
async def tree(
    session: AsyncSession = Depends(get_session),
) -> list[ActivityTree]:
    activities = await activity_service.fetch_activity_tree(session)
    return [_serialize_activity(activity) for activity in sorted(activities, key=lambda item: item.name)]


@router.get("/{activity_id}", response_model=ActivityTree)
async def branch(
    activity_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ActivityTree:
    activity = await activity_service.get_activity(session, activity_id)
    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Деятельность не найдена.")
    return _serialize_activity(activity)


@router.get("/{activity_id}/organizations", response_model=list[OrganizationDetail])
async def organizations_for_activity(
    activity_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> list[OrganizationDetail]:
    activity_ids = await activity_service.collect_descendant_ids(session, activity_id)
    if not activity_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Деятельность не найдена.")

    organizations = await organization_service.list_by_activity_ids(session, activity_ids)
    return [OrganizationDetail.model_validate(org) for org in organizations]
