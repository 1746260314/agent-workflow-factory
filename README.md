---
title: Agent Workflow Factory
created: 2026-03-20
author: AI-assisted
last_updated: 2026-03-23
updated_by: AI-assisted
status: active
---

# Agent Workflow Factory

一个独立的项目级 AI loop 基础设施生成工具。

它的目标不是直接替代开发者，而是在扫描目标项目之后，为该项目生成一整套“可执行、可验收、可追踪、可恢复”的 AI 持续开发基础设施，包括：

- 项目矩阵扫描
- 技术栈与工程能力识别
- skills 推荐与绑定策略
- playbook / tracking / queue / schema 生成
- loop runner 与 sync recovery 规则
- 需求转 case 的规划能力
- 验收、提交、推送门禁

## 设计目标

1. 可被不同项目复用，而不是绑定某一个业务仓库或技术栈
2. 扫描完成后直接产出一套可被 AI 工具消费的开发基础设施
3. 同时支持人类可读的 tracking 和机器可读的 queue/schema/result
4. 让用户在完成项目接入后，只需要继续提供需求和范围即可进入 loop 开发

## 产品定义

这个项目对外应表现为一个“项目 AI loop 工厂”，而不是单纯的分析器。

给定一个目标项目，它应该能够：

1. 扫描项目矩阵与仓库能力
2. 生成适配该项目的规范、tracking、case queue、loop runner、schema
3. 基于新需求生成计划与 case 拆解
4. 驱动 AI 以 loop 方式持续开发、测试、提交与恢复同步问题

## 内部模块

从内部实现上，当前按 4 个模块拆：

1. `scanner`
- 扫描项目矩阵、技术栈、测试、文档、skills、脚本与 git 结构

2. `scaffold generator`
- 为目标项目生成 playbook、tracking、queue、schema、loop 脚本

3. `requirement planner`
- 把一个新需求转换为计划、case 队列和验收标准

4. `loop runner`
- 读取当前 case，执行门禁、测试、tracking、commit/push 与 sync recovery

## 当前阶段

当前是产品自举开发阶段，项目自身也按 tracking + case 的方式推进。

已完成：
- 基础目录与 Python CLI 骨架
- scanner MVP
- tracking 模板与基础 schema

待完成：
- scaffold generator MVP
- requirement planner MVP
- loop runner MVP
- 项目自身的自举验证

## 当前项目结构

```text
agent-workflow-factory/
├── docs/
├── examples/
├── schemas/
├── src/agent_workflow_factory/
├── templates/
├── tracking/
│   ├── index.md
│   └── self-bootstrap-v1/
├── pyproject.toml
└── README.md
```

## MVP 命令

```bash
cd /Users/cggg/Documents/private/agent-workflow-factory
PYTHONPATH=src python3 -m agent_workflow_factory.cli --help
PYTHONPATH=src python3 -m agent_workflow_factory.cli scan --workspace /Users/cggg/Documents/private/chron-matrix
PYTHONPATH=src python3 -m agent_workflow_factory.cli scaffold --workspace /path/to/workspace --output /path/to/project
PYTHONPATH=src python3 -m agent_workflow_factory.cli plan --project /path/to/project --goal "接入真实接口" --scope "护士端首页与列表"
PYTHONPATH=src python3 -m agent_workflow_factory.cli run-loop --project /path/to/project --cases-file /path/to/project/tracking/<task>/loop_cases.json
```

## 自举路线

当前项目会用自己要生成的那套思路来开发自己：

1. 先在本项目中建立 tracking 与 case 门禁
2. 再实现 scaffold generator
3. 再实现 requirement planner
4. 最后实现 loop runner 并用于本项目自举
