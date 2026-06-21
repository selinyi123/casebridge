from dataclasses import dataclass

SENSITIVE_LABELS = {
    "手机号": "[REDACTED_PHONE_LABEL]",
    "电话": "[REDACTED_PHONE_LABEL]",
    "身份证": "[REDACTED_ID_LABEL]",
    "门牌": "[REDACTED_ADDR_LABEL]",
    "真实姓名": "[REDACTED_NAME_LABEL]",
    "银行卡": "[REDACTED_BANK_LABEL]",
}


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
            hits.append({"type": label, "action": "masked_label"})
    return clean, hits


def _mask_digit_runs(text: str) -> tuple[str, list[dict[str, str]]]:
    """Mask long digit-like runs without regular expressions.

    This is intentionally conservative for MVP. It reduces obvious leakage in demo text
    while leaving production-grade de-identification to a later Presidio-style service.
    """
    chars = list(text)
    hits: list[dict[str, str]] = []
    start: int | None = None

    def flush(end: int) -> None:
        nonlocal start
        if start is None:
            return
        raw = "".join(chars[start:end])
        digit_count = sum(1 for c in raw if c.isdigit())
        replacement: str | None = None
        hit_type: str | None = None
        if digit_count >= 18:
            replacement = "[REDACTED_LONG_ID]"
            hit_type = "long_digit_id"
        elif digit_count >= 15:
            replacement = "[REDACTED_ID]"
            hit_type = "id_number"
        elif digit_count >= 11:
            replacement = "[REDACTED_PHONE]"
            hit_type = "phone"
        if replacement and hit_type:
            chars[start:end] = list(replacement) + [""] * (end - start - len(replacement))
            hits.append({"type": hit_type, "action": "masked_digits"})
        start = None

    for index, char in enumerate(chars):
        if char.isdigit() or char in {"X", "x", "-", " "}:
            if start is None:
                start = index
        else:
            flush(index)
    flush(len(chars))

    return "".join(chars), hits


def redact_text(text: str) -> RedactionResult:
    """MVP privacy redactor.

    This function is not production DLP. It is a local baseline that prevents
    obvious sensitive labels and long digit-like identifiers from entering future
    model calls during synthetic-demo development.
    """
    clean, label_hits = _mask_sensitive_labels(text)
    clean, digit_hits = _mask_digit_runs(clean)
    hits = label_hits + digit_hits
    return RedactionResult(clean_text=clean, pii_hits=hits, is_safe_for_model=True)
