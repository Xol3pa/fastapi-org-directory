"""Initial schema and seed data.

Revision ID: 20240411_0001
Revises:
Create Date: 2024-04-11
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20240411_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "buildings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("address", sa.String(length=255), nullable=False, unique=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
    )

    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("activities.id", ondelete="SET NULL")),
        sa.CheckConstraint("level >= 1 AND level <= 3", name="ck_activities_level"),
        sa.UniqueConstraint("parent_id", "name", name="uq_activities_parent_name"),
    )

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("description", sa.String(length=1024)),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False),
    )

    op.create_table(
        "organization_phones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("phone_number", sa.String(length=30), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
    )

    op.create_table(
        "organization_activities",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
    )

    seed_data()


def seed_data() -> None:
    building_ids = {
        "lenina": uuid.UUID("4f780fb7-2a1e-4020-9e50-2f4286f2fa14"),
        "bluchera": uuid.UUID("ad5d9e32-6204-4b75-b9d6-484f4025150e"),
        "nevsky": uuid.UUID("a0f76d43-57ce-48ca-af6c-8f3a1bf6c0d9"),
    }

    op.bulk_insert(
        sa.table(
            "buildings",
            sa.Column("id", postgresql.UUID(as_uuid=True)),
            sa.Column("address", sa.String(length=255)),
            sa.Column("latitude", sa.Float()),
            sa.Column("longitude", sa.Float()),
        ),
        [
            {
                "id": building_ids["lenina"],
                "address": "г. Москва, ул. Ленина 1, офис 3",
                "latitude": 55.75222,
                "longitude": 37.61556,
            },
            {
                "id": building_ids["bluchera"],
                "address": "г. Новосибирск, ул. Блюхера 32/1",
                "latitude": 55.0415,
                "longitude": 82.9346,
            },
            {
                "id": building_ids["nevsky"],
                "address": "г. Санкт-Петербург, Невский проспект 100",
                "latitude": 59.9311,
                "longitude": 30.3609,
            },
        ],
    )

    activity_ids = {
        "food": uuid.UUID("a8b96c4e-7f2d-4fe8-9a27-3a0f7d69b4a1"),
        "meat": uuid.UUID("1bb4d88a-0d67-4db7-9d79-7fb5df4ab4d8"),
        "dairy": uuid.UUID("64f1d91b-2316-4ab3-9f3a-0c3df9ba7840"),
        "automotive": uuid.UUID("af657256-9f37-4f33-b9bc-e66b4a79a0e1"),
        "trucks": uuid.UUID("b723d0f3-210c-4a7a-a6b4-97521116db0d"),
        "cars": uuid.UUID("eb22f236-3774-4d38-b1cc-354e0c64b89c"),
        "spare_parts": uuid.UUID("d67026b0-0485-4d8d-86ce-70415efe7da4"),
        "accessories": uuid.UUID("f3a03295-1ab7-4ac4-9089-00baa8223790"),
        "services": uuid.UUID("b4c5c2c1-6c8a-4011-8d7f-8a4e70f35456"),
        "consulting": uuid.UUID("8a6f7f26-4d84-4278-ab3c-96b8fba3f127"),
        "it_support": uuid.UUID("c4a19a53-1c9b-49c5-9f26-ccc2c6217cf4"),
    }

    activity_table = sa.table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True)),
        sa.Column("name", sa.String(length=120)),
        sa.Column("level", sa.Integer()),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True)),
    )

    op.bulk_insert(
        activity_table,
        [
            {"id": activity_ids["food"], "name": "Еда", "level": 1, "parent_id": None},
            {"id": activity_ids["meat"], "name": "Мясная продукция", "level": 2, "parent_id": activity_ids["food"]},
            {"id": activity_ids["dairy"], "name": "Молочная продукция", "level": 2, "parent_id": activity_ids["food"]},
            {"id": activity_ids["automotive"], "name": "Автомобили", "level": 1, "parent_id": None},
            {"id": activity_ids["trucks"], "name": "Грузовые", "level": 2, "parent_id": activity_ids["automotive"]},
            {"id": activity_ids["cars"], "name": "Легковые", "level": 2, "parent_id": activity_ids["automotive"]},
            {"id": activity_ids["spare_parts"], "name": "Запчасти", "level": 3, "parent_id": activity_ids["cars"]},
            {"id": activity_ids["accessories"], "name": "Аксессуары", "level": 3, "parent_id": activity_ids["cars"]},
            {"id": activity_ids["services"], "name": "Сервисы", "level": 1, "parent_id": None},
            {"id": activity_ids["consulting"], "name": "Консалтинг", "level": 2, "parent_id": activity_ids["services"]},
            {"id": activity_ids["it_support"], "name": "IT поддержка", "level": 2, "parent_id": activity_ids["services"]},
        ],
    )

    organization_ids = {
        "roga": uuid.UUID("8e3c7b0e-2e0f-4ef0-8e59-bf1f89e012e1"),
        "avtotrans": uuid.UUID("7b0f9c8c-f2ef-4b5d-95c6-a6cfa9953660"),
        "avtomarket": uuid.UUID("c2af7638-4a19-4c75-87f3-0ad7ec9c61b4"),
        "consultplus": uuid.UUID("3cf6af6c-5642-48ce-9865-e7c61ea6c2fd"),
    }

    organization_table = sa.table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True)),
        sa.Column("name", sa.String(length=255)),
        sa.Column("description", sa.String(length=1024)),
        sa.Column("building_id", postgresql.UUID(as_uuid=True)),
    )

    op.bulk_insert(
        organization_table,
        [
            {
                "id": organization_ids["roga"],
                "name": "ООО «Рога и Копыта»",
                "description": "Продажа фермерской мясной и молочной продукции.",
                "building_id": building_ids["bluchera"],
            },
            {
                "id": organization_ids["avtotrans"],
                "name": "ООО «АвтоТранс»",
                "description": "Поставки грузовых автомобилей и обслуживание парка.",
                "building_id": building_ids["nevsky"],
            },
            {
                "id": organization_ids["avtomarket"],
                "name": "ООО «АвтоМаркет»",
                "description": "Магазин автозапчастей и аксессуаров.",
                "building_id": building_ids["lenina"],
            },
            {
                "id": organization_ids["consultplus"],
                "name": "ООО «Консалт Плюс»",
                "description": "Бизнес-консалтинг и IT поддержка.",
                "building_id": building_ids["lenina"],
            },
        ],
    )

    phone_table = sa.table(
        "organization_phones",
        sa.Column("id", postgresql.UUID(as_uuid=True)),
        sa.Column("phone_number", sa.String(length=30)),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True)),
    )

    op.bulk_insert(
        phone_table,
        [
            {
                "id": uuid.UUID("fbc572fd-6827-4daa-9617-0cc63eb92234"),
                "phone_number": "2-222-222",
                "organization_id": organization_ids["roga"],
            },
            {
                "id": uuid.UUID("c9a923a8-391e-4910-87ad-97fcb91205e7"),
                "phone_number": "8-923-666-13-13",
                "organization_id": organization_ids["roga"],
            },
            {
                "id": uuid.UUID("bf29a5aa-286f-4ec1-bd74-6369db52d55b"),
                "phone_number": "3-333-333",
                "organization_id": organization_ids["roga"],
            },
            {
                "id": uuid.UUID("604acb74-6bdb-49d0-b241-fd5edd64d41e"),
                "phone_number": "+7 (812) 123-45-67",
                "organization_id": organization_ids["avtotrans"],
            },
            {
                "id": uuid.UUID("e0a6c1d4-0d1a-4a68-8cb1-5242559d5292"),
                "phone_number": "+7 (495) 555-00-11",
                "organization_id": organization_ids["avtomarket"],
            },
            {
                "id": uuid.UUID("1f80d64a-79dd-4f39-bb36-b57fae3318c2"),
                "phone_number": "+7 (495) 555-00-22",
                "organization_id": organization_ids["avtomarket"],
            },
            {
                "id": uuid.UUID("64517d01-1cce-4eed-a884-d7f62a4c2e40"),
                "phone_number": "+7 (495) 700-80-90",
                "organization_id": organization_ids["consultplus"],
            },
        ],
    )

    association_table = sa.table(
        "organization_activities",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True)),
        sa.Column("activity_id", postgresql.UUID(as_uuid=True)),
    )

    op.bulk_insert(
        association_table,
        [
            {"organization_id": organization_ids["roga"], "activity_id": activity_ids["food"]},
            {"organization_id": organization_ids["roga"], "activity_id": activity_ids["meat"]},
            {"organization_id": organization_ids["roga"], "activity_id": activity_ids["dairy"]},
            {"organization_id": organization_ids["avtotrans"], "activity_id": activity_ids["automotive"]},
            {"organization_id": organization_ids["avtotrans"], "activity_id": activity_ids["trucks"]},
            {"organization_id": organization_ids["avtomarket"], "activity_id": activity_ids["automotive"]},
            {"organization_id": organization_ids["avtomarket"], "activity_id": activity_ids["cars"]},
            {"organization_id": organization_ids["avtomarket"], "activity_id": activity_ids["spare_parts"]},
            {"organization_id": organization_ids["avtomarket"], "activity_id": activity_ids["accessories"]},
            {"organization_id": organization_ids["consultplus"], "activity_id": activity_ids["services"]},
            {"organization_id": organization_ids["consultplus"], "activity_id": activity_ids["consulting"]},
            {"organization_id": organization_ids["consultplus"], "activity_id": activity_ids["it_support"]},
        ],
    )


def downgrade() -> None:
    op.drop_table("organization_activities")
    op.drop_table("organization_phones")
    op.drop_table("organizations")
    op.drop_table("activities")
    op.drop_table("buildings")
