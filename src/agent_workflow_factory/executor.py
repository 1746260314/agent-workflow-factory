from __future__ import annotations

from pathlib import Path
from typing import Any


def _rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


ADAPTER_REGISTRY: dict[str, dict[str, Any]] = {
    "manual-handoff": {
        "id": "manual-handoff",
        "label": "Manual Handoff",
        "artifact_format": "markdown",
        "bundle_input": "handoff_bundle.json",
        "notes": [
            "适合人工复制粘贴给任意 AI 工具。",
            "优先阅读 handoff bundle 和 required_reads。",
        ],
    },
    "cursor": {
        "id": "cursor",
        "label": "Cursor",
        "artifact_format": "markdown",
        "bundle_input": "handoff_bundle.json",
        "notes": [
            "适合在 IDE 对话中直接粘贴 handoff。",
            "优先读取 bundle 中的 adapter_hints 与 executor_request。",
        ],
    },
    "codex": {
        "id": "codex",
        "label": "Codex",
        "artifact_format": "markdown",
        "bundle_input": "handoff_bundle.json",
        "notes": [
            "适合面向 case 的执行式代理。",
            "建议按 loop 方式只处理当前 case。",
        ],
    },
    "claude-code": {
        "id": "claude-code",
        "label": "Claude Code",
        "artifact_format": "markdown",
        "bundle_input": "handoff_bundle.json",
        "notes": [
            "适合工程代理式工作流。",
            "建议先读取 paths 中的 tracking 文件再开始实现。",
        ],
    },
}


def list_adapters() -> list[dict[str, Any]]:
    return [ADAPTER_REGISTRY[key] for key in sorted(ADAPTER_REGISTRY.keys())]


def get_adapter(adapter_id: str) -> dict[str, Any]:
    if adapter_id not in ADAPTER_REGISTRY:
        raise KeyError(f"unknown adapter: {adapter_id}")
    return ADAPTER_REGISTRY[adapter_id]


def build_executor_request(
    *,
    project_name: str,
    project_dir: Path,
    task_name: str,
    goal: str,
    scope: str,
    recommended_skills: list[str],
    loop_script: str = "",
    case_id: str = "C1",
) -> dict[str, Any]:
    task_dir = project_dir / "tracking" / task_name
    required_reads = [
        _rel(task_dir / "task_plan.md", project_dir),
        _rel(task_dir / "findings.md", project_dir),
        _rel(task_dir / "progress.md", project_dir),
        _rel(task_dir / "loop_cases.json", project_dir),
    ]
    playbook = project_dir / "docs" / "development-playbook.md"
    if playbook.exists():
        required_reads.append(_rel(playbook, project_dir))

    return {
        "version": 1,
        "project_name": project_name,
        "project_root": str(project_dir),
        "task_name": task_name,
        "case_id": case_id,
        "goal": goal,
        "scope": scope,
        "required_reads": required_reads,
        "recommended_skills": recommended_skills,
        "loop": {
            "script_path": loop_script,
            "cases_file": _rel(task_dir / "loop_cases.json", project_dir),
            "tracking_dir": _rel(task_dir, project_dir),
        },
        "execution_rules": [
            "先阅读 required_reads 中列出的文件，再开始工作",
            "只处理当前允许进入的 case",
            "每个 case 完成后都要更新 tracking",
            "执行必要测试或验收后再结束当前 case",
            "项目有远端时，完成提交后应 push",
        ],
        "supported_adapters": [
            adapter["id"] for adapter in list_adapters()
        ],
        "handoff_prompt": (
            f"请接手项目 {project_name} 的任务 {task_name}。"
            f"任务目标是：{goal}。"
            f"作用范围是：{scope}。"
            "先阅读 required_reads 中列出的文件，然后只处理当前允许进入的 case，"
            "按 loop 方式推进，并在每个 case 完成后更新 tracking 与验收结果。"
        ),
    }


