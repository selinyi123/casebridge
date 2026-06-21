from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models import utc_now


class SupervisorReview(Base):
    __tablename__ = "supervisor_reviews"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    organization_id: Mapped[int] = mapped_column(Integer, default=1, index=True)
    case_id: Mapped[str] = mapped_column(String(40), index=True)
    review_type: Mapped[str] = mapped_column(String(80), default="closure_readiness")
    decision: Mapped[str] = mapped_column(String(80), default="needs_more_work")
    blockers: Mapped[list[str]] = mapped_column(JSON, default=list)
    evidence_summary: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    note: Mapped[str] = mapped_column(Text)
    reviewed_by: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
