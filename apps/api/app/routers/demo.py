from fastapi import APIRouter

from app.core.privacy import redact_text
from app.core.resource_match import match_resources

router = APIRouter(prefix="/demo", tags=["demo"])

TAG_CATALOG = {
    "needs": [
        {"code": "meal_difficulty", "match_codes": ["meal"]},
        {"code": "mobility_limited", "match_codes": ["mobility", "care", "medical"]},
        {"code": "living_alone", "match_codes": ["volunteer", "care", "elderly"]},
        {"code": "weak_family_support", "match_codes": ["family", "volunteer", "care"]},
        {"code": "sleep_emotional", "match_codes": ["support", "medical"]},
    ]
}

RESOURCES = [
    {"code": "R-001", "name": "和安社区长者饭堂", "category": "meal", "match_codes": ["meal"], "status": "active"},
    {"code": "R-003", "name": "青桥街道社区卫生服务中心", "category": "medical", "match_codes": ["medical", "care"], "status": "active"},
    {"code": "R-005", "name": "青桥街道志愿者探访队", "category": "volunteer", "match_codes": ["volunteer", "care"], "status": "active"},
    {"code": "R-007", "name": "青桥街道居家养老服务咨询点", "category": "care", "match_codes": ["care", "mobility"], "status": "active"},
]


@router.get("/client-c0001")
def get_demo_client() -> dict:
    return {
        "code": "C-0001",
        "display_name": "独居老人 C-0001",
        "age": 78,
        "community": "和安社区",
        "primary_concern": "餐食困难、行动不便、家庭支持不足、睡眠不好",
        "tags": ["meal_difficulty", "mobility_limited", "living_alone", "weak_family_support", "sleep_emotional"],
    }


@router.post("/redact")
def demo_redact(payload: dict) -> dict:
    result = redact_text(str(payload.get("text", "")))
    return {
        "clean_text": result.clean_text,
        "pii_hits": result.pii_hits,
        "is_safe_for_model": result.is_safe_for_model,
    }


@router.post("/match-resources")
def demo_match_resources(payload: dict) -> dict:
    tags = payload.get("need_tag_codes") or []
    return {"candidates": match_resources(tags, RESOURCES, TAG_CATALOG)}
