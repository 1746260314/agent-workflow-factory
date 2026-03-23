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


def _load_state(root: Path) -> dict[str, Any]:
    state_path = root / ".awf" / "state.json"
    if not state_path.exists():
        return {"sync_recovery": {}}
    return _load_json(state_path)


def _write_state(root: Path, data: dict[str, Any]) -> None:
    _write_json(root / ".awf" / "state.json", data)


def _find_next_case(cases: list[dict[str, Any]]) -> dict[str, Any] | None:
    for case in cases:
        if case.get("status") == "pending":
            return case
    return None


def _find_case(cases: list[dict[str, Any]], case_id: str) -> dict[str, Any] | None:
    for case in cases:
        if case.get("id") == case_id:
            return case
    return None


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
    )


def _is_git_repo(root: Path) -> bool:
    probe = _git(["rev-parse", "--is-inside-work-tree"], root)
    return probe.returncode == 0 and probe.stdout.strip() == "true"


def _worktree_is_clean(root: Path) -> bool:
    status = _git(["status", "--porcelain"], root)
    if status.returncode != 0:
        return False
    lines = [line for line in status.stdout.splitlines() if line.strip()]
    if not lines:
        return True

    allowed_prefixes = ("tracking/", ".awf/")
    for line in lines:
        path_part = line[3:] if len(line) > 3 else ""
        if "->" in path_part:
            path_part = path_part.split("->", 1)[1].strip()
        normalized = path_part.strip()
        if normalized.startswith(allowed_prefixes):
            continue
        return False
    return True


def _has_remote(root: Path) -> bool:
    remote = _git(["remote"], root)
    return remote.returncode == 0 and bool(remote.stdout.strip())


def _current_branch(root: Path) -> str:
    branch = _git(["branch", "--show-current"], root)
    if branch.returncode != 0:
        return ""
    return branch.stdout.strip()


def _build_result(
    case_id: str,
    status: str,
    summary: str,
    tests_run: list[str],
    notes: str,
    files_touched: list[str],
    *,
    git_sync_performed: bool = False,
    git_push_attempted: bool = False,
    git_push_succeeded: bool = False,
    commit_created: bool = False,
    commit_message: str = "",
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "status": status,
        "summary": summary,
        "tests_run": tests_run,
        "tests_passed": status == "completed",
        "commit_created": commit_created,
        "commit_message": commit_message,
        "files_touched": files_touched,
        "notes": notes,
        "git_sync_performed": git_sync_performed,
        "git_push_attempted": git_push_attempted,
        "git_push_succeeded": git_push_succeeded,
    }


def _persist_result(cases_path: Path, case_id: str, result: dict[str, Any]) -> str:
    result_path = cases_path.parent / "runs" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{case_id}.result.json"
    _write_json(result_path, result)
    return str(result_path)


def _sync_key(root: Path, branch: str, action: str, case_id: str) -> str:
    return f"{root}:{branch}:{action}:{case_id}"


def _ensure_recovery_case(cases: list[dict[str, Any]], *, blocked_case_id: str, action: str, attempt: int, manual: bool = False) -> None:
    target_id = "git_sync_manual_intervention" if manual else "git_sync_recovery"
    title = "人工介入处理 Git 同步问题" if manual else "处理 Git 同步问题"
    goal = (
        f"人工处理 {blocked_case_id} 的 {action} 同步失败问题"
        if manual
        else f"恢复 {blocked_case_id} 的 {action} 同步问题"
    )
    existing = _find_case(cases, target_id)
    payload = {
        "id": target_id,
        "title": title,
        "status": "pending",
        "goal": goal,
        "commands": [],
        "tests": [],
        "notes": [f"source_case={blocked_case_id}", f"action={action}", f"attempt={attempt}"],
        "history": [],
    }
    if existing is not None:
        existing.update(payload)
        return
    cases.insert(0, payload)


def _note_map(case: dict[str, Any]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for item in case.get("notes") or []:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        mapped[key] = value
    return mapped


def _handle_sync_failure(
    *,
    root: Path,
    payload: dict[str, Any],
    current_case: dict[str, Any],
    action: str,
    branch: str,
    stdout: str,
    stderr: str,
    keep_pending: bool,
    max_retries: int,
) -> tuple[str, str]:
    cases = payload.get("cases") or []
    state = _load_state(root)
    bucket = state.setdefault("sync_recovery", {})
    key = _sync_key(root, branch, action, current_case["id"])
    attempt = int(bucket.get(key, 0)) + 1
    bucket[key] = attempt

    current_case["status"] = "pending" if keep_pending else "sync_pending"
    current_case.setdefault("history", []).append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "status": "sync_pending",
            "action": action,
            "attempt": attempt,
            "stdout": stdout[-1000:],
            "stderr": stderr[-1000:],
        }
    )

    manual = attempt > max_retries
    _ensure_recovery_case(
        cases,
        blocked_case_id=current_case["id"],
        action=action,
        attempt=attempt,
        manual=manual,
    )

    _write_state(root, state)
    return ("manual intervention required for git sync failure" if manual else f"{action} failed; recovery case inserted", current_case["status"])


