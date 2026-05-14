from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, Iterable

LITE_RUNTIME_DIR = (
    Path(__file__).resolve().parent / "PECS_LITE v2" / "pecs_lite v2" / "runtime"
)

if str(LITE_RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(LITE_RUNTIME_DIR))

from pecs_lite_runtime_v2 import PECSLiteRuntimeV2  # noqa: E402

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "build",
    "dist",
    ".pecs",
}


class PECSLiteV2WorkspaceDaemon:
    def __init__(
        self,
        workspace_root: Path,
        artifact_dir_name: str = ".pecs",
        output_name: str = "pecs_lite_runtime_topology.json",
        poll_interval: float = 1.0,
    ) -> None:
        self.workspace_root = workspace_root.resolve()
        self.artifact_dir = self.workspace_root / artifact_dir_name
        self.output_path = self.artifact_dir / output_name
        self.state_path = self.artifact_dir / "daemon_lite_v2_state.json"
        self.chat_history_path = self.artifact_dir / "ai_chat_history.json"
        self.poll_interval = poll_interval
        self._last_snapshot: Dict[str, float] = {}
        self._last_chat_history_mtime: float | None = None
        self._running = True

        if not self.workspace_root.exists():
            raise FileNotFoundError(
                f"Workspace root does not exist: {self.workspace_root}"
            )

        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.runtime = PECSLiteRuntimeV2(str(self.workspace_root))

    def start(self) -> None:
        self._install_signal_handlers()
        self._rebuild("initial")
        self._last_snapshot = self._scan_python_mtimes()
        self._last_chat_history_mtime = self._read_chat_history_mtime()
        print(
            f"PECS Lite v2 daemon started for {self.workspace_root}. "
            "Press Ctrl+C to stop."
        )

        while self._running:
            snapshot = self._scan_python_mtimes()
            chat_mtime = self._read_chat_history_mtime()
            if snapshot != self._last_snapshot:
                self._rebuild("filesystem_change")
                self._last_snapshot = snapshot
            elif chat_mtime is not None and chat_mtime != self._last_chat_history_mtime:
                self._rebuild("chat_history_change")
                self._last_chat_history_mtime = chat_mtime
            time.sleep(self.poll_interval)

    def _install_signal_handlers(self) -> None:
        def _handle_stop(_signum: int, _frame: object) -> None:
            self._running = False

        signal.signal(signal.SIGINT, _handle_stop)
        signal.signal(signal.SIGTERM, _handle_stop)

    def _scan_python_mtimes(self) -> Dict[str, float]:
        mtimes: Dict[str, float] = {}
        for path in self._iter_python_files():
            try:
                mtimes[str(path)] = path.stat().st_mtime
            except OSError:
                continue
        return mtimes

    def _read_chat_history_mtime(self) -> float | None:
        if not self.chat_history_path.exists():
            return None
        try:
            return self.chat_history_path.stat().st_mtime
        except OSError:
            return None

    def _read_chat_history_entry_count(self) -> int:
        if not self.chat_history_path.exists():
            return 0
        try:
            data = json.loads(self.chat_history_path.read_text(encoding="utf-8"))
            return len(data) if isinstance(data, list) else 0
        except Exception:
            return 0

    def _iter_python_files(self) -> Iterable[Path]:
        for path in self.workspace_root.rglob("*.py"):
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            yield path

    def _rebuild(self, reason: str) -> None:
        topology = self.runtime.build_runtime_topology()
        self.runtime.export_runtime_topology(str(self.output_path))

        payload = {
            "workspace_root": str(self.workspace_root),
            "output_path": str(self.output_path),
            "reason": reason,
            "timestamp": time.time(),
            "node_count": len(topology) if isinstance(topology, dict) else 0,
            "chat_history_path": str(self.chat_history_path),
            "chat_entry_count": self._read_chat_history_entry_count(),
            "chat_history_mtime": self._read_chat_history_mtime(),
        }
        self.state_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run PECS Lite v2 daemon for a workspace."
    )
    parser.add_argument(
        "workspace_root",
        nargs="?",
        default=".",
        help="Path to workspace root (default: current directory).",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds (default: 1.0).",
    )
    args = parser.parse_args()

    daemon = PECSLiteV2WorkspaceDaemon(
        workspace_root=Path(args.workspace_root),
        poll_interval=max(args.poll_interval, 0.2),
    )
    daemon.start()


if __name__ == "__main__":
    main()
