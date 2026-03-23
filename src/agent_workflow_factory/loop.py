from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class LoopRunResult:
    case_id: str
    status: str
    result_path: str
    tests_run: list[str]
    notes: str


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _find_next_case(cases: list[dict[str, Any]]) -> dict[str, Any] | None:
    for case in cases:
        if case.get("status") == "pending":
            return case
    return None


def run_loop_once(project_root: str, cases_file: str) -> LoopRunResult:
    root = Path(project_root).expanduser().resolve()
    cases_path = Path(cases_file).expanduser().resolve()
    payload = _load_json(cases_path)
    cases = payload.get("cases") or []

    current_case = _find_next_case(cases)
    if current_case is None:
        result = {
            "case_id": "none",
            "status": "skipped",
            "summary": "no pending case",
            "tests_run": [],
            "tests_passed": True,
            "commit_created": False,
            "commit_message": "",
            "files_touched": [str(cases_path)],
            "notes": "all cases are already resolved",
        }
        result_path = cases_path.parent / "runs" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-no-case.result.json"
        _write_json(result_path, result)
        return LoopRunResult("none", "skipped", str(result_path), [], result["notes"])

    commands = current_case.get("commands") or []
    current_case["status"] = "in_progress"
    tests_run: list[str] = []
    files_touched = [str(cases_path)]

    if not commands:
        current_case["status"] = "blocked"
        current_case.setdefault("history", []).append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "status": "blocked",
                "notes": "no commands configured",
            }
        )
        _write_json(cases_path, payload)
        result = {
            "case_id": current_case["id"],
            "status": "blocked",
            "summary": current_case.get("title", current_case["id"]),
            "tests_run": [],
            "tests_passed": False,
            "commit_created": False,
            "commit_message": "",
            "files_touched": files_touched,
            "notes": "no commands configured for this case",
        }
        result_path = cases_path.parent / "runs" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{current_case['id']}.result.json"
        _write_json(result_path, result)
        return LoopRunResult(current_case["id"], "blocked", str(result_path), [], result["notes"])

    for command in commands:
        tests_run.append(command)
        completed = subprocess.run(
            command,
            shell=True,
            cwd=str(root),
            text=True,
            capture_output=True,
        )
        if completed.returncode != 0:
            current_case["status"] = "failed"
            current_case.setdefault("history", []).append(
                {
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "status": "failed",
                    "command": command,
                    "stdout": completed.stdout[-1000:],
                    "stderr": completed.stderr[-1000:],
                }
            )
            _write_json(cases_path, payload)
            result = {
                "case_id": current_case["id"],
                "status": "failed",
                "summary": current_case.get("title", current_case["id"]),
                "tests_run": tests_run,
                "tests_passed": False,
                "commit_created": False,
                "commit_message": "",
                "files_touched": files_touched,
                "notes": f"command failed: {command}",
            }
            result_path = cases_path.parent / "runs" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{current_case['id']}.result.json"
            _write_json(result_path, result)
            return LoopRunResult(current_case["id"], "failed", str(result_path), tests_run, result["notes"])

    current_case["status"] = "completed"
    current_case.setdefault("history", []).append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "status": "completed",
            "commands": commands,
        }
    )
    _write_json(cases_path, payload)

    result = {
        "case_id": current_case["id"],
        "status": "completed",
        "summary": current_case.get("title", current_case["id"]),
        "tests_run": tests_run,
        "tests_passed": True,
        "commit_created": False,
        "commit_message": "",
        "files_touched": files_touched,
        "notes": "commands completed successfully",
    }
    result_path = cases_path.parent / "runs" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{current_case['id']}.result.json"
    _write_json(result_path, result)
    return LoopRunResult(current_case["id"], "completed", str(result_path), tests_run, result["notes"])
