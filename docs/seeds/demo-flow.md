# C-0001 Demo Flow — 独居老人个案服务闭环

> This is the canonical demo flow for v0.1.x. It uses only synthetic data.

## Scenario

- Station: 青桥街道社工站
- Community: 和安社区
- Client: C-0001
- Type: elderly living alone
- Main concerns: meal difficulty, mobility limitation, weak family support, sleep/emotional concern

## Initial visit note

```text
今天入户走访 C-0001，老人 78 岁，独居，腿脚不便，最近做饭困难，子女在外地，晚上睡不好，希望了解社区有没有方便吃饭的地方。
```

## 9-step acceptance flow

### 1. Create client profile

Expected fields:

- code: C-0001
- display name: 独居老人 C-0001
- community: 和安社区
- client type: elderly_alone
- consent status: oral

### 2. Add visit note

Add the initial visit note as `case_notes.content_raw`.

Expected system behavior:

- keep raw note unchanged
- create `content_clean` after privacy redaction
- mark `pii_detected=false` for the provided synthetic text

### 3. AI intake analysis

Expected draft output:

```json
{
  "needs": ["餐食支持", "居家安全", "家庭支持不足"],
  "risk_clues": ["独居", "行动不便"],
  "strengths": ["主动表达需求", "仍有子女关系"],
  "missing_info": ["是否有慢病", "是否有紧急联系人", "是否同意转介"],
  "suggested_next_steps": ["核实长者饭堂条件", "评估居家安全", "确认志愿者探访意愿"],
  "need_tag_codes": ["meal_difficulty", "mobility_limited", "living_alone"],
  "confidence": "medium",
  "disclaimer": "AI 生成草稿，需要社工人工确认"
}
```

System rule:

- result enters `ai_outputs.review_status=pending`
- no formal assessment is created before human review

### 4. Assessment omission check

Expected reminders:

- missing medical/basic health follow-up information
- missing emergency contact
- missing client consent for referrals
- missing community resource verification
- missing home safety observation

### 5. Resource matching

Expected candidates:

- R-001 和安社区长者饭堂
- R-003 青桥街道社区卫生服务中心
- R-005 青桥街道志愿者探访队
- R-007 青桥街道居家养老服务咨询点
- R-024 居家安全观察志愿小组

System rule:

- resources are selected by tag rules
- AI may draft match reasons only
- case_referrals are created only after human confirmation

### 6. Service plan draft

Expected plan:

- goal: lower meal and home-care risks for C-0001
- short-term: verify meal-service eligibility within 7 days
- mid-term: connect community health service within 14 days
- long-term: establish weekly volunteer visit within 30 days
- review_required: true

### 7. Referral status

Initial referrals:

- R-001: to_verify
- R-003: to_verify
- R-005: to_verify

State rule:

- `client_consent` must be recorded before advancing beyond verification/contact steps.

### 8. Supervision review

Expected questions:

- 是否记录了老人本人对长者饭堂的真实意愿？
- 是否过早把“睡不好”解释为心理问题？
- 是否评估了居家跌倒风险？
- 是否考虑了家庭支持系统？
- 当前服务目标是否可衡量？

### 9. Outcome tracking

Initial metrics:

| Metric | Initial | Target |
| --- | --- | --- |
| 餐食困难 | 明显 | 已链接助餐资源 |
| 独居照护风险 | 需关注 | 已建立探访机制 |
| 健康随访 | 未确认 | 已联系社区卫生服务中心 |
| 家庭支持 | 较弱 | 完成支持系统核实 |

## Demo success criteria

- The whole flow can be completed without AI.
- AI output is available only as draft.
- Human confirmation is required before formal records change.
- Resource matching is explainable through tags.
- All records remain synthetic and privacy-safe.
