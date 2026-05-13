from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class LocalityIndex:
    """
    Execution-local continuity locality index.

    Supports direct locality reconstruction without
    full-project scanning.
    """

    object_locality: Dict[str, List[str]] = field(
        default_factory=dict
    )

    runtime_locality: Dict[str, List[str]] = field(
        default_factory=dict
    )

    ownership_locality: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_object_locality(
        self,
        object_id: str,
        locality_nodes: List[str],
    ) -> None:
        self.object_locality[object_id] = locality_nodes

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
