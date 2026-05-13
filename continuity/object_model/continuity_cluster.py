from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ContinuityCluster:
    """
    Duplicate evolution and continuity drift cluster.

    Represents competing or historically evolving
    continuity implementations.
    """

    cluster_id: str
    canonical_name: str

    active_candidate_id: Optional[str] = None

    member_nodes: List[str] = field(default_factory=list)

    runtime_authority_score: float = 0.0
    continuity_confidence: float = 0.0

    regression_prone: bool = False

    metadata: Dict[str, object] = field(default_factory=dict)

    def register_member(self, node_id: str) -> None:
        if node_id not in self.member_nodes:
            self.member_nodes.append(node_id)

    def to_dict(self) -> Dict[str, object]:
        return {
            "cluster_id": self.cluster_id,
            "canonical_name": self.canonical_name,
            "active_candidate_id": self.active_candidate_id,
            "member_nodes": self.member_nodes,
            "runtime_authority_score": self.runtime_authority_score,
            "continuity_confidence": self.continuity_confidence,
            "regression_prone": self.regression_prone,
            "metadata": self.metadata,
        }
