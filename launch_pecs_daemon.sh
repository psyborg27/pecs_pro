#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="${1:-.}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "${PECS_PRO_REPO:-}" ]]; then
  REPO_ROOT="${PECS_PRO_REPO}"
fi

# --- Install-root safety check ---
case "$REPO_ROOT" in
  *Downloads*|*Desktop*|/tmp/*|/private/tmp/*|/Volumes/*)
    echo "WARNING: PECS is being launched from an unstable or transient location: $REPO_ROOT" >&2
    echo "It is strongly recommended to install PECS in a stable, user-owned directory such as ~/Developer/PECS or ~/Applications/PECS." >&2
    ;;
esac

if [[ ! -d "$REPO_ROOT" ]]; then
  echo "PECS repository not found: $REPO_ROOT" >&2
  exit 1
fi

CENTRAL_VENV="$REPO_ROOT/.venv"
CENTRAL_PYTHON="$CENTRAL_VENV/bin/python"
if [[ ! -x "$CENTRAL_PYTHON" ]]; then
  echo "ERROR: PECS venv Python not found at: $CENTRAL_PYTHON" >&2
  echo "Ensure PECS runtime is installed in the repository venv and try again." >&2
  echo "Example: cd \"$REPO_ROOT\" && python3 -m venv .venv && .venv/bin/python -m pip install -e . watchdog" >&2
  exit 2
fi

source "$CENTRAL_VENV/bin/activate"

export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"

echo "PECS runtime environment: $CENTRAL_PYTHON"
echo "PECS install root: $REPO_ROOT"
echo "Target workspace root: $WORKSPACE_ROOT"

# --- Dependency health check ---
if ! "$CENTRAL_PYTHON" "$REPO_ROOT/scripts/pecs_health_check.py" --workspace-root "$WORKSPACE_ROOT"; then
  echo "ERROR: PECS health check failed. Resolve issues before launching the daemon." >&2
  exit 2
fi

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

"$CENTRAL_PYTHON" -m run_pecs_daemon "$WORKSPACE_ROOT"
