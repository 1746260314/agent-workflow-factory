#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

run_cli() {
  PYTHONPATH="$ROOT_DIR/src" "$PYTHON_BIN" -m agent_workflow_factory.cli "$@"
}

usage() {
  cat <<'EOF'
Usage:
  ./start.sh help
  ./start.sh scan <workspace>
  ./start.sh scaffold <workspace> [output] [project_name] [task_name]
  ./start.sh plan <project> <goal> <scope> [task_name]
  ./start.sh run-loop <project> <cases_file>
  ./start.sh status <project> <cases_file>

Examples:
  ./start.sh scan /Users/me/projects/my-app
  ./start.sh scaffold /Users/me/projects/my-app
  ./start.sh plan /Users/me/projects/my-app "开发一个新的首页功能模块" "首页和公共组件"
  ./start.sh run-loop /Users/me/projects/my-app /Users/me/projects/my-app/tracking/homepage-feature/loop_cases.json
  ./start.sh status /Users/me/projects/my-app /Users/me/projects/my-app/tracking/homepage-feature/loop_cases.json
EOF
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  help|-h|--help)
    usage
    ;;
  scan)
    workspace="${1:?workspace is required}"
    run_cli scan --workspace "$workspace"
    ;;
  scaffold)
    workspace="${1:?workspace is required}"
    output="${2:-$workspace}"
    project_name="${3:-$(basename "$workspace")}"
    task_name="${4:-initial-delivery}"
    run_cli scaffold --workspace "$workspace" --output "$output" --project-name "$project_name" --task-name "$task_name"
    ;;
  plan)
    project="${1:?project is required}"
    goal="${2:?goal is required}"
    scope="${3:?scope is required}"
    task_name="${4:-}"
    if [ -n "$task_name" ]; then
      run_cli plan --project "$project" --goal "$goal" --scope "$scope" --task-name "$task_name"
    else
      run_cli plan --project "$project" --goal "$goal" --scope "$scope"
    fi
    ;;
  run-loop)
    project="${1:?project is required}"
    cases_file="${2:?cases_file is required}"
    run_cli run-loop --project "$project" --cases-file "$cases_file"
    ;;
  status)
    project="${1:?project is required}"
    cases_file="${2:?cases_file is required}"
    run_cli status --project "$project" --cases-file "$cases_file"
    ;;
  *)
    echo "unknown command: $cmd" >&2
    usage
    exit 1
    ;;
esac