def render_adapter_handoff(bundle: dict[str, Any], adapter_id: str) -> str:
    adapter = get_adapter(adapter_id)
    paths = bundle.get("paths") or {}
    lines = [
        f"# {adapter['label']} Handoff",
        "",
        f"- 项目：`{bundle['project_name']}`",
        f"- 任务：`{bundle['task_name']}`",
        f"- 当前 case：`{bundle['current_case_id']}`",
        f"- 目标：{bundle['goal']}",
        f"- 范围：{bundle['scope']}",
        "",
        "## 优先读取",
        "",
        f"1. `{paths.get('executor_request', '')}`",
        f"2. `{paths.get('task_plan', '')}`",
        f"3. `{paths.get('findings', '')}`",
        f"4. `{paths.get('progress', '')}`",
        f"5. `{paths.get('loop_cases', '')}`",
    ]
    playbook = paths.get("playbook", "")
    if playbook:
        lines.append(f"6. `{playbook}`")

    lines.extend(
        [
            "",
            "## 执行要求",
            "",
            "1. 只处理当前允许进入的 case。",
            "2. 每完成一个 case，都要更新 tracking。",
            "3. 先做必要测试或验收，再结束当前 case。",
            "4. 项目存在远端时，提交后继续 push。",
            "",
            "## Adapter 说明",
            "",
        ]
    )
    lines.extend(f"- {note}" for note in adapter.get("notes") or [])
    lines.extend(
        [
            "",
            "## 推荐 skills",
            "",
            ", ".join(bundle.get("recommended_skills") or []) or "无",
            "",
            "## Prompt",
            "",
            bundle.get("executor_request", {}).get("handoff_prompt", ""),
            "",
        ]
    )
    return "\n".join(lines)


def build_handoff_bundle(
    *,
    project_name: str,
    project_dir: Path,
    task_name: str,
    goal: str,
    scope: str,
    recommended_skills: list[str],
    loop_script: str = "",
    case_id: str = "C1",
) -> dict[str, Any]:
    task_dir = project_dir / "tracking" / task_name
    executor_request = build_executor_request(
        project_name=project_name,
        project_dir=project_dir,
        task_name=task_name,
        goal=goal,
        scope=scope,
        recommended_skills=recommended_skills,
        loop_script=loop_script,
        case_id=case_id,
    )
    adapter_artifacts = {
        adapter["id"]: _rel(task_dir / "adapters" / f"{adapter['id']}.md", project_dir)
        for adapter in list_adapters()
    }
    return {
        "version": 1,
        "project_name": project_name,
        "task_name": task_name,
        "goal": goal,
        "scope": scope,
        "current_case_id": case_id,
        "paths": {
            "task_plan": _rel(task_dir / "task_plan.md", project_dir),
            "findings": _rel(task_dir / "findings.md", project_dir),
            "progress": _rel(task_dir / "progress.md", project_dir),
            "loop_cases": _rel(task_dir / "loop_cases.json", project_dir),
            "ai_handoff": _rel(task_dir / "ai_handoff.md", project_dir),
            "executor_request": _rel(task_dir / "executor_request.json", project_dir),
            "playbook": _rel(project_dir / "docs" / "development-playbook.md", project_dir)
            if (project_dir / "docs" / "development-playbook.md").exists()
            else "",
        },
        "recommended_skills": recommended_skills,
        "supported_adapters": executor_request["supported_adapters"],
        "adapter_artifacts": adapter_artifacts,
        "adapter_hints": {
            "manual-handoff": {
                "preferred_input": _rel(task_dir / "handoff_bundle.json", project_dir),
                "artifact": adapter_artifacts["manual-handoff"],
                "notes": ["适合人工转交。"],
            },
            "cursor": {
                "preferred_input": _rel(task_dir / "handoff_bundle.json", project_dir),
                "artifact": adapter_artifacts["cursor"],
                "notes": ["优先读取 bundle，再查看 rendered handoff。"],
            },
            "codex": {
                "preferred_input": _rel(task_dir / "handoff_bundle.json", project_dir),
                "artifact": adapter_artifacts["codex"],
                "notes": ["按 loop 方式只处理当前允许进入的 case。"],
            },
            "claude-code": {
                "preferred_input": _rel(task_dir / "handoff_bundle.json", project_dir),
                "artifact": adapter_artifacts["claude-code"],
                "notes": ["先读取 bundle 中的 paths，再开始实现与验收。"],
            },
        },
        "executor_request": executor_request,
    }
