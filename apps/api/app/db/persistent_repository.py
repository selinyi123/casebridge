from datetime import datetime
from itertools import count
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CaseNote, CaseRecord, Client, Referral, Resource, ServiceGoal, model_to_dict, utc_now

_note_counter = count(2)
_goal_counter = count(1)
_referral_counter = count(1)
BLOCKED_REFERRAL_STATUSES = {"referred", "success", "completed"}
VALID_AGREEMENT_STATUSES = {"verbal", "written"}


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


def list_case_notes(db: Session, case_id: str) -> list[dict[str, Any]]:
    stmt = select(CaseNote).where(CaseNote.case_id == case_id).order_by(CaseNote.occurred_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_case_note(db: Session, case_id: str, payload: dict[str, Any], content_clean: str, pii_detected: bool) -> dict[str, Any]:
    note_id = _next_id("NOTE", _note_counter, CaseNote, db)
    note = CaseNote(
        id=note_id,
        case_id=case_id,
        note_type=payload.get("note_type", "visit"),
        content_raw=payload.get("content_raw", ""),
        content_clean=content_clean,
        occurred_at=_dt(payload.get("occurred_at")),
        pii_detected=pii_detected,
        source="human",
    )
    db.add(note)
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
    goal = ServiceGoal(
        id=_next_id("GOAL", _goal_counter, ServiceGoal, db),
        case_id=case_id,
        title=payload.get("title", ""),
        target_state=payload.get("target_state", ""),
        status=payload.get("status", "not_started"),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return model_to_dict(goal)


def list_referrals(db: Session, case_id: str) -> list[dict[str, Any]]:
    stmt = select(Referral).where(Referral.case_id == case_id).order_by(Referral.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_referral(db: Session, case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    referral = Referral(
        id=_next_id("REF", _referral_counter, Referral, db),
        case_id=case_id,
        resource_code=payload.get("resource_code", ""),
        status="to_verify",
        agreement_status=payload.get("agreement_status", "none"),
        notes=payload.get("notes"),
    )
    db.add(referral)
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
    db.commit()
    db.refresh(referral)
    return model_to_dict(referral)
