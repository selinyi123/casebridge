from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models import utc_now


class CaseReopenRequest(Base):
    __tablename__ = "case_reopen_requests"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    organization_id: Mapped[int] = mapped_column(Integer, default=1, index=True)
    case_id: Mapped[str] = mapped_column(String(40), index=True)
    request_status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    reopen_reason: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(String(120))
    reviewed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
