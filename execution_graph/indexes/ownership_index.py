from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class OwnershipIndex:
    """
    Runtime ownership locality index.
    """

    ownership_locality: Dict[str, List[str]] = field(
        default_factory=dict
    )

    canonical_ownership: Dict[str, str] = field(
        default_factory=dict
    )

    def register_ownership_locality(
        self,
        owner_id: str,
        node_ids: List[str],
    ) -> None:
        self.ownership_locality[owner_id] = node_ids

    def get_owned_locality(
        self,
        owner_id: str,
    ) -> List[str]:
        return self.ownership_locality.get(owner_id, [])
