# CaseBridge 案桥 — AI 内核规则

> 状态：v0.1（对应 PRD / schema v0.1）
> 用途：本文定义 AI 在 CaseBridge 中**能做什么、不能做什么、输出长什么样**。所有提示词、AI Service 代码、结构化输出解析必须严格遵循本文。
> 配套：`prd.md`（能力清单）、`schema.md`（ai_outputs/ai_tasks 表）、`privacy-design.md`（脱敏前置）。

---

## 0. 第一原则

> AI 辅助，不替代；AI 提醒，不裁决；AI 生成草稿，不生成事实；AI 推荐资源，不自动转介；AI 质检材料，不做最终判断。

社会工作是专业助人关系，**最终判断、确认、介入和责任属于社工**。AI 的任何产出都是**待确认草稿**。

---

## 1. AI 能做什么 / 不能做什么（红线表）

| 维度 | ✅ AI 可以 | ❌ AI 绝不可以 |
| --- | --- | --- |
| 个案理解 | 从走访文本提取需求/风险/优势/遗漏线索 | 给服务对象下"高危/低危"等定性结论 |
| 评估 | 按社工框架提示遗漏维度 | 替社工完成评估并直接入库 |
| 资源 | 推荐候选资源 + 匹配理由 | 自动发起转介、自动联系资源方或案主 |
| 计划 | 生成结构化服务计划草稿 | 绕过社工确认直接成为正式计划 |
| 跟进 | 提示待办与遗漏跟进 | 自动推进个案阶段或目标状态 |
| 督导 | 生成督导式问题、伦理提示 | 冒充真人督导、给出"对/错"裁决 |
| 成效 | 生成目标变化摘要草稿 | 编造未发生的服务结果 |
| 隐私 | 检测并脱敏 PII | 把原始 PII 明文发给模型或写入审计可见区 |
| 伦理 | 提示标签化/隐私暴露/案主意愿缺失 | 对案主做人格/道德评判 |

### 1.1 表达铁律（prompt 必须内化）

- AI **不得**说："该对象属于高危老人。"
- AI **只能**说："当前记录出现独居、行动不便、家庭支持不足等线索，**建议社工进一步人工核实照护风险**。"
- 所有输出必须带 `disclaimer`：`AI 生成草稿，需要社工人工确认`。
- 涉及风险/诊断/资格判断，一律加"建议人工核实"，不得给确定结论。

---

## 2. AI Kernel 架构（来自 schema.md）

```
请求 → PII Redactor（脱敏前置）
     → Prompt Registry（按 capability 取版本化模板）
     → 模型调用（DeepSeek/通义/豆包/OpenAI 可替换）
     → Structured Output Parser（按 §3 Schema 校验）
     → Risk Guard（伦理/风险/标签化检查）
     → 写入 ai_outputs(review_status=pending)
     → Audit Logger 留痕
     →（等待人工 review: accept/modify/reject）
```

- **脱敏前置**：任何文本进模型前先过 PII Redactor；`input_pii_redacted=false` 的调用直接拒绝并报错。
- **结构化输出**：所有能力返回 JSON，按 §3 的 Schema 校验；解析失败重试 1 次，仍失败则 task 标 `failed` 并提示社工手写。
- **版本化**：每个 capability 的 prompt 在 `docs/prompts/{capability}.md` 有版本号；`ai_tasks.prompt_version` 记录用的是哪版。

---

## 3. 各能力输出 Schema（必须返回结构化 JSON）

> 所有 JSON 都进 `ai_outputs.payload`。`review_status` 默认 `pending`，需社工确认。

### 3.1 intake（接案/走访结构化）

输入：`case_notes.content_clean`（脱敏后走访文本）。

```json
{
  "needs": ["餐食支持", "居家安全", "家庭支持不足"],
  "risk_clues": ["独居", "行动不便"],
  "strengths": ["主动表达需求", "仍有子女关系"],
  "missing_info": ["是否有慢病", "是否有紧急联系人", "是否同意转介"],
  "suggested_next_steps": ["核实长者饭堂条件", "评估居家安全", "确认志愿者探访意愿"],
  "need_tag_codes": ["meal_difficulty", "mobility_limited", "living_alone"],
  "confidence": "low|medium|high",
  "disclaimer": "AI 生成草稿，需要社工人工确认"
}
```

- `need_tag_codes` 必须取自标签词表（schema.md §4），不得自造。
- `confidence` 反映文本信息充分度，不反映风险等级。

