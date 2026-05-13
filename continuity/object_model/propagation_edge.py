from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class PropagationEdgeType(str, Enum):
    """
    Runtime propagation continuity relationships.
    """

    OVERLAY_PROPAGATION = "overlay_propagation"
    VIEWER_PROPAGATION = "viewer_propagation"
    STATE_PROPAGATION = "state_propagation"
    CONTEXT_PROPAGATION = "context_propagation"
    ANNOTATION_PROPAGATION = "annotation_propagation"


@dataclass
class PropagationEdge:
    """
    Runtime propagation topology edge.
    """

    edge_id: str

    propagation_source_id: str
    propagation_target_id: str

    propagation_type: PropagationEdgeType

    confidence: float = 0.0

    runtime_verified: bool = False
    propagation_verified: bool = False

    execution_zone: Optional[str] = None

    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "edge_id": self.edge_id,
            "propagation_source_id": self.propagation_source_id,
            "propagation_target_id": self.propagation_target_id,
            "propagation_type": self.propagation_type.value,
            "confidence": self.confidence,
            "runtime_verified": self.runtime_verified,
            "propagation_verified": self.propagation_verified,
            "execution_zone": self.execution_zone,
            "metadata": self.metadata,
        }
