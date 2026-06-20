# CaseBridge 案桥 — 数据模型与系统架构

> 状态：v0.1（对应 PRD v0.1 MVP）
> 用途：本文是 CaseBridge 的数据与架构约束。**所有建表、API、模型代码必须严格遵循本文；新增表/字段前先改本文。**
> 配套阅读：`prd.md`（做什么）、`ai-rules.md`（AI 输出格式）、`privacy-design.md`（脱敏/审计）。

---

## 0. 设计原则

1. **业务闭环优先**：表结构服务于"接案→评估→资源→计划→跟进→转介→督导→成效→结案"主线，不为单点功能建表。
2. **AI 输出隔离**：AI 任何产出只能进 `ai_outputs`，经人工确认后才能落到正式业务表。正式表里不存"AI 原始猜测"。
3. **隐私内建**：涉及 PII 的字段（身份/电话/地址/未成年信息）独立标记并默认脱敏展示。
4. **可追溯**：关键写操作进 `audit_logs`；AI 调用进 `ai_audit_logs`；原始记录不被 AI 摘要覆盖。
5. **MVP 克制**：只建主线必需的表，但所有表预留 `organization_id`、`created_at`、`created_by`、`updated_at`、`updated_by`、`deleted_at`（软删）。

---

## 1. 系统架构

```
Frontend / Next.js (apps/web)
├── Dashboard（工作台）
├── Client Profile（服务对象档案）
├── Case Workspace（个案工作区：走访/计划/跟进）
├── Resource Match（资源匹配）
├── Service Plan（服务计划）
├── Supervision Review（督导复盘）
└── Outcome Tracking（成效追踪）

Backend / FastAPI (apps/api)
├── Auth Service        JWT + RBAC
├── Client Service      服务对象/家庭/标签
├── Case Service        个案/走访/评估/计划/目标/跟进/转介/复盘/成效
├── Resource Service    资源库/分类/联系人
├── Plan Service        服务计划与目标
├── Follow-up Service   跟进与转介状态机
├── AI Service          AI 任务调度 + 结构化输出
├── Audit Service       操作审计
└── Privacy Service     PII 检测/脱敏

Data Layer
├── PostgreSQL          主库（全部业务表）
├── pgvector            （MVP 可选，先标签规则）
├── Redis               缓存 / 任务队列
└── MinIO               文件/附件

AI Kernel（apps/api 内 ai/ 模块）
├── PII Redactor        脱敏前置
├── Prompt Registry     提示词版本管理
├── RAG Retriever       （后续，MVP 用标签）
├── Structured Output Parser   JSON Schema 校验
├── Risk Guard          风险/伦理提示
├── Human Review Gate   人工确认门禁
└── Audit Logger        AI 调用留痕
```

### 1.1 仓库结构

```
casebridge/
├── apps/
│   ├── web/                 # Next.js 前端
│   └── api/                 # FastAPI 后端
│       ├── app/
│       │   ├── models/      # SQLAlchemy 模型（对应本文）
│       │   ├── schemas/     # Pydantic 入参/出参
│       │   ├── routers/     # 路由
│       │   ├── services/    # 业务逻辑
│       │   ├── ai/          # AI Kernel
│       │   └── core/        # 配置/安全/审计
│       └── alembic/         # 数据库迁移
├── docs/
│   ├── product/prd.md
│   ├── architecture/schema.md   ← 本文件
│   ├── ai/ai-rules.md
│   ├── privacy/privacy-design.md
│   └── prompts/             # 提示词模板（版本化）
├── packages/
│   └── shared/              # 前后端共享类型/枚举/标签词表
├── infra/
│   └── docker/              # docker-compose.yml
└── README.md
```

---

## 2. 公共字段约定

所有业务表统一包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | bigint / PK | 主键，自增 |
| `organization_id` | bigint | 预留多租户；MVP 固定单租户 |
| `created_at` | timestamptz | 创建时间 |
| `created_by` | bigint → users.id | 创建人 |
| `updated_at` | timestamptz | 更新时间 |
| `updated_by` | bigint → users.id | 更新人 |
| `deleted_at` | timestamptz, null | 软删除时间 |

枚举与标签词表放在 `packages/shared`，前后端共用，避免魔法字符串。

---

## 3. 数据模型（核心表）

> 下文给出字段语义与关键约束，不写死具体 DDL 语法。建表时以本表为准，迁移用 Alembic 管理。

### 3.1 主体域

#### users
用户（社工 / 管理员）。

| 字段 | 说明 |
| --- | --- |
| id, organization_id | 见公共字段 |
| username | 登录名 |
| email | 邮箱（可空） |
| password_hash | 密码哈希（JWT 鉴权） |
| display_name | 显示名 |
| role | 枚举：`social_worker` / `admin`（MVP）；预留 `supervisor`/`student`/`org_admin` |
| is_active | 是否启用 |
| last_login_at | 最近登录 |

