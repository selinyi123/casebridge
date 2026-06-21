from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import RequireCaseWriter, RequireSupervisorReviewer
from app.db.persistent_repository import create_service_goal, get_case, list_service_goals
from app.db.service_plan_repository import build_evidence_chain, create_intervention, create_service_plan, list_interventions, list_service_plans
from app.db.session import get_db
from app.db.supervisor_review_repository import build_closure_readiness, create_review, list_reviews
from app.schemas import CreateServiceGoalRequest

router = APIRouter(prefix="/cases/{case_id}/goals", tags=["goals"])


class CreateServicePlanRequest(BaseModel):
    assessment_id: str | None = Field(default=None, max_length=40)
    title: str = Field(min_length=1, max_length=200)
    plan_status: str = Field(default="draft", pattern="^(draft|active|paused|completed|cancelled)$")
    plan_data: dict = Field(default_factory=dict)


class CreateInterventionRequest(BaseModel):
    plan_id: str = Field(min_length=1, max_length=40)
    goal_id: str | None = Field(default=None, max_length=40)
    intervention_type: str = Field(default="followup", pattern="^(followup|resource_coordination|home_visit|supervision_note)$")
    narrative: str = Field(min_length=1, max_length=3000)
    evidence: str | None = Field(default=None, max_length=3000)


class CreateSupervisorReviewRequest(BaseModel):
    review_type: str = Field(default="closure_readiness", pattern="^(closure_readiness|case_consultation|evidence_review)$")
    decision: str = Field(default="needs_more_work", pattern="^(needs_more_work|ready_for_closure|continue_service)$")
    note: str = Field(min_length=1, max_length=3000)


@router.get("/closure-readiness")
def closure_readiness(case_id: str, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return build_closure_readiness(db, case_id, current_user.organization_id)


@router.get("/supervisor-reviews")
def supervisor_reviews(case_id: str, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_reviews(db, case_id, current_user.organization_id)}


@router.post("/supervisor-reviews")
def create_supervisor_review(case_id: str, payload: CreateSupervisorReviewRequest, current_user: RequireSupervisorReviewer, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    review = create_review(db, case_id, payload.model_dump(), current_user.username, current_user.organization_id)
    return {"review": review}


@router.get("/plans")
def plans(case_id: str, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_service_plans(db, case_id, current_user.organization_id)}


@router.post("/plans")
def create_plan(case_id: str, payload: CreateServicePlanRequest, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        plan = create_service_plan(db, case_id, payload.model_dump(), current_user.username, current_user.organization_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"plan": plan}


@router.get("/interventions")
def interventions(case_id: str, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_interventions(db, case_id, current_user.organization_id)}


@router.post("/interventions")
def create_intervention_record(case_id: str, payload: CreateInterventionRequest, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        intervention = create_intervention(db, case_id, payload.model_dump(), current_user.username, current_user.organization_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"intervention": intervention}


@router.get("/evidence-chain")
def evidence_chain(case_id: str, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return build_evidence_chain(db, case_id, current_user.organization_id)


@router.get("")
def index(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_service_goals(db, case_id)}


@router.post("")
def create(case_id: str, payload: CreateServiceGoalRequest, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    organization_id = current_user.organization_id
    if not get_case(db, case_id, organization_id=organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    goal = create_service_goal(db, case_id, payload.model_dump(), actor=current_user.username, organization_id=organization_id)
    return {"goal": goal}
