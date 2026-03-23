---
title: Self Bootstrap V1 Progress
created: 2026-03-23
author: AI-assisted
last_updated: 2026-03-23
updated_by: AI-assisted
status: active
---

# Self Bootstrap V1 Progress

## 2026-03-23

### 已完成

- 重新对齐产品目标：生成项目级 AI loop 基础设施，而不是输出分析报告
- 更新 README，使其以用户视角描述产品价值
- 更新 architecture 文档，使模块改为 `scanner / scaffold generator / requirement planner / loop runner`
- 新增 `tracking/index.md`
- 新增 `tracking/self-bootstrap-v1/` 三件套
- 新增 `scaffold.py`
- CLI 新增 `awf scaffold`
- 新增 `schemas/scaffold_manifest.schema.json`
- 新增 `examples/scaffold-output.example.json`
- 完成 scaffold CLI smoke：
  - `PYTHONPATH=src python3 -m agent_workflow_factory.cli scaffold --workspace /Users/cggg/Documents/private/chron-matrix --output <tmp> --project-name ChronMatrix`
- 完成 scaffold Python smoke：
  - `scaffold smoke passed`
- 新增 `planner.py`
- CLI 新增 `awf plan`
- 新增 `schemas/requirement_plan.schema.json`
- 新增 `examples/requirement-plan-output.example.json`
- 完成 planner CLI smoke：
  - `PYTHONPATH=src python3 -m agent_workflow_factory.cli plan --project <tmp> --goal '接入真实接口' --scope '护士端首页与列表' --task-name connect-real-api`
- 完成 planner Python smoke：
  - `planner smoke passed`
- 新增 `loop.py`
- CLI 新增 `awf run-loop`
- 新增 `schemas/loop_cases.schema.json`
- 完成 run-loop CLI smoke：
  - `PYTHONPATH=src python3 -m agent_workflow_factory.cli run-loop --project <tmp> --cases-file <tmp>/tracking/demo/loop_cases.json`
- 完成 run-loop Python smoke：
  - `loop smoke passed`
- 完成 end-to-end self-bootstrap smoke：
  - `scan -> scaffold -> plan -> run-loop`

### 进行中

- 当前 tracking 已收口，等待下一轮能力扩展或远端接入

### 下一步

1. 接 Git 远端并建立提交策略
2. 强化 planner 的细粒度 case 拆解
3. 强化 run-loop 的 sync recovery、git 门禁和 LLM executor 绑定
