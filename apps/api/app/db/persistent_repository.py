from datetime import datetime
from itertools import count
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CaseNote, CaseRecord, Client, Resource, model_to_dict, utc_now

_note_counter = count(2)


def _dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value.strip():
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return utc_now()


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
    note_id = f"NOTE-{next(_note_counter):04d}"
    while db.get(CaseNote, note_id):
        note_id = f"NOTE-{next(_note_counter):04d}"
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
