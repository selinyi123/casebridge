"""add case assessments

Revision ID: 20260621_0004
Revises: 20260621_0003
Create Date: 2026-06-21
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260621_0004"
down_revision: str | None = "20260621_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_assessments",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("case_id", sa.String(length=40), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("source_note_id", sa.String(length=40), sa.ForeignKey("case_notes.id"), nullable=False),
        sa.Column("source_ai_output_id", sa.String(length=40), sa.ForeignKey("ai_outputs.id"), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("prompt_version", sa.String(length=80), nullable=False),
        sa.Column("assessment_type", sa.String(length=80), nullable=False),
        sa.Column("assessment_data", sa.JSON(), nullable=False),
        sa.Column("reviewer_id", sa.String(length=120), nullable=False),
        sa.Column("reviewer_responsibility_accepted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_case_assessments_case_id", "case_assessments", ["case_id"])
    op.create_index("ix_case_assessments_source_note_id", "case_assessments", ["source_note_id"])
    op.create_index("ix_case_assessments_source_ai_output_id", "case_assessments", ["source_ai_output_id"])


def downgrade() -> None:
    op.drop_table("case_assessments")
