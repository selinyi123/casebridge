from datetime import datetime
from itertools import count
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AiOutput, AiTask, AuditEvent, CaseNote, CaseRecord, Client, Referral, Resource, ServiceGoal, model_to_dict, utc_now

_note_counter = count(2)
_goal_counter = count(1)
_referral_counter = count(1)
_ai_task_counter = count(1)
_ai_output_counter = count(1)
BLOCKED_REFERRAL_STATUSES = {"referred", "success", "completed"}
VALID_AGREEMENT_STATUSES = {"verbal", "written"}
APPLYABLE_REVIEW_STATUSES = {"accepted", "modified"}


def _dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value.strip():
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return utc_now()


def _next_id(prefix: str, counter: count, model: type, db: Session) -> str:
    identifier = f"{prefix}-{next(counter):04d}"
    while db.get(model, identifier):
        identifier = f"{prefix}-{next(counter):04d}"
    return identifier


def assert_referral_transition_allowed(status: str, agreement_status: str) -> None:
    if status in BLOCKED_REFERRAL_STATUSES and agreement_status not in VALID_AGREEMENT_STATUSES:
        raise ValueError("agreement_required_for_referral_status")


def record_audit_event(db: Session, case_id: str, event_type: str, entity_type: str, entity_id: str, payload: dict[str, Any] | None = None) -> None:
    db.add(AuditEvent(case_id=case_id, event_type=event_type, entity_type=entity_type, entity_id=entity_id, payload=payload or {}))


def list_clients(db: Session) -> list[dict[str, Any]]:
    return [model_to_dict(row) for row in db.scalars(select(Client).order_by(Client.code)).all()]


def get_client(db: Session, code: str) -> dict[str, Any] | None:
    row = db.scalar(select(Client).where(Client.code == code))
    return model_to_dict(row) if row else None


def list_cases(db: Session, client_code: str | None = None) -> list[dict[str, Any]]:
    stmt = select(CaseRecord).order_by(CaseRecord.opened_at)
    if client_code:
        stmt = stmt.where(CaseRecord.client_code == client_code)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def get_case(db: Session, case_id: str) -> dict[str, Any] | None:
    row = db.get(CaseRecord, case_id)
    return model_to_dict(row) if row else None


def get_note(db: Session, note_id: str) -> dict[str, Any] | None:
    row = db.get(CaseNote, note_id)
    return model_to_dict(row) if row else None