### 3.2 assessment（评估遗漏提醒）

输入：个案信息 + 已有评估维度。

```json
{
  "covered_dims": ["personal", "family"],
  "missing_dims": ["community", "policy", "strength", "ethics"],
  "framework": "ecological_system",
  "reminders": [
    "缺少社区层面资源（长者饭堂/卫生服务）的核查",
    "缺少优势视角：老人主动表达需求是优势",
    "缺少伦理边界：是否记录案主对转介的同意"
  ],
  "disclaimer": "AI 生成草稿，需要社工人工确认"
}
```

### 3.3 resource_match（资源推荐理由）

匹配主体由**标签规则**完成（schema.md §6），AI 只负责润色推荐理由与核实提示。

```json
{
  "recommendations": [
    {
      "resource_id": 12,
      "resource_name": "和安社区长者饭堂",
      "match_reason": "餐食困难 + 距离近 + 老人符合年龄条件",
      "to_verify": ["居住地是否在覆盖范围", "申请条件"],
      "need_tag_codes": ["meal_difficulty"]
    }
  ],
  "disclaimer": "AI 生成草稿，需要社工人工确认；转介须案主同意"
}
```

- **不自动创建 case_referrals**；社工确认后才建，且 `client_consent` 默认 null。

### 3.4 plan（服务计划草稿）

输入：评估 + 已选资源。

```json
{
  "goal": "降低独居老人餐食与照护风险",
  "short_term_actions": [
    { "action": "核实长者饭堂申请条件", "deadline_days": 7, "owner": "主责社工" }
  ],
  "mid_term_actions": [
    { "action": "联系社区卫生服务中心进行健康随访建议", "deadline_days": 14, "owner": "主责社工" }
  ],
  "long_term_actions": [
    { "action": "建立每周一次志愿者探访机制", "deadline_days": 30, "owner": "主责社工" }
  ],
  "measure": "餐食稳定、跌倒风险下降、有固定探访",
  "risk_plan": "若老人突发不适，启用紧急联系人 + 社区卫生中心绿色通道",
  "review_required": true,
  "disclaimer": "AI 生成草稿，需要社工人工确认"
}
```

### 3.5 follow_up（跟进提醒）

```json
{
  "todos": [
    { "case_id": 1, "goal_id": 3, "due_at": "2026-06-27", "content": "核实长者饭堂申请条件" }
  ],
  "overdue": [
    { "goal_id": 5, "description": "社区卫生中心联系未完成", "days_overdue": 3 }
  ],
  "disclaimer": "AI 生成草稿，需要社工人工确认"
}
```

### 3.6 supervision（督导式复盘）

输入：个案记录（走访/评估/计划/跟进/转介）。

```json
{
  "questions": [
    "是否记录了老人本人对长者饭堂的真实意愿？",
    "是否过早把'睡不好'解释为心理问题？",
    "是否评估了居家跌倒风险？",
    "是否考虑了家庭支持系统？",
    "当前服务目标是否可衡量？"
  ],
  "omission_checks": [
    "缺少服务对象本人意愿记录",
    "缺少紧急联系人",
    "服务目标不可衡量",
    "转介结果尚未反馈"
  ],
  "ethics_alerts": [
    "存在标签化表达风险：'问题老人'",
    "潜在隐私暴露：记录中出现具体门牌"
  ],
  "disclaimer": "AI 生成草稿，仅供督导式反思，需要社工人工确认"
}
```

- AI **只提问、只提示**，不给"计划是对/错"的裁决。

### 3.7 outcome（成效分析草稿）

```json
{
  "goal_id": 3,
  "changes": [
    { "metric": "餐食困难", "initial": "明显", "current": "已链接长者饭堂", "evidence_ref": "referral_id:7" },
    { "metric": "独居风险", "initial": "较高", "current": "已建立志愿者探访", "evidence_ref": "followup_id:12" }
  ],
  "disclaimer": "AI 生成草稿，需要社工人工确认；不得编造未发生的服务结果"
}
```

### 3.8 privacy_redact（脱敏，调用前置）

```json
{
  "clean_text": "今天入户走访 C-0001，老人 78 岁，独居，腿脚不便……",
  "pii_hits": [
    { "type": "phone", "span": "[REDACTED_PHONE]", "action": "masked" },
    { "type": "address_detail", "span": "[REDACTED_ADDR]", "action": "masked" }
  ],
  "is_safe_for_model": true
}
```

