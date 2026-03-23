from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .scanner import scan_workspace


@dataclass
class ScaffoldResult:
    output_dir: str
    project_name: str
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
    slug = "".join(cleaned).strip("-")
    return slug or "project"


def _detect_primary_repo(scan_result: dict[str, Any]) -> dict[str, Any] | None:
    repos = scan_result.get("repos") or []
    if not repos:
        return None

    workspace = scan_result.get("workspace")
    for repo in repos:
        if repo.get("path") == workspace:
            return repo
    return repos[0]


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _render_playbook(project_name: str, primary_repo: dict[str, Any] | None, recommended_skills: list[str]) -> str:
    repo_name = primary_repo.get("name") if primary_repo else project_name
    tech_stack = ", ".join(primary_repo.get("tech_stack") or []) if primary_repo else "unknown"
    skills_text = ", ".join(recommended_skills) if recommended_skills else "planning-with-files, split-up-task, task-manager"

    return f"""---
title: {project_name} AI Development Playbook
created: 2026-03-23
author: Agent Workflow Factory
last_updated: 2026-03-23
updated_by: Agent Workflow Factory
status: active
---

# {project_name} AI Development Playbook

本文件由 Agent Workflow Factory 自动生成，用于让 AI 工具在当前项目内按统一 loop 方式工作。

## 项目基线

- 主仓库：`{repo_name}`
- 技术栈信号：`{tech_stack}`
- 推荐 skills：`{skills_text}`

## 默认流程

1. 先读取本 playbook 与 `tracking/index.md`
2. 对新需求先做任务重述和范围确认
3. 在 `tracking/<task-name>/` 下生成三件套
4. 先拆 case，再按顺序执行
5. 每个 case 完成后必须更新 tracking
6. 有 git 远端时，case 完成后应 `commit + push`

## Loop 规则

1. 一次只处理一个 case
2. 当前 case 未完成前，不进入下一个 case
3. 每个 case 都需要至少一种可执行验收
4. 遇到 sync 问题时，优先进入 `git_sync_recovery`
5. 连续恢复失败时，升级为人工介入
"""


def _render_tracking_index(project_name: str) -> str:
    return f"""---
title: {project_name} Tracking Index
created: 2026-03-23
author: Agent Workflow Factory
last_updated: 2026-03-23
updated_by: Agent Workflow Factory
status: active
---

# Tracking Index

本目录用于维护 {project_name} 的复杂任务流。

## 约定

1. 每个任务流放在 `tracking/<task-name>/`
2. 每个任务流维护：
- `task_plan.md`
- `findings.md`
- `progress.md`
3. 不在项目根目录散落放置 tracking 文件
"""


def _render_task_plan(project_name: str, task_name: str) -> str:
    return f"""---
title: {project_name} Initial Task Plan
created: 2026-03-23
author: Agent Workflow Factory
last_updated: 2026-03-23
updated_by: Agent Workflow Factory
status: active
---

# Initial Task Plan

## 任务目标

- 在 {project_name} 中启动一个新的 AI loop 任务流

## Case 列表

| Case | 状态 | 说明 | 验收 |
| --- | --- | --- | --- |
| C1 | pending | 对齐需求与范围 | 任务重述完成 |
| C2 | pending | 实现当前最小功能 | 构建或测试通过 |
| C3 | pending | 验收、更新 tracking、提交 | tracking 完整更新 |

## 当前执行指令

- 当前允许进入的 case：`C1`
- 当前任务目录：`tracking/{task_name}/`
"""


def _render_findings() -> str:
    return """# Findings

## 当前已确认事实

1. 在这里记录与本任务直接相关的发现。
"""


def _render_progress(task_name: str) -> str:
    return f"""# Progress

## 当前状态

- 当前任务：`{task_name}`
- 当前 case：`C1`

## 已完成

- 已初始化 tracking 基线
"""


