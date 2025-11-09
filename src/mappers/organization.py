from __future__ import annotations

from typing import Iterable

from src.mappers.building import map_building
from src.models import Activity, Organization, OrganizationPhone
from src.schemas import ActivityRead, OrganizationDetail, OrganizationPhoneRead


def _map_activity(activity: Activity) -> ActivityRead:
    return ActivityRead(
        id=activity.id,
        name=activity.name,
        level=activity.level,
        parent_id=activity.parent_id,
    )


def _map_phone(phone: OrganizationPhone) -> OrganizationPhoneRead:
    return OrganizationPhoneRead(
        id=phone.id,
        phone_number=phone.phone_number,
    )


def map_organization_detail(organization: Organization) -> OrganizationDetail:
    building = organization.building
    if building is None:
        raise ValueError("Organization building relation is not loaded.")

    return OrganizationDetail(
        id=organization.id,
        name=organization.name,
        description=organization.description,
        building_id=organization.building_id,
        building=map_building(building),
        phone_numbers=[_map_phone(phone) for phone in sorted(organization.phone_numbers, key=lambda item: item.phone_number)],
        activities=[_map_activity(activity) for activity in sorted(organization.activities, key=lambda item: item.name)],
    )


def map_organization_details(organizations: Iterable[Organization]) -> list[OrganizationDetail]:
    return [map_organization_detail(org) for org in organizations]

