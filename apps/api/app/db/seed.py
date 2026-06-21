from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CaseNote, CaseRecord, Client, Resource


def seed_demo_data(db: Session) -> None:
    existing = db.scalar(select(Client).where(Client.code == "C-0001"))
    if existing:
        return

    client = Client(
        code="C-0001",
        display_name="独居老人 C-0001",
        age=78,
        gender="female",
        community="和安社区",
        client_type="elderly_alone",
        primary_concern="餐食困难、行动不便、家庭支持不足、睡眠不好",
        existing_support="邻里偶尔关照，暂无固定探访机制",
        consent_status="oral",
        tags=["meal_difficulty", "mobility_limited", "living_alone", "weak_family_support", "sleep_emotional"],
    )
    case = CaseRecord(
        id="CASE-0001",
        client_code="C-0001",
        title="C-0001 独居老人支持个案",
        stage="intake",
        status="open",
        primary_worker="demo_social_worker",
    )
    note = CaseNote(
        id="NOTE-0001",
        case_id="CASE-0001",
        note_type="home_visit",
        content_raw="今天入户走访 C-0001，老人 78 岁，独居，腿脚不便，最近做饭困难，子女在外地，晚上睡不好，希望了解社区有没有方便吃饭的地方。",
        content_clean="今天入户走访 C-0001，老人 78 岁，独居，腿脚不便，最近做饭困难，子女在外地，晚上睡不好，希望了解社区有没有方便吃饭的地方。",
        occurred_at=datetime(2026, 6, 20, 9, 0, tzinfo=timezone.utc),
        pii_detected=False,
        source="human",
    )

    resources = [
        Resource(code="R-001", name="和安社区长者饭堂", category="meal", match_codes=["meal"], status="active", region="和安社区"),
        Resource(code="R-003", name="青桥街道社区卫生服务中心", category="medical", match_codes=["medical", "care"], status="active", region="青桥街道"),
        Resource(code="R-005", name="青桥街道志愿者探访队", category="volunteer", match_codes=["volunteer", "care"], status="active", region="青桥街道"),
        Resource(code="R-007", name="青桥街道居家养老服务咨询点", category="care", match_codes=["care", "mobility"], status="active", region="青桥街道"),
        Resource(code="R-024", name="居家安全观察志愿小组", category="care", match_codes=["care", "mobility", "volunteer"], status="active", region="青桥街道"),
    ]

    db.add(client)
    db.add(case)
    db.add(note)
    db.add_all(resources)
    db.commit()
