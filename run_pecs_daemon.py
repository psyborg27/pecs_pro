from __future__ import annotations

import argparse
from pathlib import Path

from pecs_pro.run_pecs_pro import PECSProRuntime
from pecs_pro.runtime.daemon import WorkspaceContinuityDaemon


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the PECS-PRO workspace continuity daemon."
    )
    parser.add_argument(
        "workspace_root",
        nargs="?",
        default=".",
        help="Path to the workspace root to monitor (default: current directory).",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    runtime = PECSProRuntime(workspace_root=workspace_root)
    components = runtime.initialize()

    daemon = WorkspaceContinuityDaemon(
        workspace_root=workspace_root,
        runtime_session=components["runtime_session"],
        compact_builder=components["compact_builder"],
    )

    daemon.start()


if __name__ == "__main__":
    main()
