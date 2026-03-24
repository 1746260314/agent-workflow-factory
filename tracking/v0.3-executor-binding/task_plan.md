---
title: V0.3 Executor Binding Task Plan
created: 2026-03-24
author: AI-assisted
last_updated: 2026-03-24
updated_by: AI-assisted
status: active
---

# V0.3 Executor Binding Task Plan

## 任务重述

- 目标：让 `agent-workflow-factory` 从“生成 handoff 材料”升级到“能稳定对接不同 AI 编码工具的 executor binding 层”
- 作用范围：executor adapter、CLI、README、架构文档、schema、examples
- 关键约束：先做通用 adapter 层，不直接绑定私有 SDK；所有产物仍保持人类可读和机器可读并存
- 预期输出：adapter registry、adapter-specific handoff 产物、可查询/可渲染的 executor 入口
- 验收方式：CLI smoke、schema 完整、examples 可读

## 阶段

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| C1 基线与设计收口 | complete | 已收敛 executor binding 的目标、边界与当前架构位置 |
| C2 Adapter Registry | complete | 已提供统一 adapter 定义与能力描述 |
| C3 Adapter Artifact 生成 | complete | 已生成面向 Cursor/Codex/Claude Code 的 adapter-specific handoff 产物 |
| C4 CLI 与文档接入 | complete | 已支持查询 adapter、导出对应 handoff |
| C5 示例与发布收口 | complete | README、examples、tracking、架构文档已同步 |

## Case 清单

| Case | 状态 | 说明 | 验收 |
| --- | --- | --- | --- |
| C1.1 新建 v0.3 tracking 与目标说明 | completed | 建立独立任务流与阶段目标 | 文档落地 |
| C1.2 收敛 executor binding 设计边界 | completed | 已明确 adapter 和真实执行器的职责边界 | 文档一致 |
| C2.1 设计 adapter registry schema | completed | 已定义 adapter id、输入格式、输出产物、适配说明 | schema 落地 |
| C2.2 实现 registry 与查询接口 | completed | 已提供代码级 adapter registry 与 `list-adapters` | CLI smoke |
| C3.1 生成 adapter-specific handoff artifact | completed | 已支持 Cursor/Codex/Claude Code 三类输出 | `awf plan` smoke |
| C3.2 扩展 bundle 与 examples | completed | bundle 已显式关联 adapter 产物 | 示例可读 |
| C4.1 新增 executor inspect/render CLI | completed | 已支持查询 adapter、渲染对应 handoff | CLI smoke |
| C5.1 README / architecture 收口 | completed | 产品说明已明确“如何交给不同 AI 工具” | 文档完整 |

## 当前结论

1. 这一轮已经把 executor binding 从概念推进为可用接口：
   - adapter registry
   - adapter-specific handoff
   - `list-adapters`
   - `render-adapter`
2. 当前仍未做的是“真实 SDK / 进程级绑定”，即：
   - 真正调用 Cursor / Codex / Claude Code 执行 case
   - 接收执行结果再回填 loop
