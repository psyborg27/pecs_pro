from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class SubprocessEdgeType(str, Enum):
    """
    Runtime subprocess continuity relationships.
    """

    OCR_LAUNCH = "ocr_launch"
    EXTERNAL_RUNTIME = "external_runtime"
    PIPELINE_STAGE = "pipeline_stage"
    PROCESS_CHAIN = "process_chain"
    SUBPROCESS_DELEGATION = "subprocess_delegation"


@dataclass
class SubprocessEdge:
    """
    Runtime subprocess topology edge.
    """

    edge_id: str

    parent_node_id: str
    subprocess_node_id: str

    subprocess_type: SubprocessEdgeType

    confidence: float = 0.0

    runtime_verified: bool = False
    subprocess_verified: bool = False

    execution_zone: Optional[str] = None

    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "edge_id": self.edge_id,
            "parent_node_id": self.parent_node_id,
            "subprocess_node_id": self.subprocess_node_id,
            "subprocess_type": self.subprocess_type.value,
            "confidence": self.confidence,
            "runtime_verified": self.runtime_verified,
            "subprocess_verified": self.subprocess_verified,
            "execution_zone": self.execution_zone,
            "metadata": self.metadata,
        }
