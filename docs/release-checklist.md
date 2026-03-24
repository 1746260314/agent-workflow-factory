---
title: Agent Workflow Factory Release Checklist
created: 2026-03-24
author: AI-assisted
last_updated: 2026-03-24
updated_by: AI-assisted
status: active
---

# Release Checklist

## CLI 基线

1. `./start.sh help`
2. `./start.sh scan <workspace>`
3. `./start.sh scaffold <workspace>`
4. `./start.sh plan <project> "<goal>" "<scope>"`
5. `./start.sh list-adapters`
6. `./start.sh render-adapter <bundle_file> codex`
7. `./start.sh status <project> <cases_file>`

## Executor Runtime

1. 为目标项目配置 `.awf/workflow.json` 中的 `executor.runtime.bindings`
2. 准备一个能输出 `executor_result` JSON 的 mock executor
3. 执行：
   - `./start.sh run-executor <project> <task_name> <case_id> <adapter>`
   - `./start.sh run-loop <project> <cases_file>`
4. 确认：
   - case 状态推进
   - `runs/*.result.json` 写入成功
   - `status` 可看到最近结果

## Planner 质量

1. 单 repo 前端需求生成 `6~8` 个 case
2. 多 repo / 高复杂度需求生成 `10+` 个 case
3. case 中应包含：
   - `owner_skill`
   - `depends_on`
   - `acceptance`
   - `write_scope`

## 文档与示例

1. README 与当前 CLI 一致
2. `examples/` 中至少覆盖：
   - multi-repo plan
   - fine-grained plan
   - executor runtime binding
   - executor result

## 发布前最后确认

1. `python3 -m py_compile src/agent_workflow_factory/*.py`
2. `git status` 干净
3. 关键 tracking 已更新
