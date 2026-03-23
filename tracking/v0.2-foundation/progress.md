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

### 进行中

- `C3.2 实现 git lifecycle runner MVP`

### 下一步

1. 收尾 `run-loop` 的 sync recovery 策略
2. 进入 `C4`：executor adapter 设计
