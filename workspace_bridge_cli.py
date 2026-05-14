from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .install_workspace_integration import install_workspace


def _run_workspace_bridge(workspace_root: Path, command: str) -> None:
    bridge_runner = workspace_root / ".pecs" / "bridge" / "run_bridge.py"
    if not bridge_runner.exists():
        raise FileNotFoundError(
            f"Workspace bridge not installed: {bridge_runner}. Run init first."
        )

    subprocess.run(
        [
            sys.executable,
            str(bridge_runner),
            command,
            "--workspace",
            str(workspace_root),
        ],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Minimal PECS workspace bridge flow: init, refresh, validate"
    )
    parser.add_argument(
        "command",
        choices=["init", "refresh", "validate"],
        help="PECS workspace command",
    )
    parser.add_argument("workspace_root", help="Target workspace root path")
    parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root (defaults to this package directory)",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    if not workspace_root.exists():
        raise FileNotFoundError(f"Workspace does not exist: {workspace_root}")

    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if args.command == "init":
        install_workspace(workspace_root, repo_root)
        _run_workspace_bridge(workspace_root, "refresh")
        print(f"PECS initialized for workspace: {workspace_root}")
        return

    if args.command == "refresh":
        _run_workspace_bridge(workspace_root, "refresh")
        print(f"PECS continuity refreshed for workspace: {workspace_root}")
        return

    _run_workspace_bridge(workspace_root, "validate")
    print(f"PECS continuity validated for workspace: {workspace_root}")


if __name__ == "__main__":
    main()