def _attempt_recovery(
    *,
    root: Path,
    payload: dict[str, Any],
    recovery_case: dict[str, Any],
    branch: str,
    max_retries: int,
) -> tuple[str, str]:
    notes = _note_map(recovery_case)
    source_case_id = notes.get("source_case", "")
    action = notes.get("action", "")
    if not source_case_id or not action:
        recovery_case["status"] = "blocked"
        return ("recovery case missing source metadata", "blocked")

    source_case = _find_case(payload.get("cases") or [], source_case_id)
    if source_case is None:
        recovery_case["status"] = "blocked"
        return ("source case not found for recovery", "blocked")

    state = _load_state(root)
    bucket = state.setdefault("sync_recovery", {})
    key = _sync_key(root, branch, action, source_case_id)
    attempt = int(bucket.get(key, 0)) + 1
    bucket[key] = attempt

    cmd = ["pull", "--ff-only", "origin", branch] if action == "git_pull" else ["push", "origin", branch]
    executed = _git(cmd, root)
    if executed.returncode != 0:
        manual = attempt > max_retries
        recovery_case["status"] = "blocked" if not manual else "completed"
        recovery_case.setdefault("history", []).append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "status": "failed",
                "attempt": attempt,
                "action": action,
                "stdout": executed.stdout[-1000:],
                "stderr": executed.stderr[-1000:],
            }
        )
        if manual:
            _ensure_recovery_case(
                payload.get("cases") or [],
                blocked_case_id=source_case_id,
                action=action,
                attempt=attempt,
                manual=True,
            )
            source_case["status"] = "sync_pending"
        _write_state(root, state)
        return ("manual intervention required for git sync failure" if manual else f"{action} recovery failed", "blocked")

    recovery_case["status"] = "completed"
    recovery_case.setdefault("history", []).append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "status": "completed",
            "attempt": attempt,
            "action": action,
        }
    )
    if action == "git_push":
        source_case["status"] = "completed"
        source_case.setdefault("history", []).append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "status": "completed",
                "notes": "completed after git push recovery",
            }
        )
    else:
        source_case["status"] = "pending"
        source_case.setdefault("history", []).append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "status": "pending",
                "notes": "returned to pending after git pull recovery",
            }
        )
    if key in bucket:
        del bucket[key]
    _write_state(root, state)
    return (f"{action} recovery succeeded", "completed")


