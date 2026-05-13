from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class TopologyIndex:
    """
    Topology-first continuity index.

    Central locality-oriented continuity lookup structure.
    """

    continuity_zones: Dict[str, List[str]] = field(
        default_factory=dict
    )

    dispatch_locality: Dict[str, List[str]] = field(
        default_factory=dict
    )

    propagation_locality: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_continuity_zone(
        self,
        zone_id: str,
        node_ids: List[str],
    ) -> None:
        self.continuity_zones[zone_id] = node_ids

    def to_dict(self) -> Dict[str, object]:
        return {
            "continuity_zones": self.continuity_zones,
            "dispatch_locality": self.dispatch_locality,
            "propagation_locality": (
                self.propagation_locality
            ),
        }
