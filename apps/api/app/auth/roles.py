ALLOWED_REVIEWER_ROLES = {"worker", "supervisor", "admin"}
CORRECTION_ROLES = {"supervisor", "admin"}
OUTCOME_REPORT_ROLES = {"worker", "supervisor", "admin"}


def require_role(role: str, allowed: set[str]) -> None:
    if role not in ALLOWED_REVIEWER_ROLES:
        raise ValueError("unknown_reviewer_role")
    if role not in allowed:
        raise PermissionError("role_not_allowed")
