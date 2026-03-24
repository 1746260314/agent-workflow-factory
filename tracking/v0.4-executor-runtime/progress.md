# Progress

## 当前状态

- 当前任务：`v0.4-executor-runtime`
- 当前 case：`C5.1`

## 已完成

- 已建立 v0.4 tracking 基线
- 已确认当前缺口在 executor runtime，而不是 handoff 产物层
- 已新增 `executor_runtime.py`
- 已新增 `schemas/executor_result.schema.json`
- 已为 scaffold/workflow 增加 executor runtime binding 配置
- 已为 planner 输出的 case 增加 `execution_mode=executor`
- 已为 loop 增加 executor 分支与结果回填
- 已新增 `run-executor` CLI 和 `start.sh run-executor`
- 已补 README、architecture、runtime examples

## 验收记录

- `python3 -m py_compile src/agent_workflow_factory/*.py`
- `./start.sh list-adapters`
- `./start.sh run-executor <tmp-project> exec-runtime C1 codex`
- `./start.sh run-loop <tmp-project> <cases_file>`

## 当前结论

- v0.4 代码与文档已收口，下一步是 commit + push，然后进入 v0.5
