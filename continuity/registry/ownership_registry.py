from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class OwnershipRegistry:
    """
    Runtime ownership continuity registry.
    """

    ownership_map: Dict[str, List[str]] = field(
        default_factory=dict
    )

    canonical_owners: Dict[str, str] = field(
        default_factory=dict
    )

    def register_ownership(
        self,
        owner_id: str,
        owned_node_id: str,
    ) -> None:
        self.ownership_map.setdefault(
            owner_id,
            [],
        ).append(owned_node_id)

    def to_dict(self) -> Dict[str, object]:
        return {
            "ownership_map": self.ownership_map,
            "canonical_owners": self.canonical_owners,
        }
