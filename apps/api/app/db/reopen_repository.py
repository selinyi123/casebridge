from itertools import count
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, CaseRecord, model_to_dict, utc_now
from app.db.reopen_models import CaseReopenRequest

_reopen_counter = count(1)


def _next_id(db: Session) -> str:
    identifier = f"REOPEN-{next(_reopen_counter):04d}"
    while db.get(CaseReopenRequest, identifier):
        identifier = f"REOPEN-{next(_reopen_counter):04d}"
    return identifier


def list_reopen_requests(db: Session, case_id: str, organization_id: int = 1) -> list[dict[str, Any]]:
    stmt = select(CaseReopenRequest).where(CaseReopenRequest.organization_id == organization_id, CaseReopenRequest.case_id == case_id).order_by(CaseReopenRequest.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_reopen_request(db: Session, case_id: str, payload: dict[str, Any], actor: str, organization_id: int = 1) -> dict[str, Any]:
    case = db.scalar(select(CaseRecord).where(CaseRecord.id == case_id, CaseRecord.organization_id == organization_id))
    if not case:
        raise ValueError("case_not_found")
    request = CaseReopenRequest(
        id=_next_id(db),
        organization_id=organization_id,
        case_id=case_id,
        request_status="draft",
        reopen_reason=payload.get("reopen_reason", ""),
        created_by=actor,
    )
    db.add(request)
    db.add(AuditEvent(organization_id=organization_id, case_id=case_id, event_type="reopen_request.created", entity_type="case_reopen_request", entity_id=request.id, actor=actor, payload={"case_status": case.status}))
    db.commit()
    db.refresh(request)
    return model_to_dict(request)


def review_reopen_request(db: Session, case_id: str, request_id: str, decision: str, actor: str, organization_id: int = 1) -> dict[str, Any]:
    request = db.scalar(select(CaseReopenRequest).where(CaseReopenRequest.id == request_id, CaseReopenRequest.organization_id == organization_id, CaseReopenRequest.case_id == case_id))
    if not request:
        raise ValueError("reopen_request_not_found")
    request.request_status = decision
    request.reviewed_by = actor
    request.reviewed_at = utc_now()
    db.add(request)
    db.add(AuditEvent(organization_id=organization_id, case_id=case_id, event_type="reopen_request.reviewed", entity_type="case_reopen_request", entity_id=request.id, actor=actor, payload={"decision": decision, "case_status_changed": False}))
    db.commit()
    db.refresh(request)
    return model_to_dict(request)


def reopen_case_from_approved_request(db: Session, case_id: str, request_id: str, actor: str, organization_id: int = 1) -> dict[str, Any]:
    request = db.scalar(select(CaseReopenRequest).where(CaseReopenRequest.id == request_id, CaseReopenRequest.organization_id == organization_id, CaseReopenRequest.case_id == case_id))
    if not request:
        raise ValueError("reopen_request_not_found")
    if request.request_status != "approved":
        raise ValueError("reopen_request_not_approved")
    case = db.scalar(select(CaseRecord).where(CaseRecord.id == case_id, CaseRecord.organization_id == organization_id))
    if not case:
        raise ValueError("case_not_found")
    if case.status != "closed":
        raise ValueError("case_not_closed")
    case.status = "open"
    case.stage = "reopened"
    db.add(case)
    db.add(AuditEvent(organization_id=organization_id, case_id=case_id, event_type="case.reopened", entity_type="case", entity_id=case_id, actor=actor, payload={"reopen_request_id": request.id, "human_confirmed": True}))
    db.commit()
    db.refresh(case)
    return model_to_dict(case)