def run_loop_once(project_root: str, cases_file: str) -> LoopRunResult:
    root = Path(project_root).expanduser().resolve()
    cases_path = Path(cases_file).expanduser().resolve()
    payload = _load_json(cases_path)
    cases = payload.get("cases") or []
    loop_policy = payload.get("loop_policy") or {}
    max_sync_retries = int(loop_policy.get("max_sync_retries", 2))

    current_case = _find_next_case(cases)
    if current_case is None:
        result = _build_result(
            "none",
            "skipped",
            "no pending case",
            [],
            "all cases are already resolved",
            [str(cases_path)],
        )
        result_path = _persist_result(cases_path, "no-case", result)
        return LoopRunResult("none", "skipped", result_path, [], result["notes"])

    files_touched = [str(cases_path)]
    tests_run: list[str] = []
    case_id = current_case["id"]
    current_case["status"] = "in_progress"

    git_enabled = _is_git_repo(root)
    branch = _current_branch(root) if git_enabled else ""
    do_pull = bool(loop_policy.get("git_pull_before_case")) and git_enabled and _has_remote(root)
    do_push = bool(loop_policy.get("git_push_after_case")) and git_enabled and _has_remote(root)

    if case_id == "git_sync_manual_intervention":
        current_case["status"] = "blocked"
        current_case.setdefault("history", []).append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "status": "blocked",
                "notes": "manual intervention required",
            }
        )
        _write_json(cases_path, payload)
        result = _build_result(
            case_id,
            "blocked",
            current_case.get("title", case_id),
            [],
            "manual intervention required",
            files_touched,
        )
        result_path = _persist_result(cases_path, case_id, result)
        return LoopRunResult(case_id, "blocked", result_path, [], result["notes"])

    if case_id == "git_sync_recovery":
        note, status = _attempt_recovery(
            root=root,
            payload=payload,
            recovery_case=current_case,
            branch=branch,
            max_retries=max_sync_retries,
        )
        _write_json(cases_path, payload)
        result = _build_result(
            case_id,
            "completed" if status == "completed" else "blocked",
            current_case.get("title", case_id),
            [],
            note,
            files_touched,
            git_sync_performed=True,
        )
        result_path = _persist_result(cases_path, case_id, result)
        return LoopRunResult(case_id, result["status"], result_path, [], result["notes"])

    if git_enabled and not _worktree_is_clean(root):
        current_case["status"] = "blocked"
        current_case.setdefault("history", []).append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "status": "blocked",
                "notes": "git worktree is not clean",
            }
        )
        _write_json(cases_path, payload)
        result = _build_result(
            case_id,
            "blocked",
            current_case.get("title", case_id),
            [],
            "git worktree is not clean",
            files_touched,
        )
        result_path = _persist_result(cases_path, case_id, result)
        return LoopRunResult(case_id, "blocked", result_path, [], result["notes"])

    if do_pull and branch:
        pulled = _git(["pull", "--ff-only", "origin", branch], root)
        if pulled.returncode != 0:
            note, _ = _handle_sync_failure(
                root=root,
                payload=payload,
                current_case=current_case,
                action="git_pull",
                branch=branch,
                stdout=pulled.stdout,
                stderr=pulled.stderr,
                keep_pending=True,
                max_retries=max_sync_retries,
            )
            _write_json(cases_path, payload)
            result = _build_result(
                case_id,
                "blocked",
                current_case.get("title", case_id),
                [],
                note,
                files_touched,
                git_sync_performed=True,
            )
            result_path = _persist_result(cases_path, case_id, result)
            return LoopRunResult(case_id, "blocked", result_path, [], result["notes"])

    commands = current_case.get("commands") or []
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
        result = _build_result(
            case_id,
            "blocked",
            current_case.get("title", case_id),
            [],
            "no commands configured for this case",
            files_touched,
            git_sync_performed=do_pull,
        )
        result_path = _persist_result(cases_path, case_id, result)
        return LoopRunResult(case_id, "blocked", result_path, [], result["notes"])

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
            result = _build_result(
                case_id,
                "failed",
                current_case.get("title", case_id),
                tests_run,
                f"command failed: {command}",
                files_touched,
                git_sync_performed=do_pull,
            )
            result_path = _persist_result(cases_path, case_id, result)
            return LoopRunResult(case_id, "failed", result_path, tests_run, result["notes"])

    if do_push and branch:
        pushed = _git(["push", "origin", branch], root)
        if pushed.returncode != 0:
            note, _ = _handle_sync_failure(
                root=root,
                payload=payload,
                current_case=current_case,
                action="git_push",
                branch=branch,
                stdout=pushed.stdout,
                stderr=pushed.stderr,
                keep_pending=False,
                max_retries=max_sync_retries,
            )
            _write_json(cases_path, payload)
            result = _build_result(
                case_id,
                "blocked",
                current_case.get("title", case_id),
                tests_run,
                note,
                files_touched,
                git_sync_performed=do_pull,
                git_push_attempted=True,
                git_push_succeeded=False,
            )
            result_path = _persist_result(cases_path, case_id, result)
            return LoopRunResult(case_id, "blocked", result_path, tests_run, result["notes"])

    current_case["status"] = "completed"
    current_case.setdefault("history", []).append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "status": "completed",
            "commands": commands,
            "git_pull": do_pull,
            "git_push": do_push,
        }
    )
    if git_enabled and branch:
        state = _load_state(root)
        bucket = state.setdefault("sync_recovery", {})
        for action in ("git_pull", "git_push"):
            key = _sync_key(root, branch, action, case_id)
            if key in bucket:
                del bucket[key]
        _write_state(root, state)
    _write_json(cases_path, payload)

    result = _build_result(
        case_id,
        "completed",
        current_case.get("title", case_id),
        tests_run,
        "commands completed successfully",
        files_touched,
        git_sync_performed=do_pull,
        git_push_attempted=do_push,
        git_push_succeeded=do_push,
    )
    result_path = _persist_result(cases_path, case_id, result)
    return LoopRunResult(case_id, "completed", result_path, tests_run, result["notes"])
