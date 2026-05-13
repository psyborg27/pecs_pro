from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class OwnershipEdgeType(str, Enum):
    """
    Runtime ownership continuity relationships.
    """

    QACTION_OWNER = "qaction_owner"
    DIALOG_OWNER = "dialog_owner"
    VIEWER_OWNER = "viewer_owner"
    OVERLAY_OWNER = "overlay_owner"
    TOOLBAR_OWNER = "toolbar_owner"
    MENU_OWNER = "menu_owner"
    DISPATCH_OWNER = "dispatch_owner"
    SUBPROCESS_OWNER = "subprocess_owner"
    EXECUTION_OWNER = "execution_owner"


@dataclass
class OwnershipEdge:
    """
    Runtime ownership relationship.

    Ownership is execution-topological authority,
    not merely filesystem locality.
    """

    edge_id: str

    owner_node_id: str
    owned_node_id: str

    ownership_type: OwnershipEdgeType

    confidence: float = 0.0

    runtime_verified: bool = False
    canonical_authority: bool = False

    execution_zone: Optional[str] = None

    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "edge_id": self.edge_id,
            "owner_node_id": self.owner_node_id,
            "owned_node_id": self.owned_node_id,
            "ownership_type": self.ownership_type.value,
            "confidence": self.confidence,
            "runtime_verified": self.runtime_verified,
            "canonical_authority": self.canonical_authority,
            "execution_zone": self.execution_zone,
            "metadata": self.metadata,
        }
