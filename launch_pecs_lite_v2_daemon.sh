#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="${1:-.}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "${PECS_PRO_REPO:-}" ]]; then
  REPO_ROOT="${PECS_PRO_REPO}"
fi

if [[ ! -d "$REPO_ROOT" ]]; then
  echo "PECS repository not found: $REPO_ROOT" >&2
  exit 1
fi

CENTRAL_VENV="$REPO_ROOT/.venv"
CENTRAL_PYTHON="$CENTRAL_VENV/bin/python"
if [[ ! -x "$CENTRAL_PYTHON" ]]; then
  echo "ERROR: PECS venv Python not found at: $CENTRAL_PYTHON" >&2
  echo "Ensure PECS runtime is installed in the repository venv and try again." >&2
  echo "Example: cd \"$REPO_ROOT\" && python3 -m venv .venv && \"$CENTRAL_PYTHON\" -m pip install -e ." >&2
  exit 2
fi

mkdir -p "$WORKSPACE_ROOT/.pecs"
PID_FILE="$WORKSPACE_ROOT/.pecs/daemon_lite_v2.pid"

if [[ -f "$PID_FILE" ]]; then
  pid=$(<"$PID_FILE")
  if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
    echo "PECS Lite v2 daemon already running for workspace: $WORKSPACE_ROOT (pid=$pid)"
    exit 0
  fi
fi

cleanup_pid() {
  rm -f "$PID_FILE"
}

trap cleanup_pid EXIT

export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"
"$CENTRAL_PYTHON" -m run_pecs_lite_v2_daemon "$WORKSPACE_ROOT" &
daemon_pid=$!

echo "$daemon_pid" > "$PID_FILE"
echo "PECS Lite v2 daemon started for workspace: $WORKSPACE_ROOT (pid=$daemon_pid)"

wait "$daemon_pid"
