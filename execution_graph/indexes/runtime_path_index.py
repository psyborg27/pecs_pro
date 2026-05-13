from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RuntimePathIndex:
    """
    Runtime execution-path locality index.
    """

    runtime_paths: Dict[str, List[str]] = field(
        default_factory=dict
    )

    active_runtime_zones: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_runtime_path(
        self,
        path_id: str,
        node_ids: List[str],
    ) -> None:
        self.runtime_paths[path_id] = node_ids

    def get_runtime_path(
        self,
        path_id: str,
    ) -> List[str]:
        return self.runtime_paths.get(path_id, [])
