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


@dataclass
class ContinuityAnchor:
    """
    Compact canonical continuity anchor.

    Anchors are topology-aware, locality-aware, ownership-aware,
    deterministic, grep-searchable, and stable across line shifts.
    """

    topology_layer: str
    locality_hint: Optional[str] = None
    semantic_key: Optional[str] = None
    ownership_hint: Optional[str] = None

    def __post_init__(self) -> None:
        self.topology_layer = self._normalize(self.topology_layer)
        self.locality_hint = self._normalize(self.locality_hint)
        self.semantic_key = self._normalize(self.semantic_key)
        self.ownership_hint = self._normalize(self.ownership_hint)

    @staticmethod
    def _normalize(value: Optional[str]) -> Optional[str]:
        if not value:
            return None

        normalized = value.strip().replace("\\", ".").replace("/", ".")
        segments = [segment for segment in normalized.split(".") if segment]
        return ".".join(segments).lower()

    def __str__(self) -> str:
        segments = [self.topology_layer]

        if self.locality_hint:
            segments.append(self.locality_hint)

        if self.semantic_key:
            segments.append(self.semantic_key)

        if self.ownership_hint:
            segments.append(self.ownership_hint)

        return "PECS_ID:" + ".".join(segments)

    def to_dict(self) -> Dict[str, object]:
        return {
            "anchor": str(self),
            "topology_layer": self.topology_layer,
            "locality_hint": self.locality_hint,
            "semantic_key": self.semantic_key,
            "ownership_hint": self.ownership_hint,
        }


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


@dataclass
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

    authority_level: RuntimeAuthorityLevel = RuntimeAuthorityLevel.WORKSPACE_STATE

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

    @property
    def canonical_anchor(self) -> str:
        anchor = ContinuityAnchor(
            topology_layer=self.node_type.value,
            locality_hint=self.module_path or self.runtime_owner or self.execution_zone,
            semantic_key=self.method_name or self.canonical_name or self.class_name,
            ownership_hint=self.runtime_owner,
        )

        return str(anchor)

    def to_dict(self) -> Dict[str, object]:
        return {
            "node_id": self.node_id,
            "canonical_anchor": self.canonical_anchor,
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
