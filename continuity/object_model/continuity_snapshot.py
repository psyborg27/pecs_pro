from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class ContinuitySnapshot:
    """
    Deterministic continuity-state snapshot.
    """

    snapshot_id: str

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    runtime_nodes: List[str] = field(default_factory=list)

    execution_edges: List[str] = field(default_factory=list)
    ownership_edges: List[str] = field(default_factory=list)
    dispatch_edges: List[str] = field(default_factory=list)
    propagation_edges: List[str] = field(default_factory=list)
    subprocess_edges: List[str] = field(default_factory=list)

    continuity_clusters: List[str] = field(default_factory=list)

    canonical_registry_version: str = "v2"

    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at,
            "runtime_nodes": self.runtime_nodes,
            "execution_edges": self.execution_edges,
            "ownership_edges": self.ownership_edges,
            "dispatch_edges": self.dispatch_edges,
            "propagation_edges": self.propagation_edges,
            "subprocess_edges": self.subprocess_edges,
            "continuity_clusters": self.continuity_clusters,
            "canonical_registry_version": (
                self.canonical_registry_version
            ),
            "metadata": self.metadata,
        }
