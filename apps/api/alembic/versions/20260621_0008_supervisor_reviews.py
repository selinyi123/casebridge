"""add supervisor reviews

Revision ID: 20260621_0008
Revises: 20260621_0007
"""

from alembic import op
import sqlalchemy as sa

revision = "20260621_0008"
down_revision = "20260621_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "supervisor_reviews",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.String(length=40), nullable=False),
        sa.Column("review_type", sa.String(length=80), nullable=False),
        sa.Column("decision", sa.String(length=80), nullable=False),
        sa.Column("blockers", sa.JSON(), nullable=False),
        sa.Column("evidence_summary", sa.JSON(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("reviewed_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("supervisor_reviews")
