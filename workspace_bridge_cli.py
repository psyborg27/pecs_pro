from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

from install_workspace_integration import install_workspace
from workspace_assets_manager import WorkspaceAssetsManager

logger = logging.getLogger(__name__)


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


def _load_json(path: Path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _setup_logging(verbose: bool) -> None:
    """Setup logging for CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def _cmd_init(args: argparse.Namespace) -> None:
    """Initialize PECS workspace (legacy command)."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        install_workspace(workspace_root, repo_root)
        _run_workspace_bridge(workspace_root, "refresh")
        logger.info(f"PECS initialized for workspace: {workspace_root}")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)


def _cmd_install_workspace_assets(args: argparse.Namespace) -> None:
    """Install PECS workspace assets."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        manager = WorkspaceAssetsManager(repo_root, workspace_root)
        result = manager.install_assets(upgrade=args.upgrade, verify=True)

        logger.info(f"Status: {result['status']}")
        logger.info(f"Installed: {len(result.get('installed_assets', []))} asset(s)")

        if result.get("errors"):
            for error in result["errors"]:
                logger.error(f"  - {error}")
            sys.exit(1)

        logger.info("Applying PECS workspace integration configuration")
        install_workspace(workspace_root, repo_root)

        logger.info("Workspace assets installed successfully")

    except Exception as e:
        logger.error(f"Asset installation failed: {e}")
        sys.exit(1)


def _cmd_verify_workspace(args: argparse.Namespace) -> None:
    """Verify PECS workspace installation."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        manager = WorkspaceAssetsManager(repo_root, workspace_root)
        result = manager.verify_installation()

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            logger.info(f"Verification: {'PASSED' if result['valid'] else 'FAILED'}")

            for asset, exists in result.get("checks", {}).items():
                status = "✓" if exists else "✗"
                logger.info(f"  {status} {asset}")

            if result.get("errors"):
                logger.error("Errors found:")
                for error in result["errors"]:
                    logger.error(f"  - {error}")

        sys.exit(0 if result["valid"] else 1)

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        sys.exit(1)


def _cmd_repair_workspace(args: argparse.Namespace) -> None:
    """Repair broken PECS workspace installation."""
    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        manager = WorkspaceAssetsManager(repo_root, workspace_root)
        result = manager.repair_installation()

        logger.info(f"Repair status: {result['status']}")
        logger.info(f"Repaired: {len(result.get('repairs', []))} item(s)")

        if result.get("repairs"):
            for repair in result["repairs"]:
                logger.info(f"  ✓ {repair}")

        if result.get("errors"):
            logger.warning("Repair encountered errors:")
            for error in result["errors"]:
                logger.warning(f"  - {error}")

        sys.exit(0 if result["status"] != "failed" else 1)

    except Exception as e:
        logger.error(f"Repair failed: {e}")
        sys.exit(1)


def _cmd_status(args: argparse.Namespace) -> None:
    """Show PECS daemon and workspace status."""
    workspace_root = (
        Path(args.workspace_root).resolve() if args.workspace_root else Path.cwd()
    )

    try:
        if not workspace_root.exists():
            logger.error(f"Workspace does not exist: {workspace_root}")
            sys.exit(1)

        daemon_pid_file = workspace_root / ".pecs" / "daemon.pid"

        if not daemon_pid_file.exists():
            logger.info(f"Workspace: {workspace_root}")
            logger.info("Daemon: NOT RUNNING (no PID file)")
            return

        try:
            pid = int(daemon_pid_file.read_text().strip())
            # Check if process exists
            subprocess.run(["kill", "-0", str(pid)], check=True, capture_output=True)
            logger.info(f"Workspace: {workspace_root}")
            logger.info(f"Daemon: RUNNING (PID {pid})")
        except (ValueError, subprocess.CalledProcessError):
            logger.info(f"Workspace: {workspace_root}")
            logger.info("Daemon: STOPPED (stale PID file)")

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        sys.exit(1)


