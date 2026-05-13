from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class ExecutionEdgeType(str, Enum):
    """
    Execution-topology continuity relationships.
    """

    METHOD_CALL = "method_call"
    SIGNAL_DISPATCH = "signal_dispatch"
    CALLBACK_EXECUTION = "callback_execution"
    DIALOG_LAUNCH = "dialog_launch"
    SUBPROCESS_LAUNCH = "subprocess_launch"
    OVERLAY_PROPAGATION = "overlay_propagation"
    VIEWER_PROPAGATION = "viewer_propagation"
    EXECUTION_CHAIN = "execution_chain"


@dataclass
class ExecutionEdge:
    """
    Runtime execution continuity relationship.

    Represents a directed execution-topological edge between
    two RuntimeNode instances.
    """

    edge_id: str

    source_node_id: str
    target_node_id: str

    edge_type: ExecutionEdgeType

    confidence: float = 0.0

    runtime_verified: bool = False
    dispatch_verified: bool = False

    execution_zone: Optional[str] = None

    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "edge_type": self.edge_type.value,
            "confidence": self.confidence,
            "runtime_verified": self.runtime_verified,
            "dispatch_verified": self.dispatch_verified,
            "execution_zone": self.execution_zone,
            "metadata": self.metadata,
        }
