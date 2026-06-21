from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.persistent_repository import create_service_goal, get_case, list_service_goals
from app.db.session import get_db
from app.schemas import CreateServiceGoalRequest

router = APIRouter(prefix="/cases/{case_id}/goals", tags=["goals"])


@router.get("")
def index(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_service_goals(db, case_id)}


@router.post("")
def create(case_id: str, payload: CreateServiceGoalRequest, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    goal = create_service_goal(db, case_id, payload.model_dump())
    return {"goal": goal}
