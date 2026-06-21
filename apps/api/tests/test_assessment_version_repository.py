from app.db.assessment_version_repository import create_version, list_versions
from app.db.models import CaseAssessment
from app.db.session import SessionLocal


def test_assessment_version_repository_creates_incrementing_versions() -> None:
    with SessionLocal() as db:
        assessment = CaseAssessment(
            id="ASSESS-TEST-REPO",
            organization_id=1,
            case_id="CASE-0001",
            source_note_id="NOTE-0001",
            source_ai_output_id="AIOUT-TEST-REPO",
            provider="mock",
            prompt_version="intake-v0.1.7",
            assessment_type="intake",
            assessment_data={"needs": ["meal"]},
            reviewer_id="demo_social_worker",
            reviewer_responsibility_accepted=True,
        )
        db.merge(assessment)
        db.commit()

        first = create_version(db, "CASE-0001", assessment.id, {"needs": ["meal"]}, "first version", "demo_admin", 1)
        second = create_version(db, "CASE-0001", assessment.id, {"needs": ["meal", "mobility"]}, "second version", "demo_admin", 1)
        listed = list_versions(db, "CASE-0001", assessment.id, 1)

        assert first["version_number"] == 1
        assert second["version_number"] == 2
        assert [item["id"] for item in listed][-2:] == [first["id"], second["id"]]
