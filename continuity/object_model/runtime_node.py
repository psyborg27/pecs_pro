from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class RuntimeNodeType(str, Enum):
    """
    Canonical runtime-topology node categories.
    """

    QACTION = "qaction"
    SIGNAL = "signal"
    SLOT = "slot"
    DIALOG = "dialog"
    SUBPROCESS = "subprocess"
    OVERLAY = "overlay"
    VIEWER = "viewer"
    CALLBACK = "callback"
    DISPATCH = "dispatch"
    EXECUTION = "execution"
    TOOLBAR = "toolbar"
    MENU = "menu"
    MODULE = "module"
    CLASS = "class"
    METHOD = "method"
    WORKSPACE = "workspace"


class RuntimeAuthorityLevel(str, Enum):
    """
    Runtime authority hierarchy.

    Higher authority levels should dominate canonical arbitration.
    """

    LIVE_RUNTIME = "live_runtime"
    EXECUTION_GRAPH = "execution_graph"
    WORKSPACE_STATE = "workspace_state"
    REGISTRY_STATE = "registry_state"
    HISTORICAL = "historical"


@dataclass(slots=True)
class RuntimeNode:
    """
    Canonical runtime-topology continuity primitive.

    A RuntimeNode represents an execution-topological entity
    participating in runtime continuity.

    PECS-PRO v2 intentionally models runtime topology rather
    than static filesystem hierarchy.
    """

    node_id: str
    node_type: RuntimeNodeType
    canonical_name: str

    module_path: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None

    runtime_owner: Optional[str] = None
    execution_zone: Optional[str] = None

    authority_level: RuntimeAuthorityLevel = (
        RuntimeAuthorityLevel.WORKSPACE_STATE
    )

    confidence: float = 0.0

    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, object] = field(default_factory=dict)

    incoming_edges: List[str] = field(default_factory=list)
    outgoing_edges: List[str] = field(default_factory=list)

    duplicate_cluster_id: Optional[str] = None
    canonical_candidate: bool = False

    def register_outgoing_edge(self, edge_id: str) -> None:
        if edge_id not in self.outgoing_edges:
            self.outgoing_edges.append(edge_id)

    def register_incoming_edge(self, edge_id: str) -> None:
        if edge_id not in self.incoming_edges:
            self.incoming_edges.append(edge_id)

    @property
    def fully_qualified_identity(self) -> str:
        components = [
            self.module_path or "",
            self.class_name or "",
            self.method_name or "",
            self.canonical_name,
        ]

        filtered = [component for component in components if component]
        return "::".join(filtered)

    def to_dict(self) -> Dict[str, object]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "canonical_name": self.canonical_name,
            "module_path": self.module_path,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "runtime_owner": self.runtime_owner,
            "execution_zone": self.execution_zone,
            "authority_level": self.authority_level.value,
            "confidence": self.confidence,
            "tags": sorted(self.tags),
            "metadata": self.metadata,
            "incoming_edges": self.incoming_edges,
            "outgoing_edges": self.outgoing_edges,
            "duplicate_cluster_id": self.duplicate_cluster_id,
            "canonical_candidate": self.canonical_candidate,
        }
