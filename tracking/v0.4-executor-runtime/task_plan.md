---
title: V0.4 Executor Runtime Task Plan
created: 2026-03-24
author: AI-assisted
last_updated: 2026-03-24
updated_by: AI-assisted
status: active
---

# V0.4 Executor Runtime Task Plan

## 任务重述

- 目标：让 `agent-workflow-factory` 的 loop 不再只会跑 shell commands，而是能按 adapter/runtime 配置真正调用外部 executor，并把结果回填到 case 与 run archive
- 作用范围：executor runtime schema、workflow config、loop runner、CLI、README、examples、tracking
- 关键约束：继续保持通用性，不绑定私有 SDK；先做外部 command binding，再做结果回填
- 预期输出：executor result schema、runtime binding config、loop 中的 executor 分支、最小 smoke
- 验收方式：CLI/loop smoke、schema 完整、tracking 更新、git 提交与 push

## 阶段

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| C1 基线与设计收口 | complete | 已明确 executor runtime 的边界、状态流与配置模型 |
| C2 Schema 与配置落地 | complete | 已补 executor result schema 与 workflow/executor runtime binding 配置 |
| C3 Loop Runtime 接入 | complete | 已在 loop 中增加 executor 分支、结果解析与 case 回填 |
| C4 CLI 与示例增强 | complete | 已补 `run-executor`、README 与 runtime examples |
| C5 验收与发布收口 | complete | smoke、tracking、代码与文档已收口，待 commit + push |

## Case 清单

| Case | 状态 | 说明 | 验收 |
| --- | --- | --- | --- |
| C1.1 收敛 executor runtime 目标与边界 | completed | 已明确 adapter 产物层和 runtime 层之间的职责边界 | 文档一致 |
| C2.1 定义 executor result schema | completed | 已新增 `schemas/executor_result.schema.json` | schema 落地 |
| C2.2 定义 workflow executor binding 配置 | completed | `.awf/workflow.json` 已包含 runtime binding 配置 | 配置可读 |
| C3.1 在 loop 中新增 executor 分支 | completed | `run-loop` 已支持当前 case 通过 executor runtime 执行 | `awf run-loop` smoke |
| C3.2 回填 executor result 到 case 生命周期 | completed | `executor_result` 已映射为 case 完成/阻塞/失败状态 | result smoke |
| C4.1 新增 executor runtime CLI/示例 | completed | 已新增 `run-executor` 与 runtime 示例 | CLI smoke |
| C5.1 README / examples / tracking 收口 | completed | README、examples、tracking 已同步到 v0.4 当前能力 | 文档完整 |

## 当前结论

1. 这一轮已经把 executor 从“handoff 产物层”推进到了“loop runtime 层”
2. 当前 runtime 方案是：
   - workflow 中声明 adapter binding
   - loop 在 executor case 中调用外部 command
   - executor 返回结构化 `executor_result`
   - loop 回填 case 与 run archive
3. 当前仍未做的是私有 SDK 级绑定；现阶段保持外部 command binding 更通用
