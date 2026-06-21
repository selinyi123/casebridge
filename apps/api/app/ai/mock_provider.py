from app.schemas import IntakeDraftOutput


def generate_intake_draft(clean_text: str) -> IntakeDraftOutput:
    """Deterministic mock provider for v0.1.6.

    No external model is called. The function produces a conservative draft from
    simple keyword cues and exists only to test the review gate.
    """
    needs: list[str] = []
    risk_clues: list[str] = []
    strengths: list[str] = []
    missing_info = ["是否记录服务对象本人意愿", "是否记录紧急联系人", "是否核实可用资源条件"]
    suggested_next_steps = ["人工复核需求线索", "确认是否同意资源链接", "补充跟进计划"]

    if "做饭" in clean_text or "吃饭" in clean_text or "餐" in clean_text:
        needs.append("餐食支持")
    if "腿脚" in clean_text or "行动" in clean_text:
        needs.append("行动与居家安全关注")
        risk_clues.append("行动不便线索")
    if "独居" in clean_text:
        risk_clues.append("独居线索")
    if "希望" in clean_text or "想" in clean_text:
        strengths.append("能主动表达需求")

    return IntakeDraftOutput(
        needs=needs or ["待人工判断的支持需求"],
        risk_clues=risk_clues,
        strengths=strengths,
        missing_info=missing_info,
        suggested_next_steps=suggested_next_steps,
    )
