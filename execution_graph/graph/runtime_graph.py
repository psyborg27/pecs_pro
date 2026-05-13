from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RuntimeGraph:
    """
    Canonical runtime-topology graph.

    Stores reconstructed runtime continuity structures.
    """

    runtime_nodes: Dict[str, Dict[str, object]] = field(
        default_factory=dict
    )

    runtime_edges: Dict[str, Dict[str, object]] = field(
        default_factory=dict
    )

    runtime_zones: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_runtime_node(
        self,
        node_id: str,
        node_data: Dict[str, object],
    ) -> None:
        self.runtime_nodes[node_id] = node_data

    def register_runtime_edge(
        self,
        edge_id: str,
        edge_data: Dict[str, object],
    ) -> None:
        self.runtime_edges[edge_id] = edge_data

    def register_runtime_zone(
        self,
        zone_id: str,
        node_ids: List[str],
    ) -> None:
        self.runtime_zones[zone_id] = node_ids

    def to_dict(self) -> Dict[str, object]:
        return {
            "runtime_nodes": self.runtime_nodes,
            "runtime_edges": self.runtime_edges,
            "runtime_zones": self.runtime_zones,
        }
