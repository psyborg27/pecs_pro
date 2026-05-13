from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class OwnershipGraph:
    """
    Runtime ownership continuity graph.
    """

    ownership_edges: Dict[str, List[str]] = field(
        default_factory=dict
    )

    canonical_owners: Dict[str, str] = field(
        default_factory=dict
    )

    def register_ownership(
        self,
        owner_id: str,
        owned_nodes: List[str],
    ) -> None:
        self.ownership_edges[owner_id] = owned_nodes

    def to_dict(self) -> Dict[str, object]:
        return {
            "ownership_edges": self.ownership_edges,
            "canonical_owners": self.canonical_owners,
        }
