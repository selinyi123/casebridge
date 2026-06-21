"""add ai tasks and outputs

Revision ID: 20260621_0003
Revises: 20260621_0002
Create Date: 2026-06-21
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260621_0003"
down_revision: str | None = "20260621_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_tasks",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("case_id", sa.String(length=40), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("note_id", sa.String(length=40), sa.ForeignKey("case_notes.id"), nullable=False),
        sa.Column("capability", sa.String(length=80), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("prompt_version", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_tasks_case_id", "ai_tasks", ["case_id"])
    op.create_index("ix_ai_tasks_note_id", "ai_tasks", ["note_id"])
    op.create_index("ix_ai_tasks_capability", "ai_tasks", ["capability"])
    op.create_index("ix_ai_tasks_status", "ai_tasks", ["status"])

    op.create_table(
        "ai_outputs",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("task_id", sa.String(length=40), sa.ForeignKey("ai_tasks.id"), nullable=False),
        sa.Column("case_id", sa.String(length=40), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("note_id", sa.String(length=40), sa.ForeignKey("case_notes.id"), nullable=False),
        sa.Column("output_type", sa.String(length=80), nullable=False),
        sa.Column("raw_output", sa.JSON(), nullable=False),
        sa.Column("parsed_output", sa.JSON(), nullable=False),
        sa.Column("validation_status", sa.String(length=50), nullable=False),
        sa.Column("review_status", sa.String(length=50), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_outputs_task_id", "ai_outputs", ["task_id"])
    op.create_index("ix_ai_outputs_case_id", "ai_outputs", ["case_id"])
    op.create_index("ix_ai_outputs_note_id", "ai_outputs", ["note_id"])
    op.create_index("ix_ai_outputs_review_status", "ai_outputs", ["review_status"])


def downgrade() -> None:
    op.drop_table("ai_outputs")
    op.drop_table("ai_tasks")
