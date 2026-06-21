from datetime import datetime, timezone
from itertools import count
from typing import Any

CLIENTS: dict[str, dict[str, Any]] = {
    "C-0001": {
        "code": "C-0001",
        "display_name": "独居老人 C-0001",
        "age": 78,
        "gender": "female",
        "community": "和安社区",
        "client_type": "elderly_alone",
        "primary_concern": "餐食困难、行动不便、家庭支持不足、睡眠不好",
        "existing_support": "邻里偶尔关照，暂无固定探访机制",
        "consent_status": "oral",
        "tags": [
            "meal_difficulty",
            "mobility_limited",
            "living_alone",
            "weak_family_support",
            "sleep_emotional",
        ],
    }
}

CASES: dict[str, dict[str, Any]] = {
    "CASE-0001": {
        "id": "CASE-0001",
        "client_code": "C-0001",
        "title": "C-0001 独居老人支持个案",
        "stage": "intake",
        "status": "open",
        "primary_worker": "demo_social_worker",
        "opened_at": "2026-06-20T00:00:00Z",
    }
}

NOTE_COUNTER = count(2)
CASE_NOTES: dict[str, list[dict[str, Any]]] = {
    "CASE-0001": [
        {
            "id": "NOTE-0001",
            "case_id": "CASE-0001",
            "note_type": "home_visit",
            "content_raw": "今天入户走访 C-0001，老人 78 岁，独居，腿脚不便，最近做饭困难，子女在外地，晚上睡不好，希望了解社区有没有方便吃饭的地方。",
            "content_clean": "今天入户走访 C-0001，老人 78 岁，独居，腿脚不便，最近做饭困难，子女在外地，晚上睡不好，希望了解社区有没有方便吃饭的地方。",
            "occurred_at": "2026-06-20T09:00:00Z",
            "pii_detected": False,
            "source": "human",
        }
    ]
}

RESOURCES: list[dict[str, Any]] = [
    {"code": "R-001", "name": "和安社区长者饭堂", "category": "meal", "match_codes": ["meal"], "status": "active"},
    {"code": "R-003", "name": "青桥街道社区卫生服务中心", "category": "medical", "match_codes": ["medical", "care"], "status": "active"},
    {"code": "R-005", "name": "青桥街道志愿者探访队", "category": "volunteer", "match_codes": ["volunteer", "care"], "status": "active"},
    {"code": "R-007", "name": "青桥街道居家养老服务咨询点", "category": "care", "match_codes": ["care", "mobility"], "status": "active"},
    {"code": "R-024", "name": "居家安全观察志愿小组", "category": "care", "match_codes": ["care", "mobility", "volunteer"], "status": "active"},
]

TAG_CATALOG = {
    "needs": [
        {"code": "meal_difficulty", "match_codes": ["meal"]},
        {"code": "mobility_limited", "match_codes": ["mobility", "care", "medical"]},
        {"code": "living_alone", "match_codes": ["volunteer", "care", "elderly"]},
        {"code": "weak_family_support", "match_codes": ["family", "volunteer", "care"]},
        {"code": "sleep_emotional", "match_codes": ["support", "medical"]},
    ]
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def list_clients() -> list[dict[str, Any]]:
    return list(CLIENTS.values())


def get_client(code: str) -> dict[str, Any] | None:
    return CLIENTS.get(code)


def list_cases(client_code: str | None = None) -> list[dict[str, Any]]:
    rows = list(CASES.values())
    if client_code:
        return [row for row in rows if row.get("client_code") == client_code]
    return rows


def get_case(case_id: str) -> dict[str, Any] | None:
    return CASES.get(case_id)


def list_case_notes(case_id: str) -> list[dict[str, Any]]:
    return CASE_NOTES.get(case_id, [])


def create_case_note(case_id: str, payload: dict[str, Any], content_clean: str, pii_detected: bool) -> dict[str, Any]:
    note_id = f"NOTE-{next(NOTE_COUNTER):04d}"
    note = {
        "id": note_id,
        "case_id": case_id,
        "note_type": payload.get("note_type", "visit"),
        "content_raw": payload.get("content_raw", ""),
        "content_clean": content_clean,
        "occurred_at": payload.get("occurred_at") or utc_now(),
        "pii_detected": pii_detected,
        "source": "human",
    }
    CASE_NOTES.setdefault(case_id, []).append(note)
    return note


def list_resources() -> list[dict[str, Any]]:
    return RESOURCES
