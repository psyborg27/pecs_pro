from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..runtime_activation_events import emit_runtime_activation


@dataclass
class NavigationPropagationMapper:
    """
    Viewer navigation propagation mapper.

    Tracks viewer-local execution continuity.
    """

    navigation_paths: Dict[str, List[str]] = field(default_factory=dict)

    def register_navigation_path(
        self,
        viewer_id: str,
        node_ids: List[str],
    ) -> None:
        self.navigation_paths[viewer_id] = node_ids
        emit_runtime_activation(
            event="viewer_sync",
            source=viewer_id,
            target=node_ids[0] if node_ids else "",
            runtime_zone="viewer_pipeline",
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "navigation_paths": self.navigation_paths,
        }
