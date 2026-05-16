#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
WORKSPACE_ROOT="${1:-$PWD}"

if [[ ! -d "$WORKSPACE_ROOT" ]]; then
  echo "ERROR: Workspace root does not exist: $WORKSPACE_ROOT" >&2
  exit 1
fi

cd "$REPO_ROOT"

PYTHON_CMD="python3"
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  PYTHON_CMD="python"
fi
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  echo "ERROR: Python is not available on PATH." >&2
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  echo "Creating Python virtual environment in .venv..."
  "$PYTHON_CMD" -m venv .venv
fi

VENV_PYTHON="$REPO_ROOT/.venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "ERROR: Virtual environment python not found at $VENV_PYTHON" >&2
  exit 1
fi

echo "Upgrading pip, setuptools, and wheel..."
"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel

if [[ -f "requirements.txt" ]]; then
  echo "Installing required dependencies..."
  "$VENV_PYTHON" -m pip install -r requirements.txt
fi

echo "Installing PECS-PRO in editable mode..."
"$VENV_PYTHON" -m pip install -e .

echo "Bootstrapping workspace: $WORKSPACE_ROOT"
"$VENV_PYTHON" -m workspace_bridge_cli bootstrap-workspace "$WORKSPACE_ROOT" --repo-root "$REPO_ROOT" --upgrade

echo "PECS onboarding completed successfully."
echo "Run: $VENV_PYTHON -m workspace_bridge_cli status \"$WORKSPACE_ROOT\""