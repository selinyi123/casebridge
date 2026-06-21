from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models import utc_now


class ServicePlan(Base):
    __tablename__ = "service_plans"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    organization_id: Mapped[int] = mapped_column(Integer, default=1, index=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    assessment_id: Mapped[str | None] = mapped_column(ForeignKey("case_assessments.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    plan_status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    plan_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_by: Mapped[str] = mapped_column(String(120), default="demo_social_worker")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ServiceIntervention(Base):
    __tablename__ = "service_interventions"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    organization_id: Mapped[int] = mapped_column(Integer, default=1, index=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("service_plans.id"), index=True)
    goal_id: Mapped[str | None] = mapped_column(ForeignKey("service_goals.id"), nullable=True, index=True)
    intervention_type: Mapped[str] = mapped_column(String(80), default="followup")
    narrative: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[str] = mapped_column(String(120), default="demo_social_worker")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
