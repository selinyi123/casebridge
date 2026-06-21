from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.outcome_repository import list_service_outcomes
from app.db.persistent_repository import get_case, list_case_timeline
from app.db.session import get_db

router = APIRouter(prefix="/cases/{case_id}/timeline", tags=["timeline"])


@router.get("")
def index(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    items = list_case_timeline(db, case_id)
    for outcome in list_service_outcomes(db, case_id):
        items.append({
            "kind": "outcome",
            "id": outcome["id"],
            "at": outcome["created_at"],
            "title": outcome["outcome_type"],
            "payload": outcome,
        })
    return {"items": sorted(items, key=lambda item: item["at"])}
