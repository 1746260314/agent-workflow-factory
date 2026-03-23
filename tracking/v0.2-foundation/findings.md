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
