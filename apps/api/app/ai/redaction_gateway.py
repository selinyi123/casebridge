from dataclasses import dataclass

from app.core.privacy import RedactionResult, redact_text


@dataclass(frozen=True)
class RedactionGateReport:
    blocked: bool
    reason: str | None
    pii_hit_count: int
    residual_findings: list[str]


@dataclass(frozen=True)
class RedactionGateResult:
    clean_text: str
    raw_result: RedactionResult
    report: RedactionGateReport


RESIDUAL_PATTERNS = ["手机号", "电话", "身份证", "银行卡", "真实姓名", "门牌"]


def _has_long_digit_run(text: str) -> bool:
    run = 0
    for char in text:
        if char.isdigit():
            run += 1
            if run >= 11:
                return True
        else:
            run = 0
    return False


def run_redaction_gate(text: str) -> RedactionGateResult:
    result = redact_text(text)
    residuals = [item for item in RESIDUAL_PATTERNS if item in result.clean_text]
    if _has_long_digit_run(result.clean_text):
        residuals.append("long_digit_run")
    blocked = bool(residuals) or not result.is_safe_for_model
    reason = "residual_sensitive_content" if residuals else None
    return RedactionGateResult(
        clean_text=result.clean_text,
        raw_result=result,
        report=RedactionGateReport(
            blocked=blocked,
            reason=reason,
            pii_hit_count=len(result.pii_hits),
            residual_findings=residuals,
        ),
    )
