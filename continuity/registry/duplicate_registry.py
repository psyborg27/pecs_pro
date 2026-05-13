from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class DuplicateRegistry:
    """
    Duplicate evolution continuity registry.
    """

    duplicate_clusters: Dict[str, List[str]] = field(
        default_factory=dict
    )

    active_candidates: Dict[str, str] = field(
        default_factory=dict
    )

    def register_duplicate_member(
        self,
        cluster_id: str,
        node_id: str,
    ) -> None:
        self.duplicate_clusters.setdefault(
            cluster_id,
            [],
        ).append(node_id)

    def to_dict(self) -> Dict[str, object]:
        return {
            "duplicate_clusters": self.duplicate_clusters,
            "active_candidates": self.active_candidates,
        }
