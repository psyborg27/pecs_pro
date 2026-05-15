#!/usr/bin/env bash
echo "Workspace integration installed."
echo "Run task 'PECS: Start Daemon' in VS Code, or run:"
echo "PECS_PRO_REPO=\"$SCRIPT_DIR\" \"$SCRIPT_DIR/launch_pecs_daemon.sh\" \"$WORKSPACE_ROOT\""

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <workspace-root>"
  exit 1
fi

WORKSPACE_ROOT="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Install-root safety checks ---
UNSTABLE_ROOT=0
case "$SCRIPT_DIR" in
  *Downloads*|*Desktop*|/tmp/*|/private/tmp/*|/Volumes/*)
    echo "WARNING: PECS is being installed from an unstable or transient location: $SCRIPT_DIR" >&2
    echo "It is strongly recommended to install PECS in a stable, user-owned directory such as ~/Developer/PECS or ~/Applications/PECS." >&2
    UNSTABLE_ROOT=1
    ;;
esac

# --- Activate venv if present ---
cd "$WORKSPACE_ROOT"
if [[ -f ".venv/bin/activate" ]]; then
  source ".venv/bin/activate"
fi

# --- Runtime dependency guarantee ---
echo "Checking required Python runtime dependencies..."
PYTHON_EXEC="python3"
if command -v python &>/dev/null; then
  PYTHON_EXEC="python"
fi

DEPENDENCIES=(watchdog)
MISSING_DEPS=()
for dep in "${DEPENDENCIES[@]}"; do
  if ! "$PYTHON_EXEC" -c "import $dep" 2>/dev/null; then
    MISSING_DEPS+=("$dep")
  fi
done

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
  echo "Missing required dependencies: ${MISSING_DEPS[*]}"
  echo "Attempting to install missing dependencies into the current environment..."
  "$PYTHON_EXEC" -m pip install "${MISSING_DEPS[@]}" || {
    echo "ERROR: Failed to install required dependencies: ${MISSING_DEPS[*]}" >&2
    echo "Please ensure your Python environment is writable and try again." >&2
    exit 2
  }
  echo "Dependencies installed: ${MISSING_DEPS[*]}"
else
  echo "All required dependencies are present."
fi

# --- Proceed with integration ---
python3 "$SCRIPT_DIR/install_workspace_integration.py" "$WORKSPACE_ROOT" --repo-root "$SCRIPT_DIR"

echo "Workspace integration installed."
if [[ $UNSTABLE_ROOT -eq 1 ]]; then
  echo "WARNING: PECS was installed from an unstable location. Move to a stable directory for persistent use." >&2
fi
echo "Run task 'PECS: Start Daemon' in VS Code, or run:"
echo "PECS_PRO_REPO=\"$SCRIPT_DIR\" \"$SCRIPT_DIR/launch_pecs_daemon.sh\" \"$WORKSPACE_ROOT\""
