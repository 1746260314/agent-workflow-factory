---
title: V0.3 Executor Binding Findings
created: 2026-03-24
author: AI-assisted
last_updated: 2026-03-24
updated_by: AI-assisted
status: active
---

# V0.3 Executor Binding Findings

## 当前已知

1. `v0.2` 已经具备：
   - `ai_handoff.md`
   - `executor_request.json`
   - `handoff_bundle.json`
2. 当前缺口不是“有没有 handoff 文件”，而是：
   - 不同 AI 工具如何消费这些产物
   - 是否需要 adapter-specific artifact
   - 如何通过 CLI 直接导出特定工具要用的输入

## 新发现

1. adapter registry 的价值不只是列举工具名称，还要统一：
   - adapter id
   - 输入来源
   - 输出产物格式
   - 适配说明
2. `handoff_bundle.json` 适合作为中间层；adapter-specific markdown 更适合作为最终交给具体 AI 工具的外层包装。
3. 在没有真实 SDK 绑定前，`list-adapters + render-adapter` 已经足够让用户低成本地把任务转交给不同 AI 工具。
