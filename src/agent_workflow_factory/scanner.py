from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".turbo",
    ".pytest_cache",
    "__pycache__",
}


@dataclass
class RepoCapability:
    name: str
    path: str
    git: bool
    tech_stack: list[str]
    test_signals: list[str]
    docs: list[str]
    automation_signals: list[str]
    recommended_skills: list[str]


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def _discover_repo_roots(workspace: Path) -> list[Path]:
    repos: list[Path] = []

    if _is_git_repo(workspace):
        repos.append(workspace)

    for child in sorted(workspace.iterdir(), key=lambda item: item.name.lower()):
        if not child.is_dir() or child.name in IGNORE_DIRS:
            continue
        if _is_git_repo(child):
            repos.append(child)

    return repos


def _detect_from_package_json(repo: Path, tech_stack: set[str], test_signals: set[str], automation_signals: set[str]) -> None:
    package_files = [repo / "package.json"]
    package_files.extend(path for path in repo.glob("*/package.json") if path.parent.name not in IGNORE_DIRS)

    for package_json in package_files:
        if not package_json.exists():
            continue

        tech_stack.add("nodejs")

        data = _safe_read_json(package_json)
        deps = {
            **(data.get("dependencies") or {}),
            **(data.get("devDependencies") or {}),
        }
        scripts = data.get("scripts") or {}

        if "typescript" in deps:
            tech_stack.add("typescript")
        if "react" in deps:
            tech_stack.add("react")
        if "@tarojs/taro" in deps:
            tech_stack.add("taro")
            tech_stack.add("miniapp")
        if "next" in deps:
            tech_stack.add("nextjs")
        if "vue" in deps:
            tech_stack.add("vue")

        for name in scripts:
            lowered = name.lower()
            if "test" in lowered:
                test_signals.add(f"npm:{name}")
            if "e2e" in lowered:
                automation_signals.add(f"npm:{name}")
            if "build" in lowered:
                automation_signals.add(f"npm:{name}")


def _detect_from_go(repo: Path, tech_stack: set[str], test_signals: set[str]) -> None:
    if (repo / "go.mod").exists() or any(path.exists() for path in repo.glob("*/go.mod")):
        tech_stack.add("go")

    if list(repo.rglob("*_test.go")):
        test_signals.add("go:test-files")


def _detect_from_python(repo: Path, tech_stack: set[str], test_signals: set[str]) -> None:
    if (
        (repo / "pyproject.toml").exists()
        or (repo / "requirements.txt").exists()
        or any(path.exists() for path in repo.glob("*/pyproject.toml"))
    ):
        tech_stack.add("python")

    if (repo / "pytest.ini").exists() or (repo / ".pytest.ini").exists() or (repo / "tests").exists():
        test_signals.add("python:pytest-signals")


def _collect_docs(repo: Path) -> list[str]:
    docs: list[str] = []
    candidates = [
        "README.md",
        "AGENTS.md",
        "docs",
        ".cursor/docs",
        "tracking",
    ]
    for rel in candidates:
        path = repo / rel
        if path.exists():
            docs.append(rel)
    return docs


def _collect_automation_signals(repo: Path, current: set[str]) -> list[str]:
    if (repo / "scripts").exists():
        current.add("scripts/")
    if (repo / ".cursor").exists():
        current.add(".cursor/")
    if (repo / "Makefile").exists():
        current.add("Makefile")
    return sorted(current)


def _recommend_skills(tech_stack: set[str], docs: list[str], automation_signals: list[str]) -> list[str]:
    skills: list[str] = ["planning-with-files", "split-up-task", "task-manager"]

    if "go" in tech_stack:
        skills.append("go-backend-dev")
        skills.append("database-design")
    if "taro" in tech_stack or "miniapp" in tech_stack:
        skills.append("taro-frontend-dev")
    elif "react" in tech_stack or "nextjs" in tech_stack or "vue" in tech_stack:
        skills.append("frontend-design")
    if docs:
        skills.append("documentation")
    if any("e2e" in signal.lower() for signal in automation_signals):
        skills.append("miniapp-e2e-tester")

    deduped: list[str] = []
    for skill in skills:
        if skill not in deduped:
            deduped.append(skill)
    return deduped


def _scan_repo(repo: Path) -> RepoCapability:
    tech_stack: set[str] = set()
    test_signals: set[str] = set()
    automation_signals: set[str] = set()

    _detect_from_package_json(repo, tech_stack, test_signals, automation_signals)
    _detect_from_go(repo, tech_stack, test_signals)
    _detect_from_python(repo, tech_stack, test_signals)

    docs = _collect_docs(repo)
    automation = _collect_automation_signals(repo, automation_signals)
    skills = _recommend_skills(tech_stack, docs, automation)

    return RepoCapability(
        name=repo.name,
        path=str(repo),
        git=True,
        tech_stack=sorted(tech_stack),
        test_signals=sorted(test_signals),
        docs=docs,
        automation_signals=automation,
        recommended_skills=skills,
    )


def scan_workspace(workspace_input: str) -> dict[str, Any]:
    workspace = Path(workspace_input).expanduser().resolve()

    result: dict[str, Any] = {
        "workspace": str(workspace),
        "summary": {
            "exists": workspace.exists(),
            "is_dir": workspace.is_dir(),
            "repo_count": 0,
        },
        "repos": [],
        "recommended_skills": [],
        "notes": [],
    }

    if not workspace.exists():
        result["notes"].append("workspace does not exist")
        return result

    if not workspace.is_dir():
        result["notes"].append("workspace is not a directory")
        return result

    repos = _discover_repo_roots(workspace)
    scanned = [_scan_repo(repo) for repo in repos]

    all_skills: list[str] = []
    for repo in scanned:
        for skill in repo.recommended_skills:
            if skill not in all_skills:
                all_skills.append(skill)

    result["summary"]["repo_count"] = len(scanned)
    result["repos"] = [asdict(repo) for repo in scanned]
    result["recommended_skills"] = all_skills
    result["notes"].append("scanner MVP currently scans workspace root and first-level git repositories")
    result["notes"].append("scanner MVP currently infers stack from package.json, go.mod, pyproject.toml, tests, docs, and scripts")

    return result
