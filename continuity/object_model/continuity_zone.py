from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass(slots=True)
class ContinuityZone:
    """
    Execution-topological continuity region.

    Zones represent runtime-local continuity ecosystems,
    not filesystem directories.
    """

    zone_id: str
    canonical_name: str

    runtime_nodes: Set[str] = field(default_factory=set)

    execution_edges: Set[str] = field(default_factory=set)
    ownership_edges: Set[str] = field(default_factory=set)
    dispatch_edges: Set[str] = field(default_factory=set)
    propagation_edges: Set[str] = field(default_factory=set)

    confidence: float = 0.0

    duplicate_clusters: List[str] = field(default_factory=list)

    metadata: Dict[str, object] = field(default_factory=dict)

    def register_runtime_node(self, node_id: str) -> None:
        self.runtime_nodes.add(node_id)

    def to_dict(self) -> Dict[str, object]:
        return {
            "zone_id": self.zone_id,
            "canonical_name": self.canonical_name,
            "runtime_nodes": sorted(self.runtime_nodes),
            "execution_edges": sorted(self.execution_edges),
            "ownership_edges": sorted(self.ownership_edges),
            "dispatch_edges": sorted(self.dispatch_edges),
            "propagation_edges": sorted(self.propagation_edges),
            "confidence": self.confidence,
            "duplicate_clusters": self.duplicate_clusters,
            "metadata": self.metadata,
        }
