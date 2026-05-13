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

export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"

PID_FILE="$WORKSPACE_ROOT/.pecs/daemon.pid"
if [[ -f "$PID_FILE" ]]; then
  pid=$(<"$PID_FILE")
  if [[ "$pid" =~ ^[0-9]+$ ]]; then
    if kill -0 "$pid" 2>/dev/null; then
      echo "PECS daemon is already running for workspace: $WORKSPACE_ROOT (pid=$pid)"
      exit 0
    fi
  fi
fi

python3 -m pecs_pro.run_pecs_daemon "$WORKSPACE_ROOT"
