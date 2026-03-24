---
title: Agent Workflow Factory Tracking Index
created: 2026-03-23
author: AI-assisted
last_updated: 2026-03-23
updated_by: AI-assisted
status: active
---

# Tracking Index

项目内所有复杂任务统一收敛到 `tracking/<task-name>/`。

## 当前任务流

1. `self-bootstrap-v1`
- 状态：in_progress
- 目标：用本项目自己的 loop 思路完成本项目 MVP 开发

2. `v0.2-foundation`
- 状态：completed
- 目标：把 MVP 提升为可长期使用的项目级 AI loop 工具

3. `v0.3-executor-binding`
- 状态：completed
- 目标：让产品能够稳定对接 Cursor / Codex / Claude Code 等 AI 工具

4. `v0.4-executor-runtime`
- 状态：completed
- 目标：让 loop 能真正调用外部 executor，并把执行结果回填到 case 生命周期

5. `v0.5-fine-grained-planning`
- 状态：completed
- 目标：把复杂需求细拆成可独立验收的更小 case，而不是停留在中等粒度模板

6. `v0.6-polish-and-release`
- 状态：completed
- 目标：完成 CLI、README、examples、多 repo 回归与发布收口

## 约定

1. 不在项目根目录直接放 `task_plan.md`、`findings.md`、`progress.md`
2. 每个任务流必须独立维护三件套
3. 任务流完成后保留归档，不覆盖历史
