---
title: Self Bootstrap V1 Task Plan
created: 2026-03-23
author: AI-assisted
last_updated: 2026-03-23
updated_by: AI-assisted
status: active
---

# Self Bootstrap V1 Task Plan

## 任务重述

- 目标：用 loop 思路完成 `agent-workflow-factory` 的首版可用产品
- 作用范围：本项目文档、tracking、CLI、scanner、scaffold generator、requirement planner、loop runner
- 关键约束：项目自身也遵循 tracking/case/验收门禁；当前不接 GitHub 远端
- 预期输出：一套能扫描项目、生成脚手架、把需求转 case，并能跑基础 loop 的本地工具
- 验收方式：CLI 可运行，关键命令有 smoke test，tracking 与示例产物完整

## 阶段

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| C1 基线收口 | complete | 已统一产品定义，迁移 tracking 结构，建立 case 基线 |
| C2 Scaffold Generator MVP | complete | 已生成项目级 playbook / tracking / queue / schema / loop skeleton |
| C3 Requirement Planner MVP | complete | 已能把一个需求转成 task plan + loop cases |
| C4 Loop Runner MVP | complete | 已能读取 cases 并执行基础门禁与命令编排 |
| C5 自举验收 | complete | 已用本项目实际跑一轮 end-to-end 示例 |

## Case 清单

| Case | 状态 | 说明 | 验收 |
| --- | --- | --- | --- |
| C1.1 收口产品定义与文档结构 | completed | 已更新 README / architecture，确立 scanner + scaffold + planner + runner | 文档一致，tracking 迁移完成 |
| C1.2 建立项目内 tracking 基线 | completed | 已生成 tracking/index 与 self-bootstrap-v1 三件套 | tracking 结构完整 |
| C2.1 设计 scaffold config/schema | completed | 已定义 scaffold manifest schema 与基础产物结构 | schema 与示例存在 |
| C2.2 实现 scaffold generate 命令 | completed | 已生成目标项目基础设施，并补齐文档与输出示例 | `awf scaffold` 可运行 |
| C3.1 设计 requirement plan schema | completed | 已定义需求转 plan/cases 的输出结果结构 | schema 与示例存在 |
| C3.2 实现 plan 命令 | completed | 已根据需求生成 tracking 与 loop cases | `awf plan` 可运行 |
| C4.1 设计 loop state/result 结构 | completed | 已定义 cases/result schema 并引入 runs 结果目录 | schema 完整 |
| C4.2 实现 run-loop 骨架 | completed | 已完成基础 case 读取、门禁、命令执行、结果记录 | `awf run-loop` 可运行 |
| C5.1 本项目自举 smoke | completed | 已用本项目示例跑扫描、scaffold、plan、loop | smoke 通过 |

## 当前结论

1. 产品定义已收口为“项目 AI loop 基础设施生成工具”
2. 当前优先级不是继续增强 scanner，而是让 scaffold / planner / runner 形成闭环
3. `awf scaffold` 已能生成：
   - `docs/development-playbook.md`
   - `tracking/index.md`
   - `tracking/<task>/` 三件套
   - `loop_cases.json`
   - `.awf/workflow.json`
   - `scripts/<project>-loop`
4. `awf plan` 已能把一个需求转成任务级 tracking 和 5-case 队列
5. `awf run-loop` 已能执行带命令的 case，并写入 `runs/*.result.json`
