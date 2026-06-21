"""add assessment versions

Revision ID: 20260621_0006
Revises: 20260621_0005
"""

from alembic import op
import sqlalchemy as sa

revision = "20260621_0006"
down_revision = "20260621_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "case_assessment_versions",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.String(length=40), nullable=False),
        sa.Column("assessment_id", sa.String(length=40), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("version_data", sa.JSON(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_case_assessment_versions_org", "case_assessment_versions", ["organization_id"])
    op.create_index("ix_case_assessment_versions_case", "case_assessment_versions", ["case_id"])
    op.create_index("ix_case_assessment_versions_assessment", "case_assessment_versions", ["assessment_id"])


def downgrade() -> None:
    op.drop_table("case_assessment_versions")
