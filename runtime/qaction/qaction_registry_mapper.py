from __future__ import annotations

import ast

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

QACTION_CLASS_NAMES = {
    "QAction",
}


@dataclass
class QActionRegistryMapper:
    """
    Deterministic QAction extraction mapper.

    Reconstructs QAction continuity participation without
    requiring full semantic analysis.
    """

    discovered_qactions: Dict[str, List[str]] = field(default_factory=dict)

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
                    discovered.append(
                        self._build_anchor(
                            file_path=file_path,
                            segment="qaction",
                            detail=func.id,
                        )
                    )

            elif isinstance(func, ast.Attribute):
                if func.attr in QACTION_CLASS_NAMES:
                    discovered.append(
                        self._build_anchor(
                            file_path=file_path,
                            segment="qaction",
                            detail=func.attr,
                        )
                    )

        if discovered:
            self.discovered_qactions[str(file_path)] = discovered

    def _path_hint(self, file_path: Path) -> str:
        parent = file_path.parent.name
        stem = file_path.stem
        return ".".join(part for part in (parent, stem) if part).lower()

    def _build_anchor(
        self,
        file_path: Path,
        segment: str,
        detail: str,
    ) -> str:
        return f"PECS_ID:{segment}.{self._path_hint(file_path)}.{detail}"

    def to_dict(self) -> Dict[str, object]:
        return {
            "discovered_qactions": self.discovered_qactions,
        }
