from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ExecutorRuntimeResult:
    case_id: str
    status: str
    summary: str
    notes: str
    tests_run: list[str]
    files_touched: list[str]
    commit_created: bool
    commit_message: str
    adapter: str
    command: str
    result_file: str


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_workflow(project_root: Path) -> dict[str, Any]:
    workflow_path = project_root / ".awf" / "workflow.json"
    if not workflow_path.exists():
        return {}
    try:
        return _load_json(workflow_path)
    except Exception:
        return {}


def _binding_for_adapter(project_root: Path, adapter: str) -> dict[str, Any]:
    workflow = _load_workflow(project_root)
    executor = workflow.get("executor") or {}
    runtime = executor.get("runtime") or {}
    bindings = runtime.get("bindings") or {}
    return bindings.get(adapter) or {}


def _resolve_case_executor(case: dict[str, Any], project_root: Path, default_adapter: str = "") -> dict[str, Any]:
    case_executor = case.get("executor") or {}
    adapter = case_executor.get("adapter") or default_adapter or "manual-handoff"
    binding = _binding_for_adapter(project_root, adapter)
    return {
        "adapter": adapter,
        "enabled": bool(case_executor.get("enabled", binding.get("enabled", False))),
        "mode": case_executor.get("mode") or binding.get("mode") or "external_command",
        "command_template": case_executor.get("command_template") or binding.get("command_template") or "",
        "result_source": case_executor.get("result_source") or binding.get("result_source") or "stdout",
        "notes": case_executor.get("notes") or binding.get("notes") or [],
    }


def _render_command(template: str, context: dict[str, str]) -> str:
    quoted = {key: shlex.quote(value) for key, value in context.items()}
    return template.format_map(quoted)


def _normalize_result(data: dict[str, Any], *, case_id: str, adapter: str, command: str, result_file: Path) -> ExecutorRuntimeResult:
    return ExecutorRuntimeResult(
        case_id=data.get("case_id") or case_id,
        status=data.get("status") or "failed",
        summary=data.get("summary") or "",
        notes=data.get("notes") or "",
        tests_run=list(data.get("tests_run") or []),
        files_touched=list(data.get("files_touched") or []),
        commit_created=bool(data.get("commit_created", False)),
        commit_message=data.get("commit_message") or "",
        adapter=adapter,
        command=command,
        result_file=str(result_file),
    )


def invoke_executor_runtime(
    *,
    project_root: Path,
    task_name: str,
    case: dict[str, Any],
    cases_file: Path,
    bundle_file: Path,
    request_file: Path,
    result_file: Path,
    default_adapter: str = "",
) -> ExecutorRuntimeResult:
    case_id = case.get("id") or "unknown"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    executor = _resolve_case_executor(case, project_root, default_adapter)
    adapter = executor["adapter"]

    if executor["mode"] == "manual":
        return ExecutorRuntimeResult(
            case_id=case_id,
            status="blocked",
            summary=f"{adapter} requires manual handoff",
            notes="executor runtime is not enabled for this adapter",
            tests_run=[],
            files_touched=[],
            commit_created=False,
            commit_message="",
            adapter=adapter,
            command="",
            result_file=str(result_file),
        )

    if not executor["enabled"]:
        return ExecutorRuntimeResult(
            case_id=case_id,
            status="blocked",
            summary=f"{adapter} runtime binding is disabled",
            notes="enable the adapter binding in .awf/workflow.json before using executor runtime",
            tests_run=[],
            files_touched=[],
            commit_created=False,
            commit_message="",
            adapter=adapter,
            command="",
            result_file=str(result_file),
        )

    template = executor["command_template"]
    if not template:
        return ExecutorRuntimeResult(
            case_id=case_id,
            status="blocked",
            summary=f"{adapter} runtime command is missing",
            notes="configure command_template in .awf/workflow.json or override it in the case executor block",
            tests_run=[],
            files_touched=[],
            commit_created=False,
            commit_message="",
            adapter=adapter,
            command="",
            result_file=str(result_file),
        )

    command = _render_command(
        template,
        {
            "project_root": str(project_root),
            "task_name": task_name,
            "case_id": case_id,
            "case_title": case.get("title") or case_id,
            "cases_file": str(cases_file),
            "bundle_file": str(bundle_file),
            "request_file": str(request_file),
            "result_file": str(result_file),
            "adapter": adapter,
        },
    )
    completed = subprocess.run(
        command,
        shell=True,
        cwd=str(project_root),
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        return ExecutorRuntimeResult(
            case_id=case_id,
            status="failed",
            summary=f"{adapter} runtime command failed",
            notes=(completed.stderr or completed.stdout or "").strip()[-1000:],
            tests_run=[],
            files_touched=[],
            commit_created=False,
            commit_message="",
            adapter=adapter,
            command=command,
            result_file=str(result_file),
        )

    source = executor["result_source"]
    payload: dict[str, Any] | None = None
    if source == "file" or (source == "auto" and result_file.exists()):
        if result_file.exists():
            payload = _load_json(result_file)
    if payload is None:
        stdout = completed.stdout.strip()
        if stdout:
            payload = json.loads(stdout)

    if payload is None:
        return ExecutorRuntimeResult(
            case_id=case_id,
            status="failed",
            summary=f"{adapter} runtime produced no structured result",
            notes="expected executor_result JSON from stdout or result file",
            tests_run=[],
            files_touched=[],
            commit_created=False,
            commit_message="",
            adapter=adapter,
            command=command,
            result_file=str(result_file),
        )

    _write_json(result_file, payload)
    return _normalize_result(payload, case_id=case_id, adapter=adapter, command=command, result_file=result_file)


def build_executor_result(
    *,
    case_id: str,
    status: str,
    summary: str,
    notes: str,
    tests_run: list[str] | None = None,
    files_touched: list[str] | None = None,
    commit_created: bool = False,
    commit_message: str = "",
) -> dict[str, Any]:
    return {
        "version": 1,
        "case_id": case_id,
        "status": status,
        "summary": summary,
        "notes": notes,
        "tests_run": list(tests_run or []),
        "tests_passed": status == "completed",
        "files_touched": list(files_touched or []),
        "commit_created": commit_created,
        "commit_message": commit_message,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