#### roles / user_roles（预留）
MVP 用 `users.role` 单字段即可；V0.3 起切换为 RBAC 表结构。schema 先建 `roles(id, code, name)` 与 `user_roles(user_id, role_id)` 占位，但 MVP 不强制使用。

#### organizations
机构 / 社工站。MVP 一条记录（青桥街道社工站）。

| 字段 | 说明 |
| --- | --- |
| id | |
| name | 如"青桥街道社工站" |
| type | 枚举：`social_work_station` / `agency` / `school` |
| region_code | 行政区划码（预留资源匹配与本地化） |

#### clients（服务对象）
| 字段 | 说明 |
| --- | --- |
| id, organization_id | |
| code | **匿名编号**，如 `C-0001`（MVP 主标识，不存真实姓名为主键） |
| display_name | 显示名（MVP 可为"独居老人 C-0001"，真实姓名默认脱敏） |
| real_name_encrypted | 真实姓名（加密存储，按权限解密；MVP 可留空） |
| age, gender | 年龄/性别 |
| community | 所属社区（文本或关联，如"和安社区"） |
| client_type | 枚举：`elderly_alone` / `child_family` / `disabled` / `new_worker` / `other` |
| household_id | → households.id |
| primary_concern | 主要困境（文本） |
| existing_support | 已有支持（文本） |
| risk_level | **不存 AI 自动评级**；仅存"社工人工填写"的风险提示文本 |
| consent_status | 授权与同意状态枚举：`none`/`oral`/`written`/`expired` |
| tags | → client_tags（多对多，需求/风险/优势标签） |

> **隐私铁律**：`real_name_encrypted`、身份证、手机号、住址等 PII 字段独立存放并默认不返回明文（见 privacy-design.md）。

#### households（家庭）
| 字段 | 说明 |
| --- | --- |
| id | |
| client_id | 主服务对象 |
| structure | 家庭结构（文本/枚举：独居/空巢/单亲/多代同堂…） |
| summary | 家庭关系摘要 |

#### client_tags（标签）
需求/风险/优势/服务对象类型标签，是资源匹配与评估的核心。

| 字段 | 说明 |
| --- | --- |
| id | |
| code | 如 `meal_difficulty`、`mobility_limited`、`living_alone`、`economic_hardship` |
| name | 中文显示名 |
| category | 枚举：`need` / `risk` / `strength` / `demographic` |
| resource_match_codes | **关联到资源的匹配码**（驱动标签规则匹配，见 §6） |

### 3.2 个案域

#### cases（个案主表）
| 字段 | 说明 |
| --- | --- |
| id, organization_id | |
| client_id | → clients.id |
| title | 个案标题 |
| stage | **个案阶段枚举**：`intake`/`assessment`/`planning`/`intervention`/`follow_up`/`evaluation`/`closed`/`followback` |
| status | `open` / `closed` / `suspended` |
| primary_worker_id | → users.id（主责社工） |
| opened_at, closed_at | 接案/结案时间 |

#### case_notes（走访/跟进记录）
| 字段 | 说明 |
| --- | --- |
| id | |
| case_id | → cases.id |
| note_type | 枚举：`intake`/`visit`/`follow_up`/`call`/`home_visit` |
| content_raw | **原始记录**（社工手写，AI 摘要不得覆盖） |
| content_clean | 脱敏后文本（供 AI 分析用） |
| occurred_at | 事件发生时间 |
| pii_detected | bool，是否命中 PII |
| source | `human`（手写）/ `ai_draft_confirmed`（AI 草稿被确认后转入） |

> 原始记录 `content_raw` 永远保留；AI 处理只读 `content_clean`，产出进 `ai_outputs`，确认后才可能沉淀为新的结构化字段，而非改写原文。

#### case_assessments（需求评估）
| 字段 | 说明 |
| --- | --- |
| id | |
| case_id | |
| framework | 评估框架枚举：`ecological_system`（生态系统）/`person_in_environment`/`strength_perspective`… |
| dimensions | JSON：各维度（个人/家庭/社区/政策/优势/伦理）评估内容 |
| missing_dims | JSON：AI 提示的遗漏维度（来自 ai_outputs 确认） |
| confirmed_by | 确认人；未确认为 null |
| confirmed_at | |

#### case_plans（服务计划）
| 字段 | 说明 |
| --- | --- |
| id | |
| case_id | |
| version | 计划版本号（计划可迭代） |
| goal_summary | 总目标 |
| status | `draft`（AI 草稿）/ `confirmed`（社工确认）/ `archived` |
| review_required | 是否需要复核 |
| risk_plan | 风险预案文本 |
| confirmed_by, confirmed_at | |

