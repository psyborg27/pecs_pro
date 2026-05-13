from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class QActionOwnershipMapper:
    """
    QAction runtime ownership mapper.

    Tracks QAction execution ownership relationships.
    """

    ownership_map: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_ownership(
        self,
        owner_id: str,
        qaction_id: str,
    ) -> None:
        self.ownership_map.setdefault(
            owner_id,
            [],
        ).append(qaction_id)

    def get_owned_qactions(
        self,
        owner_id: str,
    ) -> List[str]:
        return self.ownership_map.get(owner_id, [])

    def to_dict(self) -> Dict[str, object]:
        return {
            "ownership_map": self.ownership_map,
        }
