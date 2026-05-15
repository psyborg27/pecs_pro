#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config/install_root.json"
INSTALL_ROOT=""

if [[ -f "$CONFIG_FILE" ]]; then
  INSTALL_ROOT="$(python3 - "$CONFIG_FILE" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
try:
    data = json.loads(path.read_text(encoding='utf-8'))
    print(data.get('install_root', ''))
except Exception:
    pass
PY
)"
fi

if [[ -n "$INSTALL_ROOT" && -f "$INSTALL_ROOT/.venv/bin/activate" ]]; then
  source "$INSTALL_ROOT/.venv/bin/activate"
fi

if command -v pecs-pro-daemon >/dev/null 2>&1; then
  pecs-pro-daemon "$WORKSPACE_ROOT"
else
  python3 -m pecs_pro.run_pecs_daemon "$WORKSPACE_ROOT"
fi
