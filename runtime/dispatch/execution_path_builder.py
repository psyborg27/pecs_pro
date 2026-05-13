from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ExecutionPathBuilder:
    """
    Deterministic execution-path builder.

    Builds execution-local continuity paths.
    """

    execution_paths: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_execution_path(
        self,
        path_id: str,
        node_ids: List[str],
    ) -> None:
        self.execution_paths[path_id] = node_ids

    def path_exists(
        self,
        path_id: str,
    ) -> bool:
        return path_id in self.execution_paths

    def to_dict(self) -> Dict[str, object]:
        return {
            "execution_paths": self.execution_paths,
        }
