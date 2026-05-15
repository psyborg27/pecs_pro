from __future__ import annotations

import argparse
import json
from pathlib import Path

from export_workspace_continuity import export_workspace_continuity
from validate_workspace_continuity import validate_workspace_continuity


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Workspace-local PECS deterministic continuity bridge"
    )
    parser.add_argument(
        "command",
        choices=["refresh", "validate"],
        help="Bridge command to run",
    )
    parser.add_argument(
        "workspace_root",
        nargs="?",
        default=None,
        help="Workspace root path (default: current directory).",
    )
    parser.add_argument(
        "--workspace",
        dest="workspace_flag",
        default=None,
        help="Workspace root path.",
    )

    parser.add_argument(
        "--validate-deps",
        action="store_true",
        help="Validate required Python dependencies and exit",
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run installation health check and exit",
    )
    args = parser.parse_args()

    workspace_value = args.workspace_flag or args.workspace_root or "."
    workspace_root = Path(workspace_value).resolve()

    if args.command == "refresh":
        result = export_workspace_continuity(workspace_root)
    else:
        result = validate_workspace_continuity(workspace_root)

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
