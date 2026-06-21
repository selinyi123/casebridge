from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.auth import JWT_ALGORITHM, JWT_SECRET, authenticate_user, create_access_token, hash_password
from app.core.privacy import redact_text
from app.db.base import Base
from app.db.models import User


def test_authenticate_user_and_create_token():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    db = SessionLocal()
    db.add(
        User(
            username="demo_social_worker",
            password_hash=hash_password("casebridge_demo_password"),
            display_name="Demo Social Worker",
            role="social_worker",
        )
    )
    db.commit()

    user = authenticate_user(db, "demo_social_worker", "casebridge_demo_password")
    assert user is not None
    assert user.last_login_at is not None

    token = create_access_token(subject=user.username, role=user.role, organization_id=user.organization_id)
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "demo_social_worker"
    assert payload["role"] == "social_worker"
    db.close()


def test_redactor_masks_common_structured_pii():
    result = redact_text("联系电话13812345678，身份证110101199001011234，住址和安社区12号3栋201室。")
    assert "13812345678" not in result.clean_text
    assert "110101199001011234" not in result.clean_text
    assert "12号" not in result.clean_text
    assert "[REDACTED_PHONE]" in result.clean_text
    assert "[REDACTED_ID]" in result.clean_text
    assert result.is_safe_for_model is True


def test_redactor_blocks_minor_and_diagnosis_clues_for_model():
    result = redact_text("服务对象13岁，诊断为抑郁症，家属希望咨询资源。")
    hit_types = {item["type"] for item in result.pii_hits}
    assert "minor" in hit_types
    assert "diagnosis_or_health" in hit_types
    assert result.is_safe_for_model is False
