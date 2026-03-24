from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .executor import build_executor_request, build_handoff_bundle, list_adapters, render_adapter_handoff
from .scanner import scan_workspace


@dataclass
class PlanResult:
    project_dir: str
    task_name: str
    files_created: list[str]
    notes: list[str]
    ai_handoff_path: str
    executor_request_path: str
    handoff_bundle_path: str
    ai_handoff_prompt: str
    case_count: int


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
            "workflow": manifest,
        }

    scan_result = scan_workspace(str(project_dir))
    return {
        "project_name": project_dir.name,
        "scan_result": scan_result,
        "recommended_skills": scan_result.get("recommended_skills") or [],
        "workflow": {},
    }


def _collect_tech_stack(context: dict[str, Any]) -> list[str]:
    scan_result = context.get("scan_result") or {}
    repos = scan_result.get("repos") or []
    values: list[str] = []
    for repo in repos:
        for item in repo.get("tech_stack") or []:
            if item not in values:
                values.append(item)
    return values


def _detect_requirement_signals(goal: str, scope: str, tech_stack: list[str], scan_result: dict[str, Any]) -> dict[str, Any]:
    text = f"{goal} {scope}".lower()
    is_frontend = any(token in text for token in ["页面", "首页", "列表", "组件", "前端", "ui"]) or any(
        token in tech_stack for token in ["react", "taro", "vue", "nextjs", "miniapp"]
    )
    is_backend = any(token in text for token in ["接口", "后端", "服务", "api", "数据库", "迁移"]) or "go" in tech_stack
    needs_docs = any(token in text for token in ["文档", "说明", "readme", "playbook"])
    needs_test = any(token in text for token in ["测试", "验收", "联调", "e2e", "build"])
    is_multi_repo = (scan_result.get("summary") or {}).get("repo_count", 0) > 1
    complexity = "medium"
    if any(token in text for token in ["重构", "架构", "矩阵", "多 repo", "多仓库", "loop", "自动化"]):
        complexity = "high"
    elif any(token in text for token in ["小改", "修复", "文案", "样式"]):
        complexity = "low"
    return {
        "frontend": is_frontend,
        "backend": is_backend,
        "docs": needs_docs,
        "test": needs_test,
        "multi_repo": is_multi_repo,
        "complexity": complexity,
    }


def _case_payload(case_id: str, title: str, goal: str, adapter: str) -> dict[str, Any]:
    return {
        "id": case_id,
        "title": title,
        "status": "pending",
        "goal": goal,
        "execution_mode": "executor",
        "executor": {
            "adapter": adapter,
        },
        "commands": [],
        "tests": [],
        "notes": [],
        "history": [],
    }


