# CaseBridge 案桥

> AI-Native 中国社工个案服务与资源协同系统。

围绕服务对象的连续支持过程，整合个案管理、需求评估、资源协同、服务计划、转介跟踪、督导复盘和成效追踪。AI 辅助，不替代；最终判断与责任属于社工。

---

## 开发铁律

1. 先文档，后代码。
2. 没有业务闭环，不接 AI。
3. AI 输出只进 `ai_outputs`，经人工确认才能进入后续流程。
4. 隐私从第一天内建。
5. AI 全部失败时，社工仍能手动完成流程。

---

## 项目文档

| 文档 | 作用 |
| --- | --- |
| [`docs/product/prd.md`](docs/product/prd.md) | 产品范围与验收标准 |
| [`docs/product/version-roadmap.md`](docs/product/version-roadmap.md) | 版本路线 |
| [`docs/product/v0.1.8-plan.md`](docs/product/v0.1.8-plan.md) | Review apply workflow 规划 |
| [`docs/product/v0.1.9-plan.md`](docs/product/v0.1.9-plan.md) | Formal assessment target 规划 |
| [`docs/product/v0.1.10-plan.md`](docs/product/v0.1.10-plan.md) | Assessment schema and outcome tracking 规划 |
| [`docs/architecture/schema.md`](docs/architecture/schema.md) | 数据模型与 API 约定 |
| [`docs/ai/ai-rules.md`](docs/ai/ai-rules.md) | AI 能力红线 |
| [`docs/privacy/privacy-design.md`](docs/privacy/privacy-design.md) | 隐私与审计设计 |
| [`docs/research/iteration-012.md`](docs/research/iteration-012.md) | assessment schema / outcome tracking 调研 |
| [`docs/development/v0.1.10-checklist.md`](docs/development/v0.1.10-checklist.md) | v0.1.10 outcome tracking 验收清单 |

---

## MVP

场景：青桥街道社工站，服务对象 C-0001（78 岁独居老人）。

闭环：建档 → 走访记录 → AI 草稿 → 人工审核 → 显式应用到正式评估 → 服务目标 → 手动成效记录 → 资源链接 → 督导复盘。

---

## 当前状态

- [x] v0.1.1 foundation-build
- [x] v0.1.2 business skeleton + hardening
- [x] v0.1.3 persistence foundation + UI workspace
- [x] v0.1.4 manual goal/link gate
- [x] v0.1.5 timeline/audit + web timeline page
- [x] v0.1.6 AI intake gate
- [x] v0.1.7 provider/prompt gate
- [x] v0.1.8 redaction gateway / golden fixture / apply preview
- [x] v0.1.9 formal assessment target / explicit apply workflow
- [x] v0.1.10 manual outcome tracking
- [x] v0.1.10.2 stabilization: outcome migration, timeline integration, schema access alias
- [ ] CI 结果待确认
- [ ] 下一节点：assessment versioning / RBAC reviewer role / outcome report view
