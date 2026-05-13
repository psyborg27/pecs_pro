from __future__ import annotations

import ast

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class ImportLocalityMapper:
    """
    Static import locality mapper.

    Imports are treated as supporting runtime evidence,
    NOT canonical continuity truth.
    """

    import_graph: Dict[str, Set[str]] = field(
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

        imports: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for imported in node.names:
                    imports.add(imported.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

        self.import_graph[str(file_path)] = imports

    def get_imports(self, file_path: str) -> List[str]:
        return sorted(self.import_graph.get(file_path, set()))

    def to_dict(self) -> Dict[str, object]:
        return {
            "import_graph": {
                path: sorted(imports)
                for path, imports in self.import_graph.items()
            }
        }
