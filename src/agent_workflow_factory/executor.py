from __future__ import annotations

from pathlib import Path
from typing import Any


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
    def rel(path: Path) -> str:
        return str(path.relative_to(project_dir))

    task_dir = project_dir / "tracking" / task_name
    required_reads = [
        rel(task_dir / "task_plan.md"),
        rel(task_dir / "findings.md"),
        rel(task_dir / "progress.md"),
        rel(task_dir / "loop_cases.json"),
    ]
    playbook = project_dir / "docs" / "development-playbook.md"
    if playbook.exists():
        required_reads.append(rel(playbook))

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
            "cases_file": rel(task_dir / "loop_cases.json"),
            "tracking_dir": rel(task_dir),
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
