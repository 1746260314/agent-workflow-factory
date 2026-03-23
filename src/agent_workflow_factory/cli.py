from __future__ import annotations

import argparse
import json

from .scanner import scan_workspace
from .scaffold import generate_scaffold
from .planner import plan_requirement
from .loop import run_loop_once


def cmd_scan(args: argparse.Namespace) -> int:
    result = scan_workspace(args.workspace)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    from pathlib import Path

    output = Path(args.output).expanduser().resolve()
    tracking_dir = output / "tracking" / "initial-workflow"
    tracking_dir.mkdir(parents=True, exist_ok=True)

    files = {
        tracking_dir / "task_plan.md": "# 任务计划\n",
        tracking_dir / "findings.md": "# 发现记录\n",
        tracking_dir / "progress.md": "# 进度日志\n",
    }

    for path, content in files.items():
        if not path.exists():
            path.write_text(content, encoding="utf-8")

    print(f"initialized workflow scaffold at: {output}")
    return 0


def cmd_scaffold(args: argparse.Namespace) -> int:
    result = generate_scaffold(
        workspace=args.workspace,
        output=args.output,
        project_name=args.project_name,
        task_name=args.task_name,
    )
    print(
        json.dumps(
            {
                "output_dir": result.output_dir,
                "project_name": result.project_name,
                "files_created": result.files_created,
                "notes": result.notes,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    result = plan_requirement(
        project=args.project,
        goal=args.goal,
        scope=args.scope,
        task_name=args.task_name,
    )
    print(
        json.dumps(
            {
                "project_dir": result.project_dir,
                "task_name": result.task_name,
                "files_created": result.files_created,
                "notes": result.notes,
                "ai_handoff_path": result.ai_handoff_path,
                "ai_handoff_prompt": result.ai_handoff_prompt,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_run_loop(args: argparse.Namespace) -> int:
    result = run_loop_once(project_root=args.project, cases_file=args.cases_file)
    print(
        json.dumps(
            {
                "case_id": result.case_id,
                "status": result.status,
                "result_path": result.result_path,
                "tests_run": result.tests_run,
                "notes": result.notes,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="awf",
        description="Agent Workflow Factory CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="scan a workspace")
    scan_parser.add_argument("--workspace", required=True, help="workspace path")
    scan_parser.set_defaults(func=cmd_scan)

    init_parser = subparsers.add_parser("init", help="initialize workflow scaffold in a target project")
    init_parser.add_argument("--output", required=True, help="target project path")
    init_parser.set_defaults(func=cmd_init)

    scaffold_parser = subparsers.add_parser("scaffold", help="generate AI loop scaffold for a target project")
    scaffold_parser.add_argument("--workspace", required=True, help="workspace path used for scanning")
    scaffold_parser.add_argument("--output", required=True, help="target project path")
    scaffold_parser.add_argument("--project-name", help="override generated project name")
    scaffold_parser.add_argument("--task-name", default="initial-delivery", help="initial tracking task name")
    scaffold_parser.set_defaults(func=cmd_scaffold)

    plan_parser = subparsers.add_parser("plan", help="generate a task-level plan and case queue for a requirement")
    plan_parser.add_argument("--project", required=True, help="target project path")
    plan_parser.add_argument("--goal", required=True, help="requirement goal")
    plan_parser.add_argument("--scope", required=True, help="requirement scope")
    plan_parser.add_argument("--task-name", help="override generated task name")
    plan_parser.set_defaults(func=cmd_plan)

    loop_parser = subparsers.add_parser("run-loop", help="run one loop iteration for a case queue")
    loop_parser.add_argument("--project", required=True, help="project root path")
    loop_parser.add_argument("--cases-file", required=True, help="path to loop_cases.json")
    loop_parser.set_defaults(func=cmd_run_loop)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
