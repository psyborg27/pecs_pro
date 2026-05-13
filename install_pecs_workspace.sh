#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <workspace-root>"
  exit 1
fi

WORKSPACE_ROOT="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$WORKSPACE_ROOT"
if [[ -f ".venv/bin/activate" ]]; then
  # Keep workspace-local Python environment active when present.
  source ".venv/bin/activate"
fi

python3 "$SCRIPT_DIR/install_workspace_integration.py" "$WORKSPACE_ROOT" --repo-root "$SCRIPT_DIR"

echo "Workspace integration installed."
echo "Run task 'PECS: Start Daemon' in VS Code, or run:"
echo "PECS_PRO_REPO=\"$SCRIPT_DIR\" \"$SCRIPT_DIR/launch_pecs_daemon.sh\" \"$WORKSPACE_ROOT\""
