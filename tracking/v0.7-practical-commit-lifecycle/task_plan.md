---
title: V0.7 Practical Commit Lifecycle Task Plan
created: 2026-03-24
author: AI-assisted
last_updated: 2026-03-24
updated_by: AI-assisted
status: active
---

# V0.7 Practical Commit Lifecycle Task Plan

## 任务重述

- 目标：为 `agent-workflow-factory` 补一个够用的 commit lifecycle，让 loop 在 case 成功后可以按配置自动提交
- 作用范围：loop runner、scaffold/workflow 配置、schema、README、tracking
- 关键约束：不做复杂 git 编排；只做最小可用的 `commit` 阶段与状态暴露
- 预期输出：`git_commit_after_case` 配置、`committing` phase、自动 commit、结果回填
- 验收方式：临时 git repo smoke，确认 case 完成后产生提交

## 阶段

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| C1 设计与配置收口 | complete | 已定义最小 commit 生命周期和默认策略 |
| C2 Loop Runner 接入 | complete | 已在成功 case 后增加自动 commit 分支 |
| C3 文档与示例收口 | complete | README 已补 commit lifecycle 说明 |
| C4 验收与提交 | complete | git repo smoke 已通过并完成收口 |

## Case 清单

| Case | 状态 | 说明 | 验收 |
| --- | --- | --- | --- |
| C1.1 定义 commit policy 和 phase | completed | 已明确何时自动 commit、默认消息格式和 `committing` phase | 配置清晰 |
| C2.1 实现自动 commit | completed | case 成功后已可按配置自动提交 | `awf run-loop` smoke |
| C2.2 回填 commit result | completed | loop result 已写入 `commit_created / commit_message` | result 可读 |
| C3.1 README / workflow 示例更新 | completed | 用户可知道如何开启和验证 commit lifecycle | 文档一致 |
| C4.1 git repo smoke 与收口 | completed | 已在全新 scaffold 的临时 git repo 中验证自动 commit 和干净工作树 | smoke 通过 |
