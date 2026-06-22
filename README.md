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
| [`docs/development/v0.1.14-checklist.md`](docs/development/v0.1.14-checklist.md) | v0.1.14 supervisor review 验收清单 |
| [`docs/development/v0.1.15-checklist.md`](docs/development/v0.1.15-checklist.md) | v0.1.15 closure draft report 验收清单 |

---

## MVP

场景：青桥街道社工站，服务对象 C-0001（78 岁独居老人）。

闭环：建档 → 走访记录 → AI 草稿 → 人工审核 → 显式应用到正式评估 → 评估版本 → 服务计划 → 介入记录 → 手动成效记录 → 证据链事件 → 督导复盘 → 结案准备度支持 → 结案草稿报告。

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
- [x] v0.1.11 assessment correction audit / reviewer role guard / outcome report
- [x] v0.1.12 assessment version table / API / version view
- [x] v0.1.12.1 version timeline integration / admin create view / repository test
- [x] v0.1.13 service plan / intervention / evidence chain
- [x] v0.1.13.1 evidence-chain events / plan create UI / intervention create UI
- [x] v0.1.14 supervisor review / closure readiness support
- [x] v0.1.15 closure draft / closure support report
- [ ] CI 结果待确认
- [ ] 下一节点：exportable review report / case closure state machine
