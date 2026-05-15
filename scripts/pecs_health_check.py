#!/usr/bin/env python3
"""
PECS Health Check Script
Performs installation root, dependency, and daemon launch diagnostics.
"""

import argparse
import sys
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run PECS installation health checks.")
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="Path to the workspace root to validate (default: current working directory).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    workspace_root = Path(args.workspace_root).resolve()
    # Import the health check logic from the main installer
    sys.path.insert(0, str(repo_root))
    try:
        from install_workspace_integration import health_check
    except ImportError:
        print(
            "ERROR: Could not import health_check from install_workspace_integration.py",
            file=sys.stderr,
        )
        sys.exit(2)
    results = health_check(workspace_root, repo_root, verbose=True)
    print(json.dumps(results, indent=2))
    if not results["install_root_stable"]:
        print("WARNING: Unstable install root detected.", file=sys.stderr)
    if any(v != "ok" for v in results["dependencies"].values()):
        print("ERROR: Missing dependencies.", file=sys.stderr)
        sys.exit(2)
    if not results["daemon_script_exists"]:
        print("ERROR: Daemon launch script missing.", file=sys.stderr)
        sys.exit(3)
    print("PECS installation health check passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
