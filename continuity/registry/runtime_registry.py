from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RuntimeRegistry:
    """
    Runtime-topology registry.
    """

    execution_paths: Dict[str, List[str]] = field(
        default_factory=dict
    )

    runtime_zones: Dict[str, List[str]] = field(
        default_factory=dict
    )

    active_dispatch_paths: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_execution_path(
        self,
        path_id: str,
        node_ids: List[str],
    ) -> None:
        self.execution_paths[path_id] = node_ids

    def to_dict(self) -> Dict[str, object]:
        return {
            "execution_paths": self.execution_paths,
            "runtime_zones": self.runtime_zones,
            "active_dispatch_paths": (
                self.active_dispatch_paths
            ),
        }
