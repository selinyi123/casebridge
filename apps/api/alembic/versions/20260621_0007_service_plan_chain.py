"""add service plan evidence chain

Revision ID: 20260621_0007
Revises: 20260621_0006
"""

from alembic import op
import sqlalchemy as sa

revision = "20260621_0007"
down_revision = "20260621_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_plans",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.String(length=40), nullable=False),
        sa.Column("assessment_id", sa.String(length=40), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("plan_status", sa.String(length=40), nullable=False),
        sa.Column("plan_data", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "service_interventions",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.String(length=40), nullable=False),
        sa.Column("plan_id", sa.String(length=40), nullable=False),
        sa.Column("goal_id", sa.String(length=40), nullable=True),
        sa.Column("intervention_type", sa.String(length=80), nullable=False),
        sa.Column("narrative", sa.Text(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("recorded_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("service_interventions")
    op.drop_table("service_plans")
