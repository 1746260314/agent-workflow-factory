---
title: V0.5 Fine Grained Planning Task Plan
created: 2026-03-24
author: AI-assisted
last_updated: 2026-03-24
updated_by: AI-assisted
status: active
---

# V0.5 Fine Grained Planning Task Plan

## 任务重述

- 目标：把 `planner` 从“中等粒度 case 生成器”升级为“能把复杂需求持续细拆到可独立验收最小 case”的规划器
- 作用范围：planning signals、任务分层、case 粒度规则、schema、examples、README
- 关键约束：每个 case 必须有单一职责、可执行、可验收
- 预期输出：更细粒度的自动拆解策略和对应示例
- 验收方式：复杂需求生成 `10+` 小 case 的 smoke 与示例

## 阶段

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| C1 粒度原则收口 | pending | 明确 case 最小颗粒度和拆解规则 |
| C2 Planner 分层拆解 | pending | 支持阶段 -> 子 case 的分层生成 |
| C3 示例与文档增强 | pending | 补复杂需求的输出示例与 README |
| C4 验收与收口 | pending | 完成 smoke、tracking 和提交 |
