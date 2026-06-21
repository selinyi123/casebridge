from pydantic import BaseModel, Field


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
    reviewer_notes: str | None = Field(default=None, max_length=2000)
    modified_output: dict | None = None


class IntakeDraftOutput(BaseModel):
    needs: list[str] = Field(default_factory=list)
    risk_clues: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    suggested_next_steps: list[str] = Field(default_factory=list)
    disclaimer: str = "AI draft only; social worker review required."