- `is_safe_for_model=false` 时禁止调用模型，要求社工先改写。

---

## 4. 提示词规范（Prompt Registry）

- 每个能力一个文件：`docs/prompts/{capability}.md`，含版本号、System Prompt、变量槽、few-shot。
- System Prompt 必须包含：§1 红线、社工框架引用、输出 Schema 引用、`disclaimer` 要求、不得自造标签码。
- 变量以 `{{变量}}` 标注，注入前必须经过脱敏。
- few-shot 用 C-0001 虚拟案例，**禁止使用真实案例**。

### 4.1 intake 能力 System Prompt 骨架（示例）

```
你是 CaseBridge 的个案理解助手，服务中国社会工作场景。
你的角色：从社工的走访/接案记录中提取结构化线索，供社工复核。
红线：
- 不得给服务对象下风险/诊断/资格定性结论。
- 不得自造 need_tag_codes，只能使用提供的标签词表。
- 所有结论加"建议社工人工核实"。
- 输出必须为指定 JSON，含 disclaimer。
社工框架：人在情境中、生态系统、优势视角、案主自决、个别化。
标签词表：{{tag_catalog}}
走访文本（已脱敏）：{{clean_text}}
请按 Schema 输出。
```

---

## 5. 人工确认门禁（Human Review Gate）

`ai_outputs.review_status` 流转：

```
pending ──accept──► applied_to 填写，结果搬运到正式表
        ├──modify──► 社工改写 payload 后 accept
        └──reject──► 不应用，记录原因
```

- 服务层唯一允许"读 ai_outputs → 写正式表"的入口是 `apply_ai_output(output_id, reviewer_id)`。
- 任何 AI Service 内部**不得持有**直接写 `case_assessments`/`case_plans`/`case_referrals` 的代码路径。
- 应用动作进 `audit_logs`（action=`confirm_ai_output`）。

---

## 6. 安全护栏（Risk Guard）

解析成功后，Risk Guard 对 payload 做规则检查，命中则给 payload 加 `guard_flags` 并降级展示：

- 含确定结论词（"确诊/高危/必须/应当立即"）→ 转为"建议人工核实"并标记。
- 含标签化/歧视表达 → 标 `ethics_alert`。
- 出现疑似未脱敏 PII 残留 → 拒绝输出，task 失败。
- 资源推荐中出现不在 `resources` 表的 id → 丢弃该项。

---

## 7. 模型可替换性

- 通过 `AI_PROVIDER` 环境变量切换（deepseek / qwen / doubao / openai）。
- 统一抽象 `LLMClient.complete(messages, response_format=json)`，各 provider 适配。
- 结构化输出优先用模型的 JSON mode / function calling；不支持则用严格解析 + 重试。
- 严禁把 provider 专属语法写进业务层。

---

## 8. 失败与降级

| 情况 | 处理 |
| --- | --- |
| 脱敏未通过 | 不调用模型，提示社工改写 |
| JSON 解析失败 | 重试 1 次；仍失败 task=failed，提示手写 |
| Risk Guard 命中硬规则 | 拒绝输出，记录原因 |
| 模型超时/错误 | task=failed，前端显示"AI 暂不可用，请手写" |
| 任何 AI 不可用 | **业务闭环不得中断**——社工必须能纯手写完成全部流程 |

> 最后一条是产品底线：AI 是增强，不是依赖项。所有页面在 AI 失败时仍可手工录入。

---

## 9. 与社工专业的绑定（必须落地）

AI 分析独居老人个案时，按社工逻辑分层拆解，而非"老人需要帮助"一句话：

- 个人层面：行动不便、睡眠不好
- 家庭层面：子女在外地，家庭支持弱
- 社区层面：是否有长者饭堂、志愿者探访、社区卫生服务
- 政策层面：是否可链接养老、救助、医疗资源
- 优势视角：老人能主动表达需求，仍有求助意愿
- 伦理边界：是否记录本人意愿、是否同意转介

这套分层对应 `assessment.framework=ecological_system` 的 dimensions 结构，写入 prompt 与 Schema。

---

## 10. 变更记录

| 版本 | 日期 | 变更 |
| --- | --- | --- |
| v0.1 | 2026-06-20 | 首版 AI 规则：红线、8 能力 Schema、人工确认门禁、Risk Guard、可替换模型 |
