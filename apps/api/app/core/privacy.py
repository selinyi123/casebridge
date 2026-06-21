import re
from dataclasses import dataclass
from enum import Enum


class Sensitivity(str, Enum):
    PHONE = "phone"
    ID_NUMBER = "id_number"
    BANK_CARD = "bank_card"
    ADDRESS_DETAIL = "address_detail"
    MINOR = "minor"
    DIAGNOSIS = "diagnosis_or_health"
    SENSITIVE_LABEL = "sensitive_label"


SENSITIVE_LABELS = {
    "手机号": "[REDACTED_PHONE_LABEL]",
    "电话": "[REDACTED_PHONE_LABEL]",
    "身份证": "[REDACTED_ID_LABEL]",
    "门牌": "[REDACTED_ADDR_LABEL]",
    "真实姓名": "[REDACTED_NAME_LABEL]",
    "银行卡": "[REDACTED_BANK_LABEL]",
}

PATTERN_RULES: list[tuple[Sensitivity, re.Pattern[str], str]] = [
    (Sensitivity.PHONE, re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "[REDACTED_PHONE]"),
    (Sensitivity.ID_NUMBER, re.compile(r"(?<![0-9A-Za-z])\d{17}[0-9Xx](?![0-9A-Za-z])"), "[REDACTED_ID]"),
    (Sensitivity.ID_NUMBER, re.compile(r"(?<!\d)\d{15}(?!\d)"), "[REDACTED_ID]"),
    (Sensitivity.BANK_CARD, re.compile(r"(?<!\d)(?:\d[ -]?){16,19}(?!\d)"), "[REDACTED_BANK_CARD]"),
    (Sensitivity.ADDRESS_DETAIL, re.compile(r"[^，。；;\n]{0,24}(?:路|街|巷|弄|小区|社区|村|镇|区)[^，。；;\n]{0,24}(?:\d+号|\d+栋|\d+单元|\d+室|门牌[^，。；;\n]*)"), "[REDACTED_ADDR]"),
]

MINOR_PATTERNS = [
    re.compile(r"(?:\b|[^0-9])(?:[1-9]|1[0-3])岁"),
    re.compile(r"不满十四周岁"),
    re.compile(r"未成年人|儿童|小学生|幼儿"),
]

DIAGNOSIS_PATTERNS = [
    re.compile(r"诊断为[^，。；;\n]{1,30}"),
    re.compile(r"确诊[^，。；;\n]{1,30}"),
    re.compile(r"残疾证号|精神障碍|抑郁症|癌症|慢病|高血压|糖尿病"),
]


@dataclass(frozen=True)
class RedactionResult:
    clean_text: str
    pii_hits: list[dict[str, str]]
    is_safe_for_model: bool


def _mask_sensitive_labels(text: str) -> tuple[str, list[dict[str, str]]]:
    clean = text
    hits: list[dict[str, str]] = []
    for label, replacement in SENSITIVE_LABELS.items():
        if label in clean:
            clean = clean.replace(label, replacement)
            hits.append({"type": Sensitivity.SENSITIVE_LABEL.value, "label": label, "action": "masked_label"})
    return clean, hits


def _mask_patterns(text: str) -> tuple[str, list[dict[str, str]]]:
    clean = text
    hits: list[dict[str, str]] = []
    for sensitivity, pattern, replacement in PATTERN_RULES:
        clean, count = pattern.subn(replacement, clean)
        if count:
            hits.append({"type": sensitivity.value, "action": "masked_regex", "count": str(count)})
    return clean, hits


def _detect_blocking_sensitivity(text: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for pattern in MINOR_PATTERNS:
        if pattern.search(text):
            hits.append({"type": Sensitivity.MINOR.value, "action": "blocked_for_model"})
            break
    for pattern in DIAGNOSIS_PATTERNS:
        if pattern.search(text):
            hits.append({"type": Sensitivity.DIAGNOSIS.value, "action": "blocked_for_model"})
            break
    return hits


def _has_residual_high_risk_identifier(text: str) -> bool:
    return any(pattern.search(text) for _, pattern, _ in PATTERN_RULES)


def redact_text(text: str) -> RedactionResult:
    """Rule-based MVP+ redactor for synthetic-demo development.

    This is still not a production DLP engine. It now masks common structured PII
    and blocks model calls when the note contains minor or health/diagnosis clues
    that require a stricter review path before any AI processing.
    """
    clean, label_hits = _mask_sensitive_labels(text)
    clean, pattern_hits = _mask_patterns(clean)
    blocking_hits = _detect_blocking_sensitivity(clean)
    hits = label_hits + pattern_hits + blocking_hits
    is_safe_for_model = not blocking_hits and not _has_residual_high_risk_identifier(clean)
    return RedactionResult(clean_text=clean, pii_hits=hits, is_safe_for_model=is_safe_for_model)
