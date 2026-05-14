from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..runtime_activation_events import emit_runtime_activation


@dataclass
class ViewerOwnershipMapper:
    """
    Viewer runtime ownership mapper.

    Viewer continuity is treated as execution-topological
    ownership continuity.
    """

    viewer_ownership: Dict[str, List[str]] = field(default_factory=dict)

    def register_viewer_ownership(
        self,
        owner_id: str,
        viewer_id: str,
    ) -> None:
        self.viewer_ownership.setdefault(
            owner_id,
            [],
        ).append(viewer_id)
        emit_runtime_activation(
            event="topology_touch",
            source=owner_id,
            target=viewer_id,
            runtime_zone="viewer_pipeline",
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "viewer_ownership": self.viewer_ownership,
        }
