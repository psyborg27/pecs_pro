from __future__ import annotations

import ast

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


SUBPROCESS_PATTERNS = {
    "subprocess",
    "Popen",
    "run",
}


@dataclass(slots=True)
class SubprocessTopologyMapper:
    """
    Runtime subprocess topology mapper.

    Reconstructs subprocess execution continuity.
    """

    subprocess_calls: Dict[str, List[str]] = field(
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

            if isinstance(func, ast.Name):
                if func.id in SUBPROCESS_PATTERNS:
                    discovered.append(
                        f"{func.id}:{node.lineno}"
                    )

            elif isinstance(func, ast.Attribute):
                if func.attr in SUBPROCESS_PATTERNS:
                    discovered.append(
                        f"{func.attr}:{node.lineno}"
                    )

        if discovered:
            self.subprocess_calls[str(file_path)] = discovered

    def to_dict(self) -> Dict[str, object]:
        return {
            "subprocess_calls": self.subprocess_calls,
        }
