from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ViewerOwnershipMapper:
    """
    Viewer runtime ownership mapper.

    Viewer continuity is treated as execution-topological
    ownership continuity.
    """

    viewer_ownership: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_viewer_ownership(
        self,
        owner_id: str,
        viewer_id: str,
    ) -> None:
        self.viewer_ownership.setdefault(
            owner_id,
            [],
        ).append(viewer_id)

    def to_dict(self) -> Dict[str, object]:
        return {
            "viewer_ownership": self.viewer_ownership,
        }
