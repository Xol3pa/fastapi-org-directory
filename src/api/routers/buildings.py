from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import verify_api_key
from src.db.session import get_session
from src.schemas import BuildingRead, OrganizationDetail
from src.services import building as building_service
from src.services import organization as organization_service

router = APIRouter(
    prefix="/buildings",
    tags=["Buildings"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/", response_model=list[BuildingRead])
async def list_buildings(
    session: AsyncSession = Depends(get_session),
) -> list[BuildingRead]:
    buildings = await building_service.list_buildings(session)
    return [BuildingRead.model_validate(item) for item in buildings]


@router.get("/{building_id}/organizations", response_model=list[OrganizationDetail])
async def organizations_by_building(
    building_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> list[OrganizationDetail]:
    building = await building_service.get_building(session, building_id)
    if building is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Здание не найдено.")

    organizations = await organization_service.list_by_building(session, building_id)
    return [OrganizationDetail.model_validate(org) for org in organizations]
