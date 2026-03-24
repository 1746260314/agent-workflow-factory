# Progress

## 当前状态

- 当前任务：`v0.7-practical-commit-lifecycle`
- 当前 case：`completed`

## 已完成

- 已建立 v0.7 tracking 基线
- 已补 `git_commit_after_case` 与 `git_commit_message_template` 配置
- 已在 `run-loop` 中加入 `committing` phase 和最小自动 commit 路径
- 已把 `commit_created / commit_message` 回填到 result
- README 已补自动 commit 用法和验证说明
- 在全新 scaffold 的临时 git repo 中完成 smoke：
  - 初始化仓库并提交 scaffold 基线
  - `plan` 生成 `commit-demo`
  - 打开 `git_commit_after_case=true`
  - 执行 `run-loop`
  - 观察到新提交 `awf: complete C1 对齐需求与边界`
  - `git status --short` 为空，工作树干净

## 验证结果

- `python3 -m py_compile src/agent_workflow_factory/*.py`
- fresh smoke:
  - `./start.sh scaffold`
  - `./start.sh plan`
  - `./start.sh run-loop`
  - `git log --oneline -2`
  - `git status --short`
