from itertools import count
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, model_to_dict
from app.db.service_plan_repository import build_evidence_chain
from app.db.supervisor_review_models import SupervisorReview

_review_counter = count(1)


def _next_id(db: Session) -> str:
    identifier = f"SREV-{next(_review_counter):04d}"
    while db.get(SupervisorReview, identifier):
        identifier = f"SREV-{next(_review_counter):04d}"
    return identifier


def build_closure_readiness(db: Session, case_id: str, organization_id: int = 1) -> dict[str, Any]:
    chain = build_evidence_chain(db, case_id, organization_id)
    blockers = []
    if not chain["plans"]:
        blockers.append("missing_service_plan")
    if not chain["interventions"]:
        blockers.append("missing_intervention")
    if not chain["outcomes"]:
        blockers.append("missing_outcome")
    if not chain["events"]:
        blockers.append("missing_evidence_events")
    return {
        "case_id": case_id,
        "ready": len(blockers) == 0,
        "blockers": blockers,
        "evidence_summary": {
            "plan_count": len(chain["plans"]),
            "intervention_count": len(chain["interventions"]),
            "outcome_count": len(chain["outcomes"]),
            "event_count": len(chain["events"]),
        },
        "manual_only": True,
    }


def list_reviews(db: Session, case_id: str, organization_id: int = 1) -> list[dict[str, Any]]:
    stmt = select(SupervisorReview).where(SupervisorReview.organization_id == organization_id, SupervisorReview.case_id == case_id).order_by(SupervisorReview.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_review(db: Session, case_id: str, payload: dict[str, Any], actor: str, organization_id: int = 1) -> dict[str, Any]:
    readiness = build_closure_readiness(db, case_id, organization_id)
    review = SupervisorReview(
        id=_next_id(db),
        organization_id=organization_id,
        case_id=case_id,
        review_type=payload.get("review_type", "closure_readiness"),
        decision=payload.get("decision", "needs_more_work"),
        blockers=readiness["blockers"],
        evidence_summary=readiness["evidence_summary"],
        note=payload.get("note", ""),
        reviewed_by=actor,
    )
    db.add(review)
    db.add(AuditEvent(organization_id=organization_id, case_id=case_id, event_type="supervisor_review.created", entity_type="supervisor_review", entity_id=review.id, actor=actor, payload={"decision": review.decision, "ready": readiness["ready"]}))
    db.commit()
    db.refresh(review)
    return model_to_dict(review)
