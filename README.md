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

它当前能做这些事：
- 扫描目标项目
- 给目标项目生成 playbook、tracking、loop 骨架
- 把一个需求转成任务流和 case 队列
- 跑一轮最小 loop
- 输出运行态 status
- 生成 adapter-specific handoff 产物
- 按 workflow 配置调用 executor runtime

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

如果你想直接使用全局命令，也可以在仓库内执行：

```bash
pip install -e .
awf --help
```

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

case 数量会按项目和需求复杂度变化：
- 单 repo 前端需求：通常是 `6~8` 个 case
- 多 repo / 高复杂度需求：可以到 `10+` 个 case
- 每个 case 会带：
  - `owner_skill`
  - `depends_on`
  - `acceptance`
  - `write_scope`

### 4. 把任务交给 AI 编码工具

`ai_handoff.md` 就是给 AI 工具的接力说明。

`executor_request.json` 是机器可读的 handoff 输入，适合被不同 AI 工具或后续 executor adapter 直接读取。

`handoff_bundle.json` 则把：
- tracking 文件路径
- 推荐 skills
- executor request
- adapter hints

收在一个统一 bundle 里，适合直接交给 AI 工具集成层使用。

现在还会额外生成：
- `tracking/<task-name>/adapters/cursor.md`
- `tracking/<task-name>/adapters/codex.md`
- `tracking/<task-name>/adapters/claude-code.md`
- `tracking/<task-name>/adapters/manual-handoff.md`

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
- 如果 case 是 `execution_mode=executor`
  - 按 `.awf/workflow.json` 中的 runtime binding 调用外部 executor
  - 读取结构化 `executor_result`
  - 回填到 case 状态和最终 loop result

### 5.1 配置 executor runtime

如果你希望 loop 真正调用外部 AI 工具，而不只是生成 handoff 文件，需要在目标项目的：

```bash
.awf/workflow.json
```

里配置某个 adapter 的 runtime binding，例如：

```json
{
  "executor": {
    "default_adapter": "codex",
    "runtime": {
      "bindings": {
        "codex": {
          "enabled": true,
          "mode": "external_command",
          "command_template": "python3 {project_root}/mock_executor.py {case_id} {result_file}",
          "result_source": "file"
        }
      }
    }
  }
}
```

占位符会在运行时被替换：
- `{project_root}`
- `{task_name}`
- `{case_id}`
- `{case_title}`
- `{cases_file}`
- `{bundle_file}`
- `{request_file}`
- `{result_file}`
- `{adapter}`

外部 executor 需要输出符合 `schemas/executor_result.schema.json` 的 JSON。

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
./start.sh list-adapters
./start.sh render-adapter <bundle_file> <adapter> [output]
./start.sh run-executor <project> <task_name> <case_id> [adapter]
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
- `list-adapters`
- `render-adapter`
- `run-executor`

但它还不是完整版，暂时还没有：
- 自动调用 LLM 写代码
- 无限递归式的子 case 细化
- 自动 commit 阶段与更完整的执行 phase
- 多 repo 协同 loop
- 真实 SDK 级的 Cursor / Codex / Claude Code 执行绑定

当前 executor runtime 是：
- 通用外部 command binding
- 结构化结果回填
- 不直接耦合私有 SDK

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
- [examples/fine-grained-plan-output.example.json](/Users/cggg/Documents/private/agent-workflow-factory/examples/fine-grained-plan-output.example.json)
- [examples/executor-runtime-binding.example.json](/Users/cggg/Documents/private/agent-workflow-factory/examples/executor-runtime-binding.example.json)
- [examples/executor-result.example.json](/Users/cggg/Documents/private/agent-workflow-factory/examples/executor-result.example.json)

## 发布前建议检查

可按以下顺序自查：

1. `./start.sh scan <workspace>`
2. `./start.sh scaffold <workspace>`
3. `./start.sh plan <project> "<goal>" "<scope>"`
4. `./start.sh list-adapters`
5. `./start.sh render-adapter <bundle_file> codex`
6. 如已配置 runtime binding，再执行：
   - `./start.sh run-executor <project> <task_name> <case_id> codex`
   - `./start.sh run-loop <project> <cases_file>`
   - `./start.sh status <project> <cases_file>`

更完整的发布检查见：
- [docs/release-checklist.md](/Users/cggg/Documents/private/agent-workflow-factory/docs/release-checklist.md)
- [examples/README.md](/Users/cggg/Documents/private/agent-workflow-factory/examples/README.md)