#### case_goals（服务目标，结构化）
| 字段 | 说明 |
| --- | --- |
| id | |
| plan_id | → case_plans.id |
| horizon | 枚举：`short_term`/`mid_term`/`long_term` |
| description | 目标描述 |
| action_steps | JSON：[{action, deadline_days, owner}] |
| measure | 评估指标 |
| status | `not_started`/`in_progress`/`achieved`/`blocked`/`dropped` |
| linked_resource_ids | 关联资源 |

> 服务计划"可追踪"的核心就在 `case_goals.status` 的变化轨迹（见 §7 状态机）。

#### case_followups（跟进）
| 字段 | 说明 |
| --- | --- |
| id | |
| case_id, goal_id | 可关联目标 |
| due_at | 截止时间 |
| done_at | 完成时间 |
| content | 跟进内容 |
| status | `pending`/`done`/`overdue`/`skipped` |

#### case_referrals（资源转介）
| 字段 | 说明 |
| --- | --- |
| id | |
| case_id | |
| resource_id | → resources.id |
| need_tag_code | 触发转介的需求标签 |
| status | **转介状态机**：`to_verify`/`contacted`/`referred`/`success`/`failed`/`awaiting_callback`/`completed` |
| reason | 转介理由（可来自 AI 推荐，需社工确认） |
| client_consent | 案主是否同意（bool + 说明） |
| result | 结果反馈 |

#### case_reviews（督导复盘）
| 字段 | 说明 |
| --- | --- |
| id | |
| case_id | |
| review_type | `supervision`/`ethics`/`omission_check` |
| questions | JSON：AI 生成的督导式问题（确认后） |
| findings | JSON：遗漏/伦理/缺失提示 |
| reflection | 社工反思文本 |
| reviewer_id | |

#### case_outcomes（成效变化）
| 字段 | 说明 |
| --- | --- |
| id | |
| case_id | |
| goal_id | → case_goals.id |
| metric | 指标名（如"餐食困难""独居风险"） |
| initial_state | 初始状态 |
| current_state | 当前状态 |
| evidence | 证据引用（跟进/转介 id） |
| recorded_at | |

### 3.3 资源域

#### resources
| 字段 | 说明 |
| --- | --- |
| id, organization_id | |
| name | 如"和安社区长者饭堂" |
| category_id | → resource_categories |
| provider_type | 枚举：`civil_affairs`/`disabled_fed`/`women_fed`/`legal_aid`/`health`/`education`/`employment`/`volunteer`/`ngo`/`charity` |
| region_code | 覆盖区域 |
| eligibility | 申请条件（结构化文本） |
| service_scope | 服务边界 |
| match_codes | **匹配码数组**（与 client_tags.resource_match_codes 对应） |
| status | `active`/`inactive` |

#### resource_categories
| 字段 | 说明 |
| --- | --- |
| id | |
| code, name | 如 `meal`（餐食）、`care`（照护）、`medical`（医疗）、`volunteer`（志愿）、`aid`（救助） |

#### resource_contacts
| 字段 | 说明 |
| --- | --- |
| id | |
| resource_id | |
| contact_name | 联系人（脱敏存储） |
| phone_encrypted | 电话（加密） |
| role | 角色 |

### 3.4 AI 域（核心：输出隔离）

#### ai_tasks（AI 任务）
| 字段 | 说明 |
| --- | --- |
| id | |
| case_id / note_id / target_id | 触发上下文 |
| capability | AI 能力枚举：`intake`/`assessment`/`resource_match`/`plan`/`follow_up`/`supervision`/`outcome`/`privacy_redact` |
| status | `pending`/`running`/`succeeded`/`failed` |
| prompt_version | 使用的提示词版本（→ Prompt Registry） |
| model | 模型标识 |
| input_ref | 输入引用（不直接存大文本，存 id；脱敏文本可存 hash） |
| triggered_by | → users.id |
| error | 失败原因 |

#### ai_outputs（AI 输出，**人工确认门禁**）
| 字段 | 说明 |
| --- | --- |
| id | |
| task_id | → ai_tasks.id |
| output_type | 对应 capability |
| payload | **结构化 JSON**（见 ai-rules.md §3 各能力 Schema） |
| review_status | `pending`/`accepted`/`modified`/`rejected` |
| reviewed_by | → users.id |
| reviewed_at | |
| applied_to | 被应用到哪张正式表/记录（确认后才填） |
| disclaimer | 免责声明（"AI 生成草稿，需社工人工确认"） |

> **AI 不能跳过此表直接写业务表。** 任何想把 AI 结果写进 `case_assessments`/`case_plans` 等的操作，必须先在 `ai_outputs` 标记 `accepted`，再由服务层搬运并记录 `applied_to`。

