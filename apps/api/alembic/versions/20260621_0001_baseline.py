"""baseline case loop schema

Revision ID: 20260621_0001
Revises:
Create Date: 2026-06-21
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260621_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("gender", sa.String(length=32), nullable=True),
        sa.Column("community", sa.String(length=120), nullable=False),
        sa.Column("client_type", sa.String(length=64), nullable=False),
        sa.Column("primary_concern", sa.Text(), nullable=False),
        sa.Column("existing_support", sa.Text(), nullable=True),
        sa.Column("consent_status", sa.String(length=32), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_clients_code", "clients", ["code"])
    op.create_index("ix_clients_community", "clients", ["community"])
    op.create_index("ix_clients_client_type", "clients", ["client_type"])

    op.create_table(
        "resources",
        sa.Column("code", sa.String(length=40), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("match_codes", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provider_type", sa.String(length=80), nullable=True),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("service_scope", sa.Text(), nullable=True),
    )
    op.create_index("ix_resources_category", "resources", ["category"])
    op.create_index("ix_resources_status", "resources", ["status"])

    op.create_table(
        "cases",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("client_code", sa.String(length=32), sa.ForeignKey("clients.code"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("primary_worker", sa.String(length=120), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_cases_client_code", "cases", ["client_code"])

    op.create_table(
        "case_notes",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("case_id", sa.String(length=40), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("note_type", sa.String(length=50), nullable=False),
        sa.Column("content_raw", sa.Text(), nullable=False),
        sa.Column("content_clean", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("pii_detected", sa.Boolean(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_case_notes_case_id", "case_notes", ["case_id"])

    op.create_table(
        "referrals",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("case_id", sa.String(length=40), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("resource_code", sa.String(length=40), sa.ForeignKey("resources.code"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("agreement_status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_referrals_case_id", "referrals", ["case_id"])
    op.create_index("ix_referrals_resource_code", "referrals", ["resource_code"])

    op.create_table(
        "service_goals",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("case_id", sa.String(length=40), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("target_state", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_service_goals_case_id", "service_goals", ["case_id"])


def downgrade() -> None:
    op.drop_table("service_goals")
    op.drop_table("referrals")
    op.drop_table("case_notes")
    op.drop_table("cases")
    op.drop_table("resources")
    op.drop_table("clients")
