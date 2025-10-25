from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import verify_api_key
from src.db.session import get_session
from src.schemas import OrganizationDetail
from src.services import activity as activity_service
from src.services import organization as organization_service

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
    dependencies=[Depends(verify_api_key)],
)


def _serialize(org) -> OrganizationDetail:
    return OrganizationDetail.model_validate(org)


@router.get("/", response_model=list[OrganizationDetail])
async def list_organizations(
    name: str | None = Query(default=None, min_length=1, description="Часть названия."),
    activity_id: UUID | None = Query(default=None, description="ID вида деятельности (с потомками)."),
    session: AsyncSession = Depends(get_session),
) -> list[OrganizationDetail]:
    organizations: list = []

    if activity_id:
        activity_ids = await activity_service.collect_descendant_ids(session, activity_id)
        if not activity_ids:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Деятельность не найдена.")
        organizations = await organization_service.list_by_activity_ids(session, activity_ids)

    if name:
        name_matches = await organization_service.search_by_name(session, name)
        if not organizations:
            organizations = name_matches
        else:
            present_ids = {org.id for org in organizations}
            organizations = [org for org in name_matches if org.id in present_ids]

    if not organizations and name is None and activity_id is None:
        organizations = await organization_service.list_all(session)

    return [_serialize(org) for org in organizations]


@router.get("/geo/search", response_model=list[OrganizationDetail])
async def search_by_geo(
    latitude: float | None = Query(default=None, description="Широта центра радиуса."),
    longitude: float | None = Query(default=None, description="Долгота центра радиуса."),
    radius_km: float | None = Query(default=None, gt=0, description="Радиус (км)."),
    min_latitude: float | None = Query(default=None, description="Минимальная широта прямоугольника."),
    max_latitude: float | None = Query(default=None, description="Максимальная широта."),
    min_longitude: float | None = Query(default=None, description="Минимальная долгота."),
    max_longitude: float | None = Query(default=None, description="Максимальная долгота."),
    session: AsyncSession = Depends(get_session),
) -> list[OrganizationDetail]:
    use_radius = latitude is not None and longitude is not None and radius_km is not None
    use_bbox = all(
        value is not None
        for value in (min_latitude, max_latitude, min_longitude, max_longitude)
    )

    if not use_radius and not use_bbox:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нужно указать параметры радиуса или прямоугольника.",
        )

    radius_results = None
    if use_radius:
        radius_results = await organization_service.list_within_radius(
            session=session,
            latitude=latitude,  # type: ignore[arg-type]
            longitude=longitude,  # type: ignore[arg-type]
            radius_km=radius_km,  # type: ignore[arg-type]
        )

    bbox_results = None
    if use_bbox:
        bbox_results = await organization_service.list_in_bbox(
            session=session,
            min_latitude=min_latitude,  # type: ignore[arg-type]
            max_latitude=max_latitude,  # type: ignore[arg-type]
            min_longitude=min_longitude,  # type: ignore[arg-type]
            max_longitude=max_longitude,  # type: ignore[arg-type]
        )

    if use_radius and use_bbox:
        assert radius_results is not None and bbox_results is not None
        bbox_ids = {org.id for org in bbox_results}
        results = [org for org in radius_results if org.id in bbox_ids]
    elif use_radius:
        assert radius_results is not None
        results = radius_results
    elif use_bbox:
        assert bbox_results is not None
        results = bbox_results
    else:
        results = await organization_service.list_all(session)

    unique = {org.id: org for org in results}
    return [_serialize(org) for org in unique.values()]


@router.get("/{organization_id}", response_model=OrganizationDetail)
async def retrieve(
    organization_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> OrganizationDetail:
    organization = await organization_service.get_by_id(session, organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Организация не найдена.")
    return _serialize(organization)
