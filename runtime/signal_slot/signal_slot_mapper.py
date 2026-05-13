from __future__ import annotations

import ast

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


SIGNAL_CONNECT_PATTERN = "connect"


@dataclass(slots=True)
class SignalSlotMapper:
    """
    Signal-slot continuity reconstruction mapper.

    Signal-slot chains are treated as primary runtime
    continuity topology.
    """

    signal_slot_connections: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def scan_file(self, file_path: Path) -> None:
        try:
            source = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            return

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return

        discovered: List[str] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            func = node.func

            if isinstance(func, ast.Attribute):
                if func.attr == SIGNAL_CONNECT_PATTERN:
                    discovered.append(
                        f"{file_path.name}:{node.lineno}"
                    )

        if discovered:
            self.signal_slot_connections[
                str(file_path)
            ] = discovered

    def to_dict(self) -> Dict[str, object]:
        return {
            "signal_slot_connections": (
                self.signal_slot_connections
            ),
        }
