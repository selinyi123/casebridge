from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.persistent_repository import get_case, list_case_timeline
from app.db.session import get_db

router = APIRouter(prefix="/cases/{case_id}/timeline", tags=["timeline"])


@router.get("")
def index(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_case_timeline(db, case_id)}
