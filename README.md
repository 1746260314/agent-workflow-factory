---
title: Agent Workflow Factory
created: 2026-03-20
author: cggg
last_updated: 2026-03-23
updated_by: cggg
status: active
---

# Agent Workflow Factory

给一个项目生成 AI 持续开发所需的基础设施。

它当前能做 4 件事：
- 扫描目标项目
- 给目标项目生成 playbook、tracking、loop 骨架
- 把一个需求转成任务流和 case 队列
- 跑一轮最小 loop

## 适合谁

适合这类场景：
- 你有一个本地代码项目
- 你想让 Cursor、Codex、Claude Code 之类的 AI 工具持续开发它
- 你希望有统一的 tracking、case、验收和 loop 结构

## 安装与运行

```bash
git clone <repo-url>
cd agent-workflow-factory
./start.sh help
```

当前直接用本地 Python 运行，不需要额外安装包。

## 最短上手流程

假设你的目标项目是：

```bash
/Users/me/projects/my-app
```

### 1. 扫描项目

```bash
./start.sh scan /Users/me/projects/my-app
```

你会看到：
- 技术栈
- 测试信号
- 文档信号
- 推荐 skills

### 2. 给项目生成 AI loop 基础设施

```bash
./start.sh scaffold /Users/me/projects/my-app
```

这一步会在目标项目里生成：
- `docs/development-playbook.md`
- `tracking/index.md`
- `tracking/initial-delivery/...`
- `.awf/workflow.json`
- `scripts/<project>-loop`

### 3. 输入一个需求，生成任务流

```bash
./start.sh plan /Users/me/projects/my-app "开发一个新的首页功能模块" "首页和公共组件"
```

这一步会生成：
- `tracking/<task-name>/task_plan.md`
- `tracking/<task-name>/findings.md`
- `tracking/<task-name>/progress.md`
- `tracking/<task-name>/loop_cases.json`
- `tracking/<task-name>/ai_handoff.md`
- `tracking/<task-name>/executor_request.json`
- `tracking/<task-name>/handoff_bundle.json`

### 4. 把任务交给 AI 编码工具

`ai_handoff.md` 就是给 AI 工具的接力说明。

`executor_request.json` 是机器可读的 handoff 输入，适合被不同 AI 工具或后续 executor adapter 直接读取。

`handoff_bundle.json` 则把：
- tracking 文件路径
- 推荐 skills
- executor request
- adapter hints

收在一个统一 bundle 里，适合直接交给 AI 工具集成层使用。

你可以把它交给：
- Cursor
- Codex
- Claude Code

也可以直接把 `plan` 命令输出里的 `ai_handoff_prompt` 贴给 AI。

### 5. 跑一轮最小 loop

```bash
./start.sh run-loop /Users/me/projects/my-app /Users/me/projects/my-app/tracking/<task-name>/loop_cases.json
```

当前版本会：
- 找到下一个 `pending` case
- 执行 case 里的命令
- 更新 case 状态
- 生成 `runs/*.result.json`

### 6. 查看 loop 运行状态

```bash
./start.sh status /Users/me/projects/my-app /Users/me/projects/my-app/tracking/<task-name>/loop_cases.json
```

这个命令会优先显示运行态：
- loop 主进程是否还活着
- 当前正在执行哪个 case
- 当前 phase 是 `implementing`、`testing`、`pushing` 还是 `sync_recovery`
- 当前运行目录
- 最近一次更新时间和最后一条消息

如果当前没有活跃 loop，它会自动退回静态队列视图。

## `start.sh` 支持的命令

```bash
./start.sh help
./start.sh scan <workspace>
./start.sh scaffold <workspace> [output] [project_name] [task_name]
./start.sh plan <project> <goal> <scope> [task_name]
./start.sh run-loop <project> <cases_file>
./start.sh status <project> <cases_file>
```

如果你更喜欢直接调 CLI，也支持：

```bash
PYTHONPATH=src python3 -m agent_workflow_factory.cli --help
```

## 当前版本边界

当前版本已经跑通：
- `scan`
- `scaffold`
- `plan`
- `run-loop`
- `status`

但它还不是完整版，暂时还没有：
- 自动调用 LLM 写代码
- 智能拆成很多细 case
- 自动 commit 阶段与更完整的执行 phase
- 多 repo 协同 loop

## 当前目录

```text
agent-workflow-factory/
├── docs/
├── examples/
├── schemas/
├── src/agent_workflow_factory/
├── templates/
├── tracking/
├── start.sh
└── README.md
```

## 多 repo / workspace 示例

如果你的目标项目本身是一个 workspace 或项目矩阵，`plan` 会把 `multi_repo` 作为信号之一，自动把 case 拆得更细。

可参考：
- [examples/multi-repo-plan-output.example.json](/Users/cggg/Documents/private/agent-workflow-factory/examples/multi-repo-plan-output.example.json)
