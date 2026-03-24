---
title: V0.2 Foundation Progress
created: 2026-03-23
author: AI-assisted
last_updated: 2026-03-23
updated_by: AI-assisted
status: active
---

# V0.2 Foundation Progress

## 2026-03-23

### 已完成

- 新建 `tracking/v0.2-foundation/` 三件套
- 更新 `tracking/index.md`
- 将 v0.2 目标拆成 planner、runner、executor、多 repo 四个方向
- 新增 [v0.2-roadmap.md](/Users/cggg/Documents/private/agent-workflow-factory/docs/v0.2-roadmap.md)
- `planner.py` 已支持基于需求信号生成可变 case 队列
- `loop_cases.json` 新增 `planning_signals`
- `plan` CLI 输出新增 `case_count`
- 完成 planner 差异化 smoke：
  - `uni-box` 首页功能需求 -> 5 cases
  - `chron-matrix` 多 repo loop 重构需求 -> 8 cases
- 修复 `multi_repo` 判定误差，已验证单仓库场景回正
- `loop.py` 已新增 git repo 探测、clean check、pull/push 门禁
- `loop_cases.json` 已新增 `loop_policy`
- `loop_result.schema.json` 已新增 git sync 结果字段
- 完成 loop git smoke：
  - 仅 `tracking/` 变动时允许执行
  - 业务脏文件存在时阻塞执行
  - push 失败时自动插入 `git_sync_recovery`
  - recovery 超过重试上限后自动升级为 `git_sync_manual_intervention`
- 新增 `src/agent_workflow_factory/executor.py`
- 新增 `schemas/executor_request.schema.json`
- `plan` 输出新增 `executor_request_path`
- `tracking/<task-name>/` 现在会生成 `executor_request.json`
- 完成 executor request smoke：
  - `plan` CLI 正确返回 `executor_request_path`
  - 生成结果包含 `supported_adapters` 与 `required_reads`
- 新增 `schemas/runtime_status.schema.json`
- `run-loop` 运行时会持续写入 `.awf/agent_loop_runtime.json`
- 新增 `status` CLI 和 `./start.sh status`
- 完成 runtime status smoke：
  - 运行中返回 `source=runtime`
  - 完成后回退到静态队列视图
- `plan` 现在会额外生成 `handoff_bundle.json`
- 新增 `schemas/handoff_bundle.schema.json`
- 完成 handoff bundle smoke：
  - `plan` CLI 正确返回 bundle 相关文件
  - bundle 内含 `paths`、`adapter_hints`、`executor_request`
- 新增多 repo 示例：
  - `examples/multi-repo-plan-output.example.json`
- README 已同步 handoff bundle 与 `status` 用法
- `v0.2-roadmap.md` 已同步 runtime status 目标
- `requirement_plan.schema.json` 已同步 `handoff_bundle_path`

### 当前状态

- `v0.2 foundation` 已完成

### 下一步

1. 进入下一轮能力增强，优先考虑更细粒度 case 拆解或真实 executor 绑定
2. 如需继续演进，可单独新开 `tracking/v0.3-*` 任务流
