---
title: Agent Workflow Factory 架构设计
created: 2026-03-20
author: AI-assisted
last_updated: 2026-03-23
updated_by: AI-assisted
status: active
---

# Agent Workflow Factory 架构设计

独立项目，用于为任意软件项目生成“扫描 -> 脚手架生成 -> 需求拆解 -> loop 执行”的自动化交付体系。

## 核心模块

### 1. Scanner

职责：

- 扫描项目矩阵
- 发现 git 仓库
- 识别技术栈
- 判断测试能力
- 发现现有规范文档、tracking、脚本和 skills

输出：

- `project_topology.json`
- `repo_capabilities.json`
- `recommended_skills.json`

### 2. Scaffold Generator

职责：

- 根据 scanner 结果生成项目级 AI loop 基础设施
- 生成 playbook / tracking 模板 / case queue 模板
- 生成 loop schema / result schema / loop 配置
- 生成通用或项目专用 loop runner 脚本

输出：

- `development-playbook.md`
- `tracking/index.md`
- `tracking/<task-name>/task_plan.md`
- `tracking/<task-name>/findings.md`
- `tracking/<task-name>/progress.md`
- `loop_cases.json`
- `loop_result.schema.json`
- `scripts/<project>-loop`

### 3. Requirement Planner

职责：

- 接收一个新需求和范围
- 结合项目扫描结果与现有 playbook 生成计划
- 拆解成可执行 case
- 给出验收标准、技能绑定和执行顺序

输出：

- `tracking/<task-name>/task_plan.md`
- `tracking/<task-name>/findings.md`
- `tracking/<task-name>/progress.md`
- `tracking/<task-name>/loop_cases.json`

### 4. Loop Runner

职责：

- 读取当前 case
- 校验 worktree、sync 状态和门禁
- 调用 LLM 执行当前 case
- 验证测试、tracking、commit、push 是否完成
- 做 sync recovery

## 设计原则

1. 人类可读与机器可读并存
2. 先生成项目基础设施，再生成需求级任务
3. 配置驱动而不是硬编码项目规则
4. 多 repo 兼容
5. 失败可恢复
6. LLM 可直接消费输出结果

## 推荐数据流

```text
workspace
  -> scanner
  -> project topology / repo capabilities / skills
  -> scaffold generator
  -> project playbook + tracking + queue + schema + loop
  -> requirement planner
  -> requirement task plan + case queue
  -> runner
  -> tests / commits / push / history
```

## MVP 范围

MVP 先实现：

1. workspace 基础扫描
2. tracking、playbook 与 queue 模板生成
3. 需求转 case 的最小 planner
4. 基础 loop 配置与 runner 骨架
5. 基础 CLI

MVP 不先实现：

1. 完整智能需求理解
2. 完整多仓库并发编排
3. 复杂 UI
4. 云端服务
