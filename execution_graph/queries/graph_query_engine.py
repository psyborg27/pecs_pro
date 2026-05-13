from __future__ import annotations

from dataclasses import dataclass

from ..indexes.graph_index import GraphIndex


@dataclass(slots=True)
class GraphQueryEngine:
    """
    Deterministic topology-aware graph query engine.

    Designed for locality-directed retrieval rather than
    full workspace scanning.
    """

    graph_index: GraphIndex

    def query_node(
        self,
        node_id: str,
    ):
        return self.graph_index.node_index.get(node_id)

    def query_zone(
        self,
        zone_id: str,
    ):
        return self.graph_index.zone_index.get(zone_id, [])
