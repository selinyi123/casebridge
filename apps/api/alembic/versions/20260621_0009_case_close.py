"""case close draft table

Revision ID: 20260621_0009
Revises: 20260621_0008
"""

from alembic import op
import sqlalchemy as sa

revision = "20260621_0009"
down_revision = "20260621_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "case_closure_drafts",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.String(length=40), nullable=False),
        sa.Column("draft_status", sa.String(length=40), nullable=False),
        sa.Column("closure_reason", sa.Text(), nullable=False),
        sa.Column("blocker_snapshot", sa.JSON(), nullable=False),
        sa.Column("evidence_summary", sa.JSON(), nullable=False),
        sa.Column("report_data", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column("approved_by", sa.String(length=120), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("case_closure_drafts")
