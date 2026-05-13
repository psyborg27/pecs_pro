from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class DispatchEdgeType(str, Enum):
    """
    Runtime dispatch continuity relationships.
    """

    QACTION_DISPATCH = "qaction_dispatch"
    TOOLBAR_DISPATCH = "toolbar_dispatch"
    MENU_DISPATCH = "menu_dispatch"
    SIGNAL_DISPATCH = "signal_dispatch"
    CALLBACK_DISPATCH = "callback_dispatch"
    EXECUTION_DISPATCH = "execution_dispatch"


@dataclass(slots=True)
class DispatchEdge:
    """
    Runtime dispatch topology edge.
    """

    edge_id: str

    dispatch_source_id: str
    dispatch_target_id: str

    dispatch_type: DispatchEdgeType

    confidence: float = 0.0

    runtime_verified: bool = False
    active_dispatch_path: bool = False

    execution_zone: Optional[str] = None

    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "edge_id": self.edge_id,
            "dispatch_source_id": self.dispatch_source_id,
            "dispatch_target_id": self.dispatch_target_id,
            "dispatch_type": self.dispatch_type.value,
            "confidence": self.confidence,
            "runtime_verified": self.runtime_verified,
            "active_dispatch_path": self.active_dispatch_path,
            "execution_zone": self.execution_zone,
            "metadata": self.metadata,
        }
