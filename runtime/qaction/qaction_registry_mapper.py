from __future__ import annotations

import ast

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


QACTION_CLASS_NAMES = {
    "QAction",
}


@dataclass(slots=True)
class QActionRegistryMapper:
    """
    Deterministic QAction extraction mapper.

    Reconstructs QAction continuity participation without
    requiring full semantic analysis.
    """

    discovered_qactions: Dict[str, List[str]] = field(
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
                if func.id in QACTION_CLASS_NAMES:
                    discovered.append(func.id)

            elif isinstance(func, ast.Attribute):
                if func.attr in QACTION_CLASS_NAMES:
                    discovered.append(func.attr)

        if discovered:
            self.discovered_qactions[str(file_path)] = discovered

    def to_dict(self) -> Dict[str, object]:
        return {
            "discovered_qactions": self.discovered_qactions,
        }
