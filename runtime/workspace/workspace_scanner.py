from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List


SUPPORTED_SOURCE_SUFFIXES = {
    ".py",
    ".pyw",
}


@dataclass
class WorkspaceScanner:
    """
    Deterministic workspace topology scanner.

    Performs stable source discovery for runtime-topology
    reconstruction.
    """

    workspace_root: Path

    discovered_files: List[Path] = field(default_factory=list)

    def scan(self) -> List[Path]:
        self.discovered_files.clear()

        for path in self.workspace_root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in SUPPORTED_SOURCE_SUFFIXES:
                continue

            self.discovered_files.append(path)

        self.discovered_files.sort()

        return list(self.discovered_files)

    def iter_files(self) -> Iterable[Path]:
        yield from self.discovered_files
