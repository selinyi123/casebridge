from pydantic import BaseModel, Field


class CreateCaseNoteRequest(BaseModel):
    note_type: str = Field(default="visit", min_length=1, max_length=50)
    content_raw: str = Field(min_length=1, max_length=5000)
    occurred_at: str | None = None


class ResourceMatchRequest(BaseModel):
    need_tag_codes: list[str] = Field(default_factory=list)
