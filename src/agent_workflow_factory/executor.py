from __future__ import annotations

from pathlib import Path
from typing import Any


def _rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


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
            "manual-handoff",
            "cursor",
            "codex",
            "claude-code",
        ],
        "handoff_prompt": (
            f"请接手项目 {project_name} 的任务 {task_name}。"
            f"任务目标是：{goal}。"
            f"作用范围是：{scope}。"
            "先阅读 required_reads 中列出的文件，然后只处理当前允许进入的 case，"
            "按 loop 方式推进，并在每个 case 完成后更新 tracking 与验收结果。"
        ),
    }


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
        "adapter_hints": {
            "cursor": {
                "preferred_input": _rel(task_dir / "executor_request.json", project_dir),
                "notes": ["优先读取 executor_request.json，再读取 required_reads 中列出的文件。"],
            },
            "codex": {
                "preferred_input": _rel(task_dir / "executor_request.json", project_dir),
                "notes": ["按 loop 方式只处理当前允许进入的 case。"],
            },
            "claude-code": {
                "preferred_input": _rel(task_dir / "executor_request.json", project_dir),
                "notes": ["先读取 bundle 中的 paths，再开始实现与验收。"],
            },
        },
        "executor_request": executor_request,
    }
