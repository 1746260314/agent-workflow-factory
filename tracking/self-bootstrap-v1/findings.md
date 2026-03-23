---
title: Self Bootstrap V1 Findings
created: 2026-03-23
author: AI-assisted
last_updated: 2026-03-23
updated_by: AI-assisted
status: active
---

# Self Bootstrap V1 Findings

## 产品定位收口

1. 工具的核心价值是为目标项目生成一套可被 AI 工具持续消费的开发基础设施。
2. `scanner / scaffold generator / requirement planner / loop runner` 是内部模块，不应成为用户理解产品的负担。
3. 用户视角下，它更像一个“项目接入后即可开始 AI loop 开发”的工厂。

## 当前实现发现

1. scanner MVP 已经够用来支撑下一阶段，不需要继续先扩扫描深度。
2. 现有根目录散落的计划文件会制造第二份真相，必须迁入 `tracking/`。
3. 下一阶段最关键的是定义脚手架产出物，而不是继续讨论抽象分层。

## Scaffold Generator 新发现

1. 对目标项目真正有价值的首批产物不是复杂 schema，而是能直接被 AI 使用的基础文件：
   - playbook
   - tracking
   - loop cases
   - loop skeleton
2. `scaffold` 命令必须同时产出人类可读文件和机器可读 manifest，否则后续 planner / runner 会缺少统一输入。
3. 当前最合理的项目内状态文件位置是 `.awf/workflow.json`，用于沉淀扫描结果与 loop 基线。

## Planner / Runner 新发现

1. `plan` 命令先产出稳定的通用 5-case 队列是合理的，比一开始追求高智能拆解更稳。
2. `run-loop` 的 MVP 关键不是直接接 LLM，而是先把 case 状态推进、命令执行和 result 写盘做扎实。
3. `tracking/<task>/runs/*.result.json` 这类结构化结果，正是 `fmsn-suite` 风格里值得保留的部分。
