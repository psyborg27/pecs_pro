from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LocalityIndex:
    """
    Execution-local continuity locality index.

    Stores compact symbolic continuity anchors instead of raw
    filesystem line references. Anchors are PECS_ID tokens that
    preserve topology locality, ownership locality, and execution
    locality without inflating the payload.
    """

    object_locality: Dict[str, List[str]] = field(default_factory=dict)

    runtime_locality: Dict[str, List[str]] = field(default_factory=dict)

    ownership_locality: Dict[str, List[str]] = field(default_factory=dict)

    def register_object_locality(
        self,
        object_id: str,
        locality_anchors: List[str],
    ) -> None:
        self.object_locality[object_id] = locality_anchors

    def resolve_locality(
        self,
        object_id: str,
    ) -> List[str]:
        return self.object_locality.get(object_id, [])

    def to_dict(self) -> Dict[str, object]:
        return {
            "object_locality": self.object_locality,
            "runtime_locality": self.runtime_locality,
            "ownership_locality": self.ownership_locality,
        }
