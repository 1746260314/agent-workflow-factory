---
title: V0.2 Foundation Findings
created: 2026-03-23
author: AI-assisted
last_updated: 2026-03-23
updated_by: AI-assisted
status: active
---

# V0.2 Foundation Findings

## 当前产品状态

1. MVP 已经跑通 `scan -> scaffold -> plan -> run-loop` 主链路。
2. 当前最大短板不是“不能用”，而是：
   - `plan` 仍是固定模板
   - `run-loop` 还没管理完整 git 生命周期
   - 还没有统一 executor 接口
3. `start.sh` 和 `ai_handoff.md` 已经把普通用户入口显著简化，这是后续继续保留的方向。

## V0.2 核心判断

1. `plan` 的“智能拆解”是产品感知价值最强的部分，应该优先于 UI 包装。
2. `run-loop` 如果不补 git/sync 生命周期，很难真正用于长期项目。
3. executor 接口不应该一开始就绑定单一平台，而应先做通用 adapter 层。

## Planner 增强新发现

1. 即便不引入 LLM，只用规则型信号拆解，也能明显提升 `plan` 的产出质量。
2. 需求信号至少应区分：
   - frontend
   - backend
   - docs
   - test
   - complexity
   - multi_repo
3. 单 repo 和多 repo 的判定必须基于 scanner 的 `repo_count`，不能偷懒用技术栈数量近似。

## Loop Git 生命周期新发现

1. `run-loop` 的 clean check 不能把 `tracking/` 和 `.awf/` 下的工作流文件算作业务脏改动，否则会误伤正常使用场景。
2. 最小 git 生命周期的第一步不是自动 commit，而是：
   - 识别 git repo
   - 检查 worktree
   - 在有远端时按策略 pull / push
3. `sync_pending` 应作为 case 状态保留，便于后续恢复逻辑接管。
4. sync 恢复不应只是插入一个占位 case；`git_sync_recovery` 本身必须能在下一轮主动尝试 pull/push 修复。
5. 人工介入升级不应覆盖原业务 case，原 case 应继续保留为 `pending` 或 `sync_pending`，让状态机保持可追溯。

## Executor 接口新发现

1. 仅靠 `ai_handoff.md` 还不够，AI 编码工具需要一份机器可读的输入对象，才能稳定接入不同 adapter。
2. executor 接口的第一版不需要立刻绑定真实平台 SDK，先统一出：
   - `required_reads`
   - `recommended_skills`
   - `loop` 元信息
   - `handoff_prompt`
3. `executor_request.json` 应与 `ai_handoff.md` 并存：
   - markdown 继续服务人工阅读
   - JSON 负责被 Cursor/Codex/Claude Code 等工具程序化消费
4. 当接入真实 AI 工具时，单个 `executor_request.json` 仍然偏底层；还需要一个更高层的 bundle，把路径、adapter hints 和 request 本身收拢到一个入口对象里。

## Runtime Status 新发现

1. 用户真正关心的不是“有没有 `runs/*.json`”，而是：
   - loop 主进程是否活着
   - 当前停在什么 case
   - 当前处于哪个 phase
   - 最近一次更新时间是什么时候
2. 所以 `status` 命令不能只读静态 case 队列，必须优先读运行态文件。
3. 运行态文件应被忽略，不进入 git；它属于可观察性层，不是项目源码的一部分。

## 多 Repo 示例新发现

1. 用户很难仅凭 README 理解 “multi_repo=true” 会带来什么实际差异，示例输出比口头说明更有效。
2. 多 repo 场景下，最有价值的不是展示完整 scan 结果，而是展示 `plan` 结果里：
   - case 数量变多
   - notes 明确带上 `multi_repo=true`
   - handoff bundle 依然保持统一入口

## 当前收口判断

1. `v0.2 foundation` 这一轮的目标已经达到：
   - planner 不再固定 5-case
   - loop 已具备 git/sync 基础生命周期
   - handoff 已升级成 bundle
   - runtime status 已可观测
   - 多 repo 示例已补齐
2. 下一轮的价值重点不再是补基础骨架，而是：
   - 继续把 case 拆得更细
   - 让 loop 真正绑定 AI 执行器
