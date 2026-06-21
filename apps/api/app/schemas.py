from typing import Any

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=200)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    organization_id: int


class CurrentUserResponse(BaseModel):
    username: str
    display_name: str
    role: str
    organization_id: int


class CreateCaseNoteRequest(BaseModel):
    note_type: str = Field(default="visit", min_length=1, max_length=50)
    content_raw: str = Field(min_length=1, max_length=5000)
    occurred_at: str | None = None


class ResourceMatchRequest(BaseModel):
    need_tag_codes: list[str] = Field(default_factory=list)


class CreateServiceGoalRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    target_state: str = Field(min_length=1, max_length=2000)
    status: str = Field(default="not_started", pattern="^(not_started|in_progress|achieved|blocked|dropped)$")


class CreateReferralRequest(BaseModel):
    resource_code: str = Field(min_length=1, max_length=40)
    agreement_status: str = Field(default="none", pattern="^(none|verbal|written|expired)$")
    notes: str | None = Field(default=None, max_length=2000)


class UpdateReferralStatusRequest(BaseModel):
    status: str = Field(pattern="^(to_verify|contacted|referred|success|failed|awaiting_callback|completed)$")
    agreement_status: str | None = Field(default=None, pattern="^(none|verbal|written|expired)$")


class GenerateAiIntakeRequest(BaseModel):
    note_id: str = Field(min_length=1, max_length=40)


class ReviewAiOutputRequest(BaseModel):
    review_status: str = Field(pattern="^(accepted|modified|rejected)$")
    reviewer_id: str = Field(default="demo_social_worker", min_length=1, max_length=120)
    reviewer_notes: str | None = Field(default=None, max_length=2000)
    modified_output: dict[str, Any] | None = None


class ApplyAiOutputRequest(BaseModel):
    reviewer_responsibility_accepted: bool
    reviewer_id: str = Field(default="demo_social_worker", min_length=1, max_length=120)


class CreateServiceOutcomeRequest(BaseModel):
    goal_id: str | None = Field(default=None, max_length=40)
    assessment_id: str | None = Field(default=None, max_length=40)
    outcome_type: str = Field(default="goal_attainment", pattern="^(goal_attainment|followup_observation|resource_result)$")
    gas_score: int | None = Field(default=None, ge=-2, le=2)
    narrative: str = Field(min_length=1, max_length=3000)
    evidence: str | None = Field(default=None, max_length=3000)
    recorded_by: str = Field(default="demo_social_worker", min_length=1, max_length=120)


class IntakeDraftOutput(BaseModel):
    needs: list[str] = Field(default_factory=list)
    risk_clues: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    suggested_next_steps: list[str] = Field(default_factory=list)
    disclaimer: str = "AI 生成草稿，需要社工人工确认"