def _build_cases(goal: str, scope: str, signals: dict[str, Any], default_adapter: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [
        _case_payload("C1", "对齐需求与边界", "确认需求目标、范围、约束和已有上下文", default_adapter),
        _case_payload("C2", "设计实现方案", "设计本轮实现所需的结构、接口、数据模型和策略", default_adapter),
    ]

    next_id = 3
    if signals["frontend"]:
        cases.append(_case_payload(f"C{next_id}", "前端页面与组件实现", "完成页面、组件、交互或样式相关实现", default_adapter))
        next_id += 1

    if signals["backend"]:
        cases.append(_case_payload(f"C{next_id}", "后端接口与数据实现", "完成接口、服务、数据模型或数据库相关实现", default_adapter))
        next_id += 1

    if signals["complexity"] == "high":
        cases.append(_case_payload(f"C{next_id}", "结构与依赖收口", "处理跨模块或跨仓库的结构调整与依赖问题", default_adapter))
        next_id += 1

    if signals["docs"]:
        cases.append(_case_payload(f"C{next_id}", "文档与规则更新", "同步更新说明文档、规则或示例", default_adapter))
        next_id += 1

    cases.append(_case_payload(f"C{next_id}", "测试与验收", "完成构建、测试、smoke 或联调验收", default_adapter))
    next_id += 1

    cases.append(_case_payload(f"C{next_id}", "收口与同步", "更新 tracking，按规则完成提交、推送或阻塞记录", default_adapter))
    return cases


def _render_case_table(cases: list[dict[str, Any]]) -> str:
    lines = ["| Case | 状态 | 说明 | 验收 |", "| --- | --- | --- | --- |"]
    for case in cases:
        lines.append(f"| {case['id']} | {case['status']} | {case['title']} | 待补具体验收 |")
    return "\n".join(lines)


def _render_task_plan(project_name: str, task_name: str, goal: str, scope: str, skills: list[str], cases: list[dict[str, Any]], signals: dict[str, Any]) -> str:
    skills_text = ", ".join(skills) if skills else "planning-with-files, split-up-task, task-manager"
    signal_lines = []
    for key, label in [
        ("frontend", "前端相关"),
        ("backend", "后端相关"),
        ("docs", "需要文档"),
        ("test", "强调测试/验收"),
        ("complexity", "复杂度"),
    ]:
        signal_lines.append(f"- {label}：{signals[key]}")
    signal_text = "\n".join(signal_lines)
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

## 任务信号

{signal_text}

## Case 列表

{_render_case_table(cases)}

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


def _render_ai_handoff(project_name: str, task_name: str, goal: str, scope: str) -> str:
    return f"""# AI Handoff

你现在接手的项目是：`{project_name}`

当前任务：
- 任务名：`{task_name}`
- 目标：{goal}
- 作用范围：{scope}

你需要按以下约束继续工作：

1. 先读取：
- `tracking/{task_name}/task_plan.md`
- `tracking/{task_name}/findings.md`
- `tracking/{task_name}/progress.md`
- `tracking/{task_name}/loop_cases.json`
- `docs/development-playbook.md`

2. 只处理当前允许进入的 case
3. 每完成一个 case，都要：
- 更新 tracking
- 执行必要测试或验收
- 在有远端时完成 commit + push
4. 当前 case 未完成前，不进入下一个 case

建议你以 loop 方式推进，而不是一次性跨越多个 case。
"""


def _build_ai_handoff_prompt(project_name: str, task_name: str, goal: str, scope: str) -> str:
    return (
        f"请接手项目 {project_name} 的任务 {task_name}。"
        f"任务目标是：{goal}。"
        f"作用范围是：{scope}。"
        "先阅读 tracking 下该任务的 task_plan.md、findings.md、progress.md、loop_cases.json 和 docs/development-playbook.md，"
        "然后只处理当前允许进入的 case，按 loop 方式推进，并在每个 case 完成后更新 tracking 与验收结果。"
    )


def _render_loop_cases(goal: str, scope: str, cases: list[dict[str, Any]], signals: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": 1,
        "project_goal": goal,
        "scope": scope,
        "planning_signals": signals,
        "loop_policy": {
            "git_pull_before_case": True,
            "git_push_after_case": False,
            "max_sync_retries": 2
        },
        "workflow_rules": [
            "一次只处理一个 case",
            "当前 case 完成后才能进入下一个 case",
            "每个 case 完成后必须更新 tracking",
            "若项目已接远端，提交后必须 push",
        ],
        "cases": cases,
    }


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def plan_requirement(project: str, goal: str, scope: str, task_name: str | None = None) -> PlanResult:
    project_dir = Path(project).expanduser().resolve()
    context = _load_project_context(project_dir)
    resolved_task_name = task_name or _slugify(goal)[:48]
    skills = context.get("recommended_skills") or []
    tech_stack = _collect_tech_stack(context)
    signals = _detect_requirement_signals(goal, scope, tech_stack, context.get("scan_result") or {})
    default_adapter = (((context.get("workflow") or {}).get("executor") or {}).get("default_adapter")) or "manual-handoff"
    cases = _build_cases(goal, scope, signals, default_adapter)

    task_dir = project_dir / "tracking" / resolved_task_name
    files_created: list[str] = []

    generated_files: dict[Path, str] = {
        task_dir / "task_plan.md": _render_task_plan(context["project_name"], resolved_task_name, goal, scope, skills, cases, signals),
        task_dir / "findings.md": _render_findings(goal, scope),
        task_dir / "progress.md": _render_progress(resolved_task_name),
        task_dir / "loop_cases.json": json.dumps(_render_loop_cases(goal, scope, cases, signals), ensure_ascii=False, indent=2) + "\n",
        task_dir / "ai_handoff.md": _render_ai_handoff(context["project_name"], resolved_task_name, goal, scope),
        task_dir / "executor_request.json": json.dumps(
            build_executor_request(
                project_name=context["project_name"],
                project_dir=project_dir,
                task_name=resolved_task_name,
                goal=goal,
                scope=scope,
                recommended_skills=skills,
                loop_script=((project_dir / ".awf" / "workflow.json").exists() and (_safe_read_json(project_dir / ".awf" / "workflow.json").get("loop_script") or "")) or "",
            ),
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        task_dir / "handoff_bundle.json": json.dumps(
            build_handoff_bundle(
                project_name=context["project_name"],
                project_dir=project_dir,
                task_name=resolved_task_name,
                goal=goal,
                scope=scope,
                recommended_skills=skills,
                loop_script=((project_dir / ".awf" / "workflow.json").exists() and (_safe_read_json(project_dir / ".awf" / "workflow.json").get("loop_script") or "")) or "",
            ),
            ensure_ascii=False,
            indent=2,
        ) + "\n",
    }

    bundle = build_handoff_bundle(
        project_name=context["project_name"],
        project_dir=project_dir,
        task_name=resolved_task_name,
        goal=goal,
        scope=scope,
        recommended_skills=skills,
        loop_script=((project_dir / ".awf" / "workflow.json").exists() and (_safe_read_json(project_dir / ".awf" / "workflow.json").get("loop_script") or "")) or "",
    )
    generated_files[task_dir / "handoff_bundle.json"] = json.dumps(bundle, ensure_ascii=False, indent=2) + "\n"
    for adapter in list_adapters():
        generated_files[task_dir / "adapters" / f"{adapter['id']}.md"] = render_adapter_handoff(bundle, adapter["id"])

    for path, content in generated_files.items():
        _write_text(path, content)
        files_created.append(str(path.relative_to(project_dir)))

    notes = [
        f"planner emitted {len(cases)} cases based on requirement signals",
        f"detected signals: {signals}",
    ]

    return PlanResult(
        project_dir=str(project_dir),
        task_name=resolved_task_name,
        files_created=sorted(files_created),
        notes=notes,
        ai_handoff_path=str((task_dir / "ai_handoff.md").relative_to(project_dir)),
        executor_request_path=str((task_dir / "executor_request.json").relative_to(project_dir)),
        handoff_bundle_path=str((task_dir / "handoff_bundle.json").relative_to(project_dir)),
        ai_handoff_prompt=_build_ai_handoff_prompt(context["project_name"], resolved_task_name, goal, scope),
        case_count=len(cases),
    )
