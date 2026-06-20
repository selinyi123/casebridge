# CaseBridge 案桥

> AI-Native 中国社工个案服务与资源协同系统
> 面向中国社会工作场景的 AI 个案管理、资源链接、督导复盘与成效追踪平台。

围绕服务对象的连续支持过程，整合个案管理、需求评估、资源协同、服务计划、转介跟踪、督导复盘和成效追踪——让社工从零散记录和经验判断，升级为可持续、可协同、可复盘的专业服务流程。

**第一性原理：社工如何更好地服务人。** AI 辅助，不替代；最终判断与责任属于社工。

---

## ⚠️ 开发铁律（先读这一段）

1. **先文档，后代码。** 开发顺序固定：`docs/product/prd.md` → `docs/architecture/schema.md` → `docs/ai/ai-rules.md` → `docs/privacy/privacy-design.md` → 代码。
2. **没有业务闭环，不接 AI。** Phase 1 只做业务骨架，不调任何模型。
3. **AI 输出只进 `ai_outputs`，经人工确认才能落到正式表。** 任何让 AI 直接写业务表的代码路径都是违规。
4. **隐私从第一天内建。** 模型只见脱敏后文本；真实 PII 不进开发与演示。
5. **AI 是增强，不是依赖项。** AI 全部失败时，社工必须能纯手写完成全部流程。

---

## 项目文档（项目宪法）

| 文档 | 作用 |
| --- | --- |
| [`docs/product/prd.md`](docs/product/prd.md) | 做什么 / 不做什么 / MVP 范围 / 验收标准 |
| [`docs/architecture/schema.md`](docs/architecture/schema.md) | 数据模型 / 系统架构 / 状态机 / API 约定 |
| [`docs/ai/ai-rules.md`](docs/ai/ai-rules.md) | AI 能力红线 / 8 能力输出 Schema / 人工确认门禁 |
| [`docs/privacy/privacy-design.md`](docs/privacy/privacy-design.md) | PIPL 对齐 / PII 脱敏 / RBAC / 审计 / 同意管理 |

四份文档互相引用、共同构成约束。**与文档冲突时，先改文档，再写代码。**

---

## MVP：独居老人个案服务闭环

只做一个强闭环，不做大平台。场景：青桥街道社工站，服务对象 C-0001（78 岁独居老人）。

跑通 9 步：建档 → 走访记录 → AI 提取需求/风险 → AI 提示遗漏 → 资源匹配 → 服务计划草稿 → 转介状态 → 督导式复盘 → 成效追踪。

完整演示流见 [`prd.md` §6.4](docs/product/prd.md)。

---

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Next.js + Tailwind + shadcn/ui |
| 后端 | FastAPI |
| 数据库 | PostgreSQL（+ pgvector 可选） |
| 缓存/队列 | Redis |
| 文件存储 | MinIO |
| AI 模型 | DeepSeek / 通义 / 豆包 / OpenAI 可替换 |
| 部署 | Docker Compose |
| 鉴权 | JWT + RBAC |

---

## 开发阶段

| Phase | 产出 | 接 AI |
| --- | --- | --- |
| 0 准备 | 仓库 + 4 文档 + 10 虚拟案例 + 30 资源 | — |
| 1 业务骨架 | 登录 / clients / cases / case_notes / 时间线 / 资源库 CRUD | ❌ |
| 2 AI 结构化 | 走访 → 结构化需求 JSON（入 `ai_outputs`） | ✅ |
| 3 资源匹配 | 标签规则 + AI 推荐理由 + 转介状态 | ✅ |
| 4 服务计划 | AI 计划草稿 + 人工确认 + 跟进待办 | ✅ |
| 5 督导复盘 | AI 督导式问题 + 伦理/缺失提示 | ✅ |
| 6 成效追踪 | 目标变化 / 资源结果 / 回访 / 结案摘要 | ✅ |
| 7 演示打磨 | 看板 / 完整案例 / 假数据 / UI / 路演 | — |

---

## 给 AI 编程工具的系统提示（每次开发带上）

> 你是我的高级全栈工程师。请严格根据 `docs/product/prd.md` 和 `docs/architecture/schema.md` 开发。
> 不得新增未定义功能。不得绕过 RBAC。
> 不得让 AI 输出直接写入正式业务字段；所有 AI 输出必须先进入 `ai_outputs` 表，等待人工确认。
> 遵守 `docs/privacy/privacy-design.md` 的脱敏与审计要求。
> 每次只完成一个小任务，完成后回答 5 个验收问题（是否进入闭环 / 是否保护隐私 / 是否保留人工确认 / 是否能演示 / 是否符合社工逻辑）。

---

## 当前状态

- [x] Phase 0 文档：PRD / schema / ai-rules / privacy-design 已完成
- [ ] Phase 0 数据：10 虚拟案例 + 30 社区资源（待生成）
- [ ] Phase 0 工程：仓库结构 / Docker Compose（待初始化）
- [ ] Phase 1 业务骨架（待开发）

> **下一步**：先生成演示用虚拟数据（10 案例 + 30 资源），再初始化仓库与 Docker Compose，然后进入 Phase 1 业务骨架。