def _render_loop_cases(project_name: str) -> dict[str, Any]:
    return {
        "version": 1,
        "project": project_name,
        "workflow_rules": [
            "一次只处理一个 case",
            "当前 case 完成后才能进入下一个 case",
            "每个 case 完成后必须更新 tracking",
            "有 git 远端时，提交后必须 push",
        ],
        "cases": [
            {
                "id": "C1",
                "title": "对齐需求与范围",
                "status": "pending",
                "goal": "完成任务重述、范围确认与 case 细化",
                "commands": [],
                "tests": [],
                "notes": [],
                "history": [],
            },
            {
                "id": "C2",
                "title": "实现当前最小功能",
                "status": "pending",
                "goal": "完成当前任务的最小可交付实现",
                "commands": [],
                "tests": [],
                "notes": [],
                "history": [],
            },
            {
                "id": "C3",
                "title": "验收与收口",
                "status": "pending",
                "goal": "完成验收、tracking 更新与提交",
                "commands": [],
                "tests": [],
                "notes": [],
                "history": [],
            },
        ],
    }


def _render_loop_script(script_name: str, task_name: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/.." && pwd)"
TASK_DIR="${{ROOT_DIR}}/tracking/{task_name}"
CASES_FILE="${{TASK_DIR}}/loop_cases.json"

cmd="${{1:-status}}"

status() {{
  echo "project root: $ROOT_DIR"
  echo "task dir: $TASK_DIR"
  echo "cases file: $CASES_FILE"
  if [ -f "$CASES_FILE" ]; then
    python3 - <<'PY' "$CASES_FILE"
import json, sys
path = sys.argv[1]
data = json.load(open(path, encoding='utf-8'))
for case in data.get("cases", []):
    print(f"{{case['id']}} {{case['status']}} {{case['title']}}")
PY
  else
    echo "cases file not found"
  fi
}}

run_once() {{
  echo "{script_name}: run-once skeleton"
  echo "next step: wire this script to an LLM executor and result schema"
}}

case "$cmd" in
  status) status ;;
  run-once) run_once ;;
  *)
    echo "usage: $(basename "$0") [status|run-once]"
    exit 1
    ;;
esac
"""


def generate_scaffold(workspace: str, output: str, project_name: str | None = None, task_name: str = "initial-delivery") -> ScaffoldResult:
    scan_result = scan_workspace(workspace)
    output_dir = Path(output).expanduser().resolve()
    primary_repo = _detect_primary_repo(scan_result)
    resolved_project_name = project_name or (primary_repo.get("name") if primary_repo else output_dir.name)
    recommended_skills = scan_result.get("recommended_skills") or []
    script_name = f"{_slugify(resolved_project_name)}-loop"

    files_created: list[str] = []

    awf_dir = output_dir / ".awf"
    tracking_dir = output_dir / "tracking" / task_name
    scripts_dir = output_dir / "scripts"
    docs_dir = output_dir / "docs"

    workflow_manifest = {
        "version": 1,
        "project_name": resolved_project_name,
        "workspace_scan": scan_result,
        "task_name": task_name,
        "recommended_skills": recommended_skills,
        "loop_script": f"scripts/{script_name}",
    }

    generated_files: dict[Path, str] = {
        docs_dir / "development-playbook.md": _render_playbook(resolved_project_name, primary_repo, recommended_skills),
        output_dir / "tracking" / "index.md": _render_tracking_index(resolved_project_name),
        tracking_dir / "task_plan.md": _render_task_plan(resolved_project_name, task_name),
        tracking_dir / "findings.md": _render_findings(),
        tracking_dir / "progress.md": _render_progress(task_name),
        tracking_dir / "loop_cases.json": json.dumps(_render_loop_cases(resolved_project_name), ensure_ascii=False, indent=2) + "\n",
        awf_dir / "workflow.json": json.dumps(workflow_manifest, ensure_ascii=False, indent=2) + "\n",
        scripts_dir / script_name: _render_loop_script(script_name, task_name),
    }

    for path, content in generated_files.items():
        _write_text(path, content)
        files_created.append(str(path.relative_to(output_dir)))

    loop_script_path = scripts_dir / script_name
    loop_script_path.chmod(0o755)

    notes = [
        "scaffold generator currently emits a minimal but runnable project skeleton",
        "loop script is a skeleton and still needs an executor binding",
    ]

    return ScaffoldResult(
        output_dir=str(output_dir),
        project_name=resolved_project_name,
        files_created=sorted(files_created),
        notes=notes,
    )