def _cmd_doctor(args: argparse.Namespace) -> None:
    """Diagnose PECS installation and environment."""
    workspace_root = (
        Path(args.workspace_root).resolve() if args.workspace_root else Path.cwd()
    )
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    try:
        logger.info("PECS Diagnostics Report")
        logger.info("=" * 60)

        # Check environment
        logger.info(f"Python: {sys.executable}")
        logger.info(f"PECS Repository: {repo_root}")
        logger.info(f"Workspace: {workspace_root}")

        if not workspace_root.exists():
            logger.error(f"Workspace does not exist: {workspace_root}")
            sys.exit(1)

        # Check assets
        logger.info("\nAssets:")
        required_files = [
            ".pecs/README.md",
            ".pecs/tools/append_ai_chat_history.py",
            ".pecs/bridge/run_bridge.py",
            ".github/copilot-instructions.md",
            ".continue/rules/pecs-first-routing.yaml",
            ".vscode/tasks.json",
        ]

        for file_path in required_files:
            full_path = workspace_root / file_path
            exists = full_path.exists()
            status = "✓" if exists else "✗"
            logger.info(f"  {status} {file_path}")

        # Check daemon
        logger.info("\nDaemon:")
        daemon_pid_file = workspace_root / ".pecs" / "daemon.pid"
        if daemon_pid_file.exists():
            try:
                pid = int(daemon_pid_file.read_text().strip())
                subprocess.run(
                    ["kill", "-0", str(pid)], check=True, capture_output=True
                )
                logger.info(f"  ✓ Running (PID {pid})")
            except:
                logger.info(f"  ✗ Stale PID file (PID {pid} not running)")
        else:
            logger.info("  ✗ Not running")

        # Check venv
        logger.info("\nVirtual Environment:")
        venv_path = workspace_root / ".venv"
        if venv_path.exists():
            logger.info(f"  ✓ Found: {venv_path}")
        else:
            logger.info("  - Not found (optional)")

        # Continuity health checks
        logger.info("\nContinuity Health:")
        active_context = _load_json(
            workspace_root / ".pecs" / "active_context.json", {}
        )
        locality_state = _load_json(
            workspace_root / ".pecs" / "locality_index.json", {}
        )
        continuity_topology = _load_json(
            workspace_root / ".pecs" / "continuity" / "active_topology.json", {}
        )
        continuity_locality_state = _load_json(
            workspace_root / ".pecs" / "continuity" / "locality_state.json", {}
        )

        active_size = (
            len(active_context.get("activated_objects", []))
            if isinstance(active_context, dict)
            else 0
        )
        cluster_count = (
            len(continuity_locality_state.get("active_locality_clusters", []))
            if isinstance(continuity_locality_state, dict)
            else 0
        )
        touched_count = (
            len(continuity_locality_state.get("active_runtime_touched_files", []))
            if isinstance(continuity_locality_state, dict)
            else 0
        )
        confirmation = float(
            continuity_topology.get("runtime_validation", {}).get(
                "runtime_confirmation_density", 0.0
            )
            if isinstance(continuity_topology, dict)
            else 0.0
        )

        logger.info(f"  Active context objects: {active_size}")
        logger.info(f"  Active locality clusters: {cluster_count}")
        logger.info(f"  Active runtime touched files: {touched_count}")
        logger.info(f"  Runtime confirmation density: {confirmation:.3f}")

        projection_path = workspace_root / ".pecs" / "pecs_lite_runtime_projection.json"
        if projection_path.exists():
            projection = _load_json(projection_path, {})
            runtime_targets = projection.get("runtime_targets", [])
            wrapper_warning = projection.get("wrapper_warning")
            authority_violation = any(
                str(path).startswith(".pecs/")
                for path in runtime_targets
                if isinstance(path, str)
            )
            logger.info("\nPECS-LITE Projection:")
            logger.info(f"  ✓ Projection file found: {projection_path}")
            logger.info(f"  Runtime targets: {len(runtime_targets)}")
            logger.info(f"  Wrapper warning: {wrapper_warning}")
            logger.info(
                f"  Authority violation: {'YES' if authority_violation else 'NO'}"
            )
        else:
            logger.info("\nPECS-LITE Projection:")
            logger.info(
                "  ✗ Projection file missing: .pecs/pecs_lite_runtime_projection.json"
            )

        logger.info("\n" + "=" * 60)

    except Exception as e:
        logger.error(f"Diagnostic failed: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="PECS workspace management CLI")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Legacy init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize PECS workspace (legacy)"
    )
    init_parser.add_argument("workspace_root", help="Target workspace root path")
    init_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    init_parser.set_defaults(func=_cmd_init)

    # New commands
    install_parser = subparsers.add_parser(
        "install-workspace-assets", help="Install PECS workspace assets"
    )
    install_parser.add_argument("workspace_root", help="Target workspace root path")
    install_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    install_parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Preserve existing user configuration",
    )
    install_parser.set_defaults(func=_cmd_install_workspace_assets)

    verify_parser = subparsers.add_parser(
        "verify-workspace", help="Verify workspace installation"
    )
    verify_parser.add_argument("workspace_root", help="Target workspace root path")
    verify_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    verify_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    verify_parser.set_defaults(func=_cmd_verify_workspace)

    repair_parser = subparsers.add_parser(
        "repair-workspace", help="Repair broken workspace installation"
    )
    repair_parser.add_argument("workspace_root", help="Target workspace root path")
    repair_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    repair_parser.set_defaults(func=_cmd_repair_workspace)

    status_parser = subparsers.add_parser(
        "status", help="Show daemon and workspace status"
    )
    status_parser.add_argument(
        "workspace_root",
        nargs="?",
        default="",
        help="Target workspace root path (default: current directory)",
    )
    status_parser.set_defaults(func=_cmd_status)

    doctor_parser = subparsers.add_parser(
        "doctor", help="Diagnose PECS installation and environment"
    )
    doctor_parser.add_argument(
        "workspace_root",
        nargs="?",
        default="",
        help="Target workspace root path (default: current directory)",
    )
    doctor_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    doctor_parser.set_defaults(func=_cmd_doctor)

    # Legacy refresh command
    refresh_parser = subparsers.add_parser(
        "refresh", help="Refresh continuity state (legacy)"
    )
    refresh_parser.add_argument("workspace_root", help="Target workspace root path")
    refresh_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    refresh_parser.set_defaults(func=lambda args: _cmd_init(args))

    # Legacy validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate continuity (legacy)"
    )
    validate_parser.add_argument("workspace_root", help="Target workspace root path")
    validate_parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root",
    )
    validate_parser.set_defaults(func=lambda args: _cmd_init(args))

    args = parser.parse_args()

    _setup_logging(args.verbose)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