#### ai_audit_logs（AI 调用审计）
| 字段 | 说明 |
| --- | --- |
| id | |
| task_id | |
| user_id | |
| model | |
| prompt_hash | 提示词哈希 |
| input_pii_redacted | bool，输入是否已脱敏 |
| tokens_in, tokens_out | |
| latency_ms | |
| request_at, response_at | |
| error | |

### 3.5 审计域

#### audit_logs（操作审计）
| 字段 | 说明 |
| --- | --- |
| id | |
| user_id | |
| action | 如 `view_client`/`export`/`update`/`confirm_ai_output` |
| entity_type, entity_id | 操作对象 |
| detail | JSON |
| ip, user_agent | |
| created_at | |

> 看 / 改 / 导出 / 确认 AI 草稿均留痕。

---

## 4. 标签词表（资源匹配的基础，MVP 用标签规则）

MVP 不上向量检索，靠"需求标签 ↔ 资源匹配码"映射：

| 需求标签 code | 名称 | 匹配资源 category / match_code |
| --- | --- | --- |
| `meal_difficulty` | 餐食困难 | `meal`（长者饭堂） |
| `mobility_limited` | 行动不便 | `medical`（社区卫生服务中心）/ `care`（居家养老） |
| `living_alone` | 独居 | `volunteer`（志愿者探访） |
| `economic_hardship` | 经济困难 | `aid`（临时救助 / 慈善） |
| `sleep_emotional` | 睡眠/情绪关注 | `medical` / `psychological` |
| `weak_family_support` | 家庭支持弱 | `volunteer` / `care` |

标签词表维护在 `packages/shared/tags.ts`（前端）与 `apps/api/app/core/tag_catalog.py`（后端），单一事实源。

---

## 5. 个案阶段状态机

```
intake → assessment → planning → intervention → follow_up → evaluation → closed
                                                            ↑                ↓
                                                         followback ←──────┘
```

- `stage` 推进由社工操作触发；AI 可在"评估/计划/督导"节点给出建议，但**不能自动推进阶段**。
- 结案 `closed` 后可进入 `followback`（回访）。

---

## 6. 资源匹配流程（标签规则版）

```
case_note → AI Intake → 需求标签(needs[]) → 匹配 client_tags.resource_match_codes
        → 在 resources.match_codes 中检索 → 返回候选资源 + 匹配理由(可 AI 润色)
        → 社工选择 → 生成 case_referrals(status=to_verify, client_consent=null)
```

- 匹配理由可由 AI 生成，但作为 `ai_outputs.payload`，经确认才展示为"正式推荐理由"。
- 转介默认 `client_consent=null`，**必须社工核实案主意愿后才能推进状态**。

---

## 7. 关键状态机汇总

### 7.1 服务目标 case_goals.status
`not_started → in_progress → achieved | blocked | dropped`

### 7.2 转介 case_referrals.status
`to_verify → contacted → referred → success | failed → awaiting_callback → completed`

### 7.3 AI 输出 ai_outputs.review_status
`pending → accepted | modified | rejected`（modified = 社工改后接受）

### 7.4 计划 case_plans.status
`draft → confirmed → archived`（新版本出现时旧版本 archived）

---

## 8. API 设计约定（摘要）

- RESTful，前缀 `/api/v1/`。
- 所有写操作需 JWT；按 `users.role` 做最小权限校验。
- AI 相关接口：
  - `POST /api/v1/ai/intake` 入参 note_id，创建 ai_task，返回 task_id
  - `GET /api/v1/ai/tasks/{id}` 查询状态与输出
  - `POST /api/v1/ai/outputs/{id}/review` `{action: accept|modify|reject, payload?}` 人工确认
- PII 字段在响应中默认脱敏；`?include_pii=true` 需更高权限（MVP 仅 admin）。
- 列表接口统一分页 `page/page_size`，排序 `sort`。

---

## 9. 迁移与种子数据

- 迁移：Alembic，每次 schema 变更生成新 revision，禁止手改库。
- 种子数据（演示用）：
  - 1 个 organization（青桥街道社工站）
  - 2 个 user（1 social_worker + 1 admin）
  - 10 个 clients（C-0001~C-0010，独居老人为主）
  - 30 条 resources（长者饭堂/卫生中心/志愿者/救助/慈善/法律…）
  - C-0001 的完整闭环数据：走访记录、评估、计划、目标、跟进、转介、复盘、成效
- **所有种子数据禁止包含真实 PII**。

---

## 10. 变更记录

| 版本 | 日期 | 变更 |
| --- | --- | --- |
| v0.1 | 2026-06-20 | 首版数据模型与架构：主体/个案/资源/AI/审计五域，AI 输出隔离门禁，标签规则匹配 |
