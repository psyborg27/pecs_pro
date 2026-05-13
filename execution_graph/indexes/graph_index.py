from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GraphIndex:
    """
    Canonical execution-topology graph index.

    Provides deterministic locality-oriented graph lookup.
    """

    node_index: Dict[str, Dict[str, object]] = field(
        default_factory=dict
    )

    edge_index: Dict[str, Dict[str, object]] = field(
        default_factory=dict
    )

    zone_index: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_node(
        self,
        node_id: str,
        node_data: Dict[str, object],
    ) -> None:
        self.node_index[node_id] = node_data

    def register_edge(
        self,
        edge_id: str,
        edge_data: Dict[str, object],
    ) -> None:
        self.edge_index[edge_id] = edge_data

    def register_zone(
        self,
        zone_id: str,
        node_ids: List[str],
    ) -> None:
        self.zone_index[zone_id] = node_ids

    def to_dict(self) -> Dict[str, object]:
        return {
            "node_index": self.node_index,
            "edge_index": self.edge_index,
            "zone_index": self.zone_index,
        }
