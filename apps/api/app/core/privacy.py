from dataclasses import dataclass


@dataclass(frozen=True)
class RedactionResult:
    clean_text: str
    pii_hits: list[dict[str, str]]
    is_safe_for_model: bool


def redact_text(text: str) -> RedactionResult:
    """Minimal MVP redactor.

    This intentionally starts conservative and simple for synthetic data.
    Production use must replace this with a formal privacy service.
    """
    clean = text
    hits: list[dict[str, str]] = []

    replacements = {
        "手机号": "[REDACTED_PHONE_LABEL]",
        "身份证": "[REDACTED_ID_LABEL]",
        "门牌": "[REDACTED_ADDR_LABEL]",
        "真实姓名": "[REDACTED_NAME_LABEL]",
    }

    for key, value in replacements.items():
        if key in clean:
            clean = clean.replace(key, value)
            hits.append({"type": key, "action": "masked"})

    return RedactionResult(clean_text=clean, pii_hits=hits, is_safe_for_model=True)
