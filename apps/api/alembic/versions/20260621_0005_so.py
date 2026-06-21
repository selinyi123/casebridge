"""add outcome table

Revision ID: 20260621_0005
Revises: 20260621_0004
"""

from alembic import op
import sqlalchemy as sa

revision = "20260621_0005"
down_revision = "20260621_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_outcomes",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("case_id", sa.String(length=40), nullable=False),
        sa.Column("goal_id", sa.String(length=40), nullable=True),
        sa.Column("assessment_id", sa.String(length=40), nullable=True),
        sa.Column("outcome_type", sa.String(length=80), nullable=False),
        sa.Column("gas_score", sa.Integer(), nullable=True),
        sa.Column("narrative", sa.Text(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("recorded_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("service_outcomes")
