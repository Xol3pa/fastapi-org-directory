from __future__ import annotations

import uuid

import pytest

from src.mappers import map_activity_tree_list, map_organization_detail
from src.models import Activity, Building, Organization, OrganizationPhone


def _activity(name: str, level: int = 1, *, parent: Activity | None = None) -> Activity:
    activity = Activity(
        id=uuid.uuid4(),
        name=name,
        level=level,
        parent_id=parent.id if parent else None,
    )
    if parent:
        parent.children.append(activity)
    return activity


def test_map_activity_tree_list_sorts_roots_and_children():
    parent_z = _activity("Zoo")
    child_b = _activity("Beta", level=2, parent=parent_z)
    child_a = _activity("Alpha", level=2, parent=parent_z)

    parent_a = _activity("AlphaRoot")

    result = map_activity_tree_list([parent_z, parent_a])
    assert [item.name for item in result] == ["AlphaRoot", "Zoo"]
    assert [child.name for child in result[1].children] == ["Alpha", "Beta"]


def test_map_organization_detail_maps_nested_entities_sorted():
    building = Building(
        id=uuid.uuid4(),
        address="Main st. 1",
        latitude=10.0,
        longitude=20.0,
    )

    org = Organization(
        id=uuid.uuid4(),
        name="Org",
        description="Desc",
        building_id=building.id,
    )
    org.building = building

    phone_2 = OrganizationPhone(id=uuid.uuid4(), phone_number="+2")
    phone_1 = OrganizationPhone(id=uuid.uuid4(), phone_number="+1")
    org.phone_numbers = [phone_2, phone_1]

    act_b = Activity(id=uuid.uuid4(), name="Beta", level=1, parent_id=None)
    act_a = Activity(id=uuid.uuid4(), name="Alpha", level=1, parent_id=None)
    org.activities = [act_b, act_a]

    dto = map_organization_detail(org)

    assert dto.id == org.id
    assert dto.building.address == "Main st. 1"
    assert [phone.phone_number for phone in dto.phone_numbers] == ["+1", "+2"]
    assert [activity.name for activity in dto.activities] == ["Alpha", "Beta"]


def test_map_organization_detail_requires_loaded_building():
    org = Organization(
        id=uuid.uuid4(),
        name="Org",
        description=None,
        building_id=uuid.uuid4(),
    )
    org.building = None

    with pytest.raises(ValueError):
        map_organization_detail(org)
