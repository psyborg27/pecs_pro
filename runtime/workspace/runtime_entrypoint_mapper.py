from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


ENTRYPOINT_PATTERNS = (
    "if __name__ == '__main__':",
    'if __name__ == "__main__":',
)


@dataclass(slots=True)
class RuntimeEntrypointMapper:
    """
    Runtime entrypoint discovery mapper.

    Discovers probable runtime execution roots.
    """

    entrypoints: Dict[str, List[int]] = field(
        default_factory=dict
    )

    def scan_file(self, file_path: Path) -> None:
        try:
            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            return

        matched_lines: List[int] = []

        for index, line in enumerate(content.splitlines(), start=1):
            if any(pattern in line for pattern in ENTRYPOINT_PATTERNS):
                matched_lines.append(index)

        if matched_lines:
            self.entrypoints[str(file_path)] = matched_lines

    def to_dict(self) -> Dict[str, object]:
        return {
            "entrypoints": self.entrypoints,
        }
