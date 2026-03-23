---
title: V0.2 Foundation Task Plan
created: 2026-03-23
author: AI-assisted
last_updated: 2026-03-23
updated_by: AI-assisted
status: active
---

# V0.2 Foundation Task Plan

## 任务重述

- 目标：把 `agent-workflow-factory` 从“主链路可演示的 MVP”推进为“可长期使用的项目级 AI loop 工具”
- 作用范围：planner、loop runner、scaffold、文档、schema、示例
- 关键约束：继续保持人类可读 tracking + 机器可读 schema 并存；每个 case 完成后都要有 smoke 或命令级验收
- 预期输出：更聪明的 planner、更完整的 git/sync runner 骨架、为 AI 执行器接入预留稳定接口
- 验收方式：CLI 可运行，关键能力有 smoke，tracking 持续更新

## 阶段

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| C1 路线图与基线收口 | complete | 已明确 v0.2 目标、边界、里程碑和 case 顺序 |
| C2 Planner 增强 | complete | 已让需求拆解从固定 5-case 升级为按复杂度和项目能力生成 |
| C3 Loop Git/Sync 增强 | complete | 已完成 git pull/push 门禁、sync recovery、人工介入升级链路 |
| C4 AI Executor 接口增强 | pending | 为 Cursor/Codex/Claude Code 等工具提供稳定 handoff 和 executor 接口 |
| C5 多 repo 与示例增强 | pending | 让多 repo/workspace 场景更明确，并补充文档与示例 |

## Case 清单

| Case | 状态 | 说明 | 验收 |
| --- | --- | --- | --- |
| C1.1 输出 v0.2 路线图文档 | completed | 已形成阶段目标、优先级和边界 | 文档落地 |
| C1.2 更新 README 与 tracking 索引 | completed | 已对齐 v0.2 状态和后续方向 | 文档一致 |
| C2.1 定义 planner 输入信号与复杂度规则 | completed | 已设计需求复杂度和 repo 能力驱动拆解逻辑 | 规则落地 |
| C2.2 实现智能 case 生成 MVP | completed | 已让 `plan` 生成可变数量和不同类型的 case，并完成差异化 smoke | `awf plan` smoke |
| C3.1 定义 loop state / sync schema | completed | 已扩充 git/sync 基础状态和 case 生命周期状态 | schema 完整 |
| C3.2 实现 git lifecycle runner MVP | completed | 已为 `run-loop` 引入 clean check、pull/push 门禁，并完成 sync recovery 与人工升级策略 | `awf run-loop` smoke |
| C4.1 定义 executor adapter 接口 | pending | 为 AI 工具执行器预留统一接口 | schema/接口落地 |
| C4.2 生成 AI tool handoff bundle | pending | 输出更完整的 handoff 包而不是单文件 | 示例可用 |
| C5.1 补多 repo 示例 | pending | 使用 workspace 示例验证多 repo 输出 | 示例可读 |
| C5.2 文档与发布收口 | pending | README、架构文档、示例、边界说明同步 | 文档完整 |

## 当前结论

1. v0.2 优先级最高的不是 UI，而是 planner 和 loop 的可用性增强
2. 当前最应该先做的是把“进一步优化开发”的目标明确落成路线图，避免后续实现发散
3. `plan` 已从固定 5-case 模板升级为基于需求信号的可变 case 队列
4. `run-loop` 已具备最小 git 生命周期：
   - clean check
   - 可选 `pull --ff-only`
   - 可选 `push`
   - 失败时写入 `sync_pending` / `blocked`
   - 自动插入 `git_sync_recovery`
   - 超过重试上限后升级为 `git_sync_manual_intervention`
