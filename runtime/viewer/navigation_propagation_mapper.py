from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class NavigationPropagationMapper:
    """
    Viewer navigation propagation mapper.

    Tracks viewer-local execution continuity.
    """

    navigation_paths: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_navigation_path(
        self,
        viewer_id: str,
        node_ids: List[str],
    ) -> None:
        self.navigation_paths[viewer_id] = node_ids

    def to_dict(self) -> Dict[str, object]:
        return {
            "navigation_paths": self.navigation_paths,
        }
