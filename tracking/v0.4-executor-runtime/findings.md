# Findings

## 当前已确认事实

1. 当前 `run-loop` 只能执行 case.commands 中的 shell commands，尚未有 executor 分支。
2. 当前产品已经具备：
- `executor_request.json`
- `handoff_bundle.json`
- adapter-specific handoff markdown
3. 已补 runtime binding：
- `.awf/workflow.json` 中新增 `executor.runtime.bindings`
- 可按 adapter 配置 `enabled / mode / command_template / result_source`
4. 已补结构化 runtime 输出：
- `schemas/executor_result.schema.json`
- `run-loop` 与 `run-executor` 都能消费 executor result
5. smoke 结果表明：
- `run-executor` 可直接调用 mock executor
- `run-loop` 在 `execution_mode=executor` 时能完成 case 并写入 result
