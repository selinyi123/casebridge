"""add reopen requests

Revision ID: 20260621_0010
Revises: 20260621_0009
"""

from alembic import op
import sqlalchemy as sa

revision = "20260621_0010"
down_revision = "20260621_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "case_reopen_requests",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.String(length=40), nullable=False),
        sa.Column("request_status", sa.String(length=40), nullable=False),
        sa.Column("reopen_reason", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column("reviewed_by", sa.String(length=120), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("case_reopen_requests")
