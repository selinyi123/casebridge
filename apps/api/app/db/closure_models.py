from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models import utc_now


class CaseClosureDraft(Base):
    __tablename__ = "case_closure_drafts"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    organization_id: Mapped[int] = mapped_column(Integer, default=1, index=True)
    case_id: Mapped[str] = mapped_column(String(40), index=True)
    draft_status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    closure_reason: Mapped[str] = mapped_column(Text)
    blocker_snapshot: Mapped[list[str]] = mapped_column(JSON, default=list)
    evidence_summary: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    report_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_by: Mapped[str] = mapped_column(String(120))
    approved_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
