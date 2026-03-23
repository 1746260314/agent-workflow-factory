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
