import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import AiOutput, AiTask, CaseAssessment, CaseNote, CaseRecord, Client, Referral, Resource, ServiceGoal
from app.db.outcome_repository import create_service_outcome
from app.db.persistent_repository import (
    apply_ai_output_to_assessment,
    create_referral,
    create_service_goal,
    get_case,
    list_case_notes,
    review_ai_output,
    update_referral_status,
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = SessionLocal()

    client_1 = Client(code="C-0001", display_name="Client 1", community="A", client_type="elderly_alone", primary_concern="meal", tags=["meal_difficulty"])
    client_2 = Client(code="C-0002", display_name="Client 2", community="B", client_type="elderly_alone", primary_concern="care", tags=["mobility_limited"])
    case_1 = CaseRecord(id="CASE-1", client_code="C-0001", title="Case 1")
    case_2 = CaseRecord(id="CASE-2", client_code="C-0002", title="Case 2")
    note_1 = CaseNote(id="NOTE-1", case_id="CASE-1", content_raw="raw phone 13800000000", content_clean="raw phone [REDACTED_PHONE]", pii_detected=True)
    resource = Resource(code="R-1", name="Meal", category="meal", match_codes=["meal"], status="active")
    referral_1 = Referral(id="REF-1", case_id="CASE-1", resource_code="R-1", status="to_verify", agreement_status="none")
    referral_2 = Referral(id="REF-2", case_id="CASE-2", resource_code="R-1", status="to_verify", agreement_status="none")
    goal_2 = ServiceGoal(id="GOAL-2", case_id="CASE-2", title="Other goal", target_state="Other target")
    ai_task_1 = AiTask(id="AITASK-1", case_id="CASE-1", note_id="NOTE-1", capability="intake", provider="mock", prompt_version="intake-v0.1.7")
    ai_output_1 = AiOutput(
        id="AIOUT-1",
        task_id="AITASK-1",
        case_id="CASE-1",
        note_id="NOTE-1",
        output_type="intake",
        parsed_output={
            "needs": ["餐食支持"],
            "risk_clues": [],
            "strengths": [],
            "missing_info": [],
            "suggested_next_steps": [],
            "disclaimer": "AI 生成草稿，需要社工人工确认",
        },
        raw_output={},
        review_status="pending",
    )
    assessment_2 = CaseAssessment(
        id="ASSESS-2",
        case_id="CASE-2",
        source_note_id="NOTE-1",
        source_ai_output_id="AIOUT-1",
        provider="mock",
        prompt_version="intake-v0.1.7",
        assessment_data={},
        reviewer_id="tester",
        reviewer_responsibility_accepted=True,
    )

    client_org2 = Client(
        organization_id=2,
        code="C-ORG2",
        display_name="Org 2 Client",
        community="Org2",
        client_type="elderly_alone",
        primary_concern="org2",
        tags=[],
    )
    case_org2 = CaseRecord(organization_id=2, id="CASE-ORG2", client_code="C-ORG2", title="Org 2 Case")
    note_org2 = CaseNote(
        organization_id=2,
        id="NOTE-ORG2",
        case_id="CASE-ORG2",
        content_raw="org2 raw",
        content_clean="org2 clean",
        pii_detected=False,
    )
    resource_org2 = Resource(organization_id=2, code="R-ORG2", name="Org 2 Resource", category="meal", match_codes=["meal"], status="active")
    referral_org2 = Referral(organization_id=2, id="REF-ORG2", case_id="CASE-ORG2", resource_code="R-ORG2", status="to_verify", agreement_status="none")

    session.add_all(
        [
            client_1,
            client_2,
            case_1,
            case_2,
            note_1,
            resource,
            referral_1,
            referral_2,
            goal_2,
            ai_task_1,
            ai_output_1,
            assessment_2,
            client_org2,
            case_org2,
            note_org2,
            resource_org2,
            referral_org2,
        ]
    )
    session.commit()

    try:
        yield session
    finally:
        session.close()


def test_referral_update_cannot_mutate_other_case(db):
    result = update_referral_status(db, case_id="CASE-1", referral_id="REF-2", status="contacted")
    assert result is None
    assert db.get(Referral, "REF-2").status == "to_verify"


def test_referral_transition_must_follow_state_machine(db):
    with pytest.raises(ValueError, match="invalid_referral_status_transition"):
        update_referral_status(db, case_id="CASE-1", referral_id="REF-1", status="success", agreement_status="verbal")


def test_referral_referred_requires_agreement(db):
    update_referral_status(db, case_id="CASE-1", referral_id="REF-1", status="contacted")
    with pytest.raises(ValueError, match="agreement_required_for_referral_status"):
        update_referral_status(db, case_id="CASE-1", referral_id="REF-1", status="referred")


def test_case_notes_hide_raw_content_by_default(db):
    notes = list_case_notes(db, "CASE-1")
    assert notes[0]["content_raw"] == "[REDACTED_RAW_CONTENT]"
    assert notes[0]["content_display"] == "raw phone [REDACTED_PHONE]"


def test_ai_review_validates_modified_output_schema(db):
    with pytest.raises(ValueError, match="invalid_modified_ai_output_schema"):
        review_ai_output(
            db=db,
            case_id="CASE-1",
            output_id="AIOUT-1",
            review_status="modified",
            reviewer_id="tester",
            modified_output={"needs": "not-a-list"},
        )


def test_apply_ai_output_marks_applied_to(db):
    reviewed = review_ai_output(
        db=db,
        case_id="CASE-1",
        output_id="AIOUT-1",
        review_status="accepted",
        reviewer_id="tester",
    )
    assert reviewed["reviewed_by"] == "tester"

    assessment = apply_ai_output_to_assessment(
        db=db,
        case_id="CASE-1",
        output_id="AIOUT-1",
        reviewer_id="tester",
        responsibility_accepted=True,
    )
    assert assessment is not None
    assert db.get(AiOutput, "AIOUT-1").applied_to == f"case_assessments:{assessment['id']}"


def test_outcome_rejects_goal_from_other_case(db):
    with pytest.raises(ValueError, match="goal_not_found"):
        create_service_outcome(
            db,
            case_id="CASE-1",
            payload={"goal_id": "GOAL-2", "narrative": "Should be rejected"},
        )


def test_outcome_rejects_assessment_from_other_case(db):
    with pytest.raises(ValueError, match="assessment_not_found"):
        create_service_outcome(
            db,
            case_id="CASE-1",
            payload={"assessment_id": "ASSESS-2", "narrative": "Should be rejected"},
        )


def test_repository_get_case_is_organization_scoped(db):
    assert get_case(db, "CASE-ORG2") is None
    assert get_case(db, "CASE-ORG2", organization_id=2)["id"] == "CASE-ORG2"


def test_repository_writers_reject_foreign_organization_case_ids(db):
    with pytest.raises(ValueError, match="case_not_found"):
        create_service_goal(db, "CASE-ORG2", {"title": "bad", "target_state": "bad"}, organization_id=1)

    with pytest.raises(ValueError, match="case_not_found"):
        create_referral(db, "CASE-ORG2", {"resource_code": "R-ORG2", "agreement_status": "none"}, organization_id=1)

    with pytest.raises(ValueError, match="case_not_found"):
        create_service_outcome(db, "CASE-ORG2", {"narrative": "bad"}, organization_id=1)


def test_repository_writers_allow_matching_organization(db):
    goal = create_service_goal(db, "CASE-ORG2", {"title": "ok", "target_state": "ok"}, organization_id=2)
    assert goal["organization_id"] == 2
    assert goal["case_id"] == "CASE-ORG2"

    referral = create_referral(db, "CASE-ORG2", {"resource_code": "R-ORG2", "agreement_status": "none"}, organization_id=2)
    assert referral["organization_id"] == 2
    assert referral["case_id"] == "CASE-ORG2"
