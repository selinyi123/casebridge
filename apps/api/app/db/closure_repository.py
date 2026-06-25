from itertools import count
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.closure_models import CaseClosureDraft
from app.db.models import AuditEvent, CaseRecord, utc_now, model_to_dict
from app.db.supervisor_review_repository import build_closure_readiness, list_reviews

_closure_counter = count(1)


def _next_id(db: Session) -> str:
    identifier = f"CLOSE-{next(_closure_counter):04d}"
    while db.get(CaseClosureDraft, identifier):
        identifier = f"CLOSE-{next(_closure_counter):04d}"
    return identifier


def _markdown_report(case_id: str, readiness: dict[str, Any], reviews: list[dict[str, Any]]) -> str:
    blockers = readiness.get("blockers", [])
    summary = readiness.get("evidence_summary", {})
    lines = [
        f"# Closure Support Report: {case_id}",
        "",
        f"Ready: {readiness.get('ready')}",
        f"Manual only: {readiness.get('manual_only')}",
        "",
        "## Evidence Summary",
        f"- Plans: {summary.get('plan_count', 0)}",
        f"- Interventions: {summary.get('intervention_count', 0)}",
        f"- Outcomes: {summary.get('outcome_count', 0)}",
        f"- Evidence events: {summary.get('event_count', 0)}",
        "",
        "## Blockers",
    ]
    if blockers:
        lines.extend([f"- {item}" for item in blockers])
    else:
        lines.append("- none")
    lines.extend(["", "## Supervisor Reviews", f"- Count: {len(reviews)}", "", "This report is support material only. It does not close the case."])
    return "\n".join(lines)


def build_closure_report(db: Session, case_id: str, organization_id: int = 1) -> dict[str, Any]:
    readiness = build_closure_readiness(db, case_id, organization_id)
    reviews = list_reviews(db, case_id, organization_id)
    return {"case_id": case_id, "readiness": readiness, "reviews": reviews, "markdown": _markdown_report(case_id, readiness, reviews), "manual_only": True, "auto_close": False}


def list_closure_drafts(db: Session, case_id: str, organization_id: int = 1) -> list[dict[str, Any]]:
    stmt = select(CaseClosureDraft).where(CaseClosureDraft.organization_id == organization_id, CaseClosureDraft.case_id == case_id).order_by(CaseClosureDraft.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_closure_draft(db: Session, case_id: str, payload: dict[str, Any], actor: str, organization_id: int = 1) -> dict[str, Any]:
    report = build_closure_report(db, case_id, organization_id)
    draft = CaseClosureDraft(
        id=_next_id(db),
        organization_id=organization_id,
        case_id=case_id,
        draft_status="draft",
        closure_reason=payload.get("closure_reason", ""),
        blocker_snapshot=report["readiness"]["blockers"],
        evidence_summary=report["readiness"]["evidence_summary"],
        report_data=report,
        created_by=actor,
    )
    db.add(draft)
    db.add(AuditEvent(organization_id=organization_id, case_id=case_id, event_type="closure_draft.created", entity_type="case_closure_draft", entity_id=draft.id, actor=actor, payload={"ready": report["readiness"]["ready"], "auto_close": False}))
    db.commit()
    db.refresh(draft)
    return model_to_dict(draft)


def approve_closure_draft(db: Session, case_id: str, draft_id: str, decision: str, actor: str, organization_id: int = 1) -> dict[str, Any]:
    draft = db.scalar(select(CaseClosureDraft).where(CaseClosureDraft.id == draft_id, CaseClosureDraft.organization_id == organization_id, CaseClosureDraft.case_id == case_id))
    if not draft:
        raise ValueError("closure_draft_not_found")
    draft.draft_status = decision
    draft.approved_by = actor
    draft.approved_at = utc_now()
    db.add(draft)
    db.add(AuditEvent(organization_id=organization_id, case_id=case_id, event_type="closure_draft.reviewed", entity_type="case_closure_draft", entity_id=draft.id, actor=actor, payload={"decision": decision, "case_status_changed": False}))
    db.commit()
    db.refresh(draft)
    return model_to_dict(draft)


def close_case_from_approved_draft(db: Session, case_id: str, draft_id: str, actor: str, organization_id: int = 1) -> dict[str, Any]:
    draft = db.scalar(select(CaseClosureDraft).where(CaseClosureDraft.id == draft_id, CaseClosureDraft.organization_id == organization_id, CaseClosureDraft.case_id == case_id))
    if not draft:
        raise ValueError("closure_draft_not_found")
    if draft.draft_status != "approved":
        raise ValueError("closure_draft_not_approved")
    case = db.scalar(select(CaseRecord).where(CaseRecord.id == case_id, CaseRecord.organization_id == organization_id))
    if not case:
        raise ValueError("case_not_found")
    if case.status == "closed":
        raise ValueError("case_already_closed")
    case.status = "closed"
    case.stage = "closed"
    db.add(case)
    db.add(AuditEvent(organization_id=organization_id, case_id=case_id, event_type="case.closed", entity_type="case", entity_id=case_id, actor=actor, payload={"closure_draft_id": draft.id, "human_confirmed": True}))
    db.commit()
    db.refresh(case)
    return model_to_dict(case)
