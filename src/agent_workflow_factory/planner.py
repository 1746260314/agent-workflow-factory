from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .scanner import scan_workspace


@dataclass
class PlanResult:
    project_dir: str
    task_name: str
    files_created: list[str]
    notes: list[str]


def _slugify(value: str) -> str:
    cleaned = []
    last_dash = False
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
            last_dash = False
            continue
        if not last_dash:
            cleaned.append("-")
            last_dash = True
    return "".join(cleaned).strip("-") or "task"


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_project_context(project_dir: Path) -> dict[str, Any]:
    manifest_path = project_dir / ".awf" / "workflow.json"
    if manifest_path.exists():
        manifest = _safe_read_json(manifest_path)
        scan_result = manifest.get("workspace_scan") or {}
        return {
            "project_name": manifest.get("project_name") or project_dir.name,
            "scan_result": scan_result,
            "recommended_skills": manifest.get("recommended_skills") or scan_result.get("recommended_skills") or [],
        }

    scan_result = scan_workspace(str(project_dir))
    return {
        "project_name": project_dir.name,
        "scan_result": scan_result,
        "recommended_skills": scan_result.get("recommended_skills") or [],
    }


def _render_task_plan(project_name: str, task_name: str, goal: str, scope: str, skills: list[str]) -> str:
    skills_text = ", ".join(skills) if skills else "planning-with-files, split-up-task, task-manager"
    return f"""---
title: {project_name} {task_name} Task Plan
created: 2026-03-23
author: Agent Workflow Factory
last_updated: 2026-03-23
updated_by: Agent Workflow Factory
status: active
---

# {task_name} Task Plan

## 任务重述

- 目标：{goal}
- 作用范围：{scope}
- 推荐 skills：{skills_text}
- 预期输出：按 case 顺序完成分析、设计、实现、验收和收口
- 验收方式：至少完成一轮源码级或命令级验收，并更新 tracking

## Case 列表

| Case | 状态 | 说明 | 验收 |
| --- | --- | --- | --- |
| C1 | pending | 对齐需求、边界与已有上下文 | 任务重述确认，关键约束记录完整 |
| C2 | pending | 设计技术方案与必要数据结构 | 方案落文档，关键接口/数据结构明确 |
| C3 | pending | 完成最小实现 | 关键代码完成 |
| C4 | pending | 执行测试与验收 | 至少一项测试或构建通过 |
| C5 | pending | 更新 tracking 并收口提交 | tracking 完整更新 |

## 当前执行指令

- 当前允许进入的 case：`C1`
- 当前任务目录：`tracking/{task_name}/`
"""


def _render_findings(goal: str, scope: str) -> str:
    return f"""# Findings

## 当前需求

1. 目标：{goal}
2. 范围：{scope}
"""


def _render_progress(task_name: str) -> str:
    return f"""# Progress

## 当前状态

- 当前任务：`{task_name}`
- 当前 case：`C1`

## 已完成

- 已生成任务级 tracking 基线
"""


def _render_loop_cases(goal: str, scope: str) -> dict[str, Any]:
    return {
        "version": 1,
        "project_goal": goal,
        "scope": scope,
        "workflow_rules": [
            "一次只处理一个 case",
            "当前 case 完成后才能进入下一个 case",
            "每个 case 完成后必须更新 tracking",
            "若项目已接远端，提交后必须 push",
        ],
        "cases": [
            {
                "id": "C1",
                "title": "对齐需求与边界",
                "status": "pending",
                "goal": "确认需求目标、范围、约束和已有上下文",
                "commands": [],
                "tests": [],
                "notes": [],
                "history": [],
            },
            {
                "id": "C2",
                "title": "设计实现方案",
                "status": "pending",
                "goal": "设计本轮实现所需的结构、接口、数据模型和策略",
                "commands": [],
                "tests": [],
                "notes": [],
                "history": [],
            },
            {
                "id": "C3",
                "title": "实现最小可交付代码",
                "status": "pending",
                "goal": "完成本轮最小闭环实现",
                "commands": [],
                "tests": [],
                "notes": [],
                "history": [],
            },
            {
                "id": "C4",
                "title": "测试与验收",
                "status": "pending",
                "goal": "完成构建、测试或 smoke，确认结果",
                "commands": [],
                "tests": [],
                "notes": [],
                "history": [],
            },
            {
                "id": "C5",
                "title": "收口与同步",
                "status": "pending",
                "goal": "更新 tracking，按规则完成提交或标记阻塞",
                "commands": [],
                "tests": [],
                "notes": [],
                "history": [],
            },
        ],
    }


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def plan_requirement(project: str, goal: str, scope: str, task_name: str | None = None) -> PlanResult:
    project_dir = Path(project).expanduser().resolve()
    context = _load_project_context(project_dir)
    resolved_task_name = task_name or _slugify(goal)[:48]
    skills = context.get("recommended_skills") or []

    task_dir = project_dir / "tracking" / resolved_task_name
    files_created: list[str] = []

    generated_files: dict[Path, str] = {
        task_dir / "task_plan.md": _render_task_plan(context["project_name"], resolved_task_name, goal, scope, skills),
        task_dir / "findings.md": _render_findings(goal, scope),
        task_dir / "progress.md": _render_progress(resolved_task_name),
        task_dir / "loop_cases.json": json.dumps(_render_loop_cases(goal, scope), ensure_ascii=False, indent=2) + "\n",
    }

    for path, content in generated_files.items():
        _write_text(path, content)
        files_created.append(str(path.relative_to(project_dir)))

    notes = [
        "planner MVP currently emits a generic 5-case queue",
        "next step is to infer finer-grained cases from repo capabilities and requirement complexity",
    ]

    return PlanResult(
        project_dir=str(project_dir),
        task_name=resolved_task_name,
        files_created=sorted(files_created),
        notes=notes,
    )