def list_case_notes(db: Session, case_id: str) -> list[dict[str, Any]]:
    stmt = select(CaseNote).where(CaseNote.case_id == case_id).order_by(CaseNote.occurred_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_case_note(db: Session, case_id: str, payload: dict[str, Any], content_clean: str, pii_detected: bool) -> dict[str, Any]:
    note_id = _next_id("NOTE", _note_counter, CaseNote, db)
    note = CaseNote(id=note_id, case_id=case_id, note_type=payload.get("note_type", "visit"), content_raw=payload.get("content_raw", ""), content_clean=content_clean, occurred_at=_dt(payload.get("occurred_at")), pii_detected=pii_detected, source="human")
    db.add(note)
    record_audit_event(db, case_id, "note.created", "case_note", note_id, {"note_type": note.note_type, "pii_detected": pii_detected})
    db.commit()
    db.refresh(note)
    return model_to_dict(note)


def list_resources(db: Session) -> list[dict[str, Any]]:
    return [model_to_dict(row) for row in db.scalars(select(Resource).order_by(Resource.code)).all()]


def get_resource(db: Session, resource_code: str) -> dict[str, Any] | None:
    row = db.get(Resource, resource_code)
    return model_to_dict(row) if row else None


def list_service_goals(db: Session, case_id: str) -> list[dict[str, Any]]:
    stmt = select(ServiceGoal).where(ServiceGoal.case_id == case_id).order_by(ServiceGoal.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_service_goal(db: Session, case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    goal = ServiceGoal(id=_next_id("GOAL", _goal_counter, ServiceGoal, db), case_id=case_id, title=payload.get("title", ""), target_state=payload.get("target_state", ""), status=payload.get("status", "not_started"))
    db.add(goal)
    record_audit_event(db, case_id, "goal.created", "service_goal", goal.id, {"status": goal.status})
    db.commit()
    db.refresh(goal)
    return model_to_dict(goal)


def list_referrals(db: Session, case_id: str) -> list[dict[str, Any]]:
    stmt = select(Referral).where(Referral.case_id == case_id).order_by(Referral.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_referral(db: Session, case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    referral = Referral(id=_next_id("REF", _referral_counter, Referral, db), case_id=case_id, resource_code=payload.get("resource_code", ""), status="to_verify", agreement_status=payload.get("agreement_status", "none"), notes=payload.get("notes"))
    db.add(referral)
    record_audit_event(db, case_id, "resource_link.created", "resource_link", referral.id, {"resource_code": referral.resource_code, "agreement_status": referral.agreement_status})
    db.commit()
    db.refresh(referral)
    return model_to_dict(referral)


def update_referral_status(db: Session, referral_id: str, status: str, agreement_status: str | None = None) -> dict[str, Any] | None:
    referral = db.get(Referral, referral_id)
    if not referral:
        return None
    next_agreement = agreement_status or referral.agreement_status
    assert_referral_transition_allowed(status, next_agreement)
    referral.status = status
    referral.agreement_status = next_agreement
    db.add(referral)
    record_audit_event(db, referral.case_id, "resource_link.status_changed", "resource_link", referral.id, {"status": status, "agreement_status": next_agreement})
    db.commit()
    db.refresh(referral)
    return model_to_dict(referral)


def create_ai_intake_output(db: Session, case_id: str, note_id: str, parsed_output: dict[str, Any], provider: str, prompt_version: str) -> dict[str, Any]:
    task = AiTask(id=_next_id("AITASK", _ai_task_counter, AiTask, db), case_id=case_id, note_id=note_id, capability="intake", provider=provider, prompt_version=prompt_version, status="completed")
    output = AiOutput(id=_next_id("AIOUT", _ai_output_counter, AiOutput, db), task_id=task.id, case_id=case_id, note_id=note_id, output_type="intake", raw_output=parsed_output, parsed_output=parsed_output, validation_status="valid", review_status="pending")
    db.add(task)
    db.add(output)
    record_audit_event(db, case_id, "ai.intake_draft.created", "ai_output", output.id, {"task_id": task.id, "provider": task.provider, "prompt_version": task.prompt_version, "review_status": output.review_status})
    db.commit()
    db.refresh(output)
    return model_to_dict(output)


def list_ai_outputs(db: Session, case_id: str) -> list[dict[str, Any]]:
    stmt = select(AiOutput).where(AiOutput.case_id == case_id).order_by(AiOutput.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def get_ai_output(db: Session, output_id: str) -> dict[str, Any] | None:
    row = db.get(AiOutput, output_id)
    return model_to_dict(row) if row else None


def review_ai_output(db: Session, output_id: str, review_status: str, reviewer_notes: str | None = None, modified_output: dict[str, Any] | None = None) -> dict[str, Any] | None:
    output = db.get(AiOutput, output_id)
    if not output:
        return None
    output.review_status = review_status
    output.reviewer_notes = reviewer_notes
    if modified_output is not None:
        output.parsed_output = modified_output
    db.add(output)
    record_audit_event(db, output.case_id, "ai.output.reviewed", "ai_output", output.id, {"review_status": review_status})
    db.commit()
    db.refresh(output)
    return model_to_dict(output)


def create_apply_preview(db: Session, output_id: str) -> dict[str, Any] | None:
    output = db.get(AiOutput, output_id)
    if not output:
        return None
    output_dict = model_to_dict(output)
    if output_dict["review_status"] not in APPLYABLE_REVIEW_STATUSES:
        raise ValueError("ai_output_not_reviewed_for_apply_preview")
    preview = {
        "output_id": output_dict["id"],
        "case_id": output_dict["case_id"],
        "note_id": output_dict["note_id"],
        "review_status": output_dict["review_status"],
        "candidate_assessment": output_dict["parsed_output"],
        "will_write_formal_fields": False,
        "requires_explicit_apply_action": True,
    }
    record_audit_event(db, output_dict["case_id"], "ai.apply_preview.created", "ai_output", output_dict["id"], {"review_status": output_dict["review_status"]})
    db.commit()
    return preview


def list_audit_events(db: Session, case_id: str) -> list[dict[str, Any]]:
    stmt = select(AuditEvent).where(AuditEvent.case_id == case_id).order_by(AuditEvent.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def list_case_timeline(db: Session, case_id: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for note in list_case_notes(db, case_id):
        events.append({"kind": "note", "id": note["id"], "at": note["occurred_at"], "title": note["note_type"], "payload": note})
    for goal in list_service_goals(db, case_id):
        events.append({"kind": "goal", "id": goal["id"], "at": goal["created_at"], "title": goal["title"], "payload": goal})
    for link in list_referrals(db, case_id):
        events.append({"kind": "resource_link", "id": link["id"], "at": link["created_at"], "title": link["resource_code"], "payload": link})
    for ai_output in list_ai_outputs(db, case_id):
        events.append({"kind": "ai_output", "id": ai_output["id"], "at": ai_output["created_at"], "title": ai_output["output_type"], "payload": ai_output})
    for audit in list_audit_events(db, case_id):
        events.append({"kind": "audit", "id": str(audit["id"]), "at": audit["created_at"], "title": audit["event_type"], "payload": audit})
    return sorted(events, key=lambda item: item["at"])
