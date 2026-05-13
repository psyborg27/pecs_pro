from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class TopologyGraphBuilder:
    """
    Runtime topology graph builder.

    Converts runtime-topological continuity into
    structured graph representations.
    """

    graph_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def register_metadata(
        self,
        key: str,
        value: object,
    ) -> None:
        self.graph_metadata[key] = value

    def to_dict(self) -> Dict[str, object]:
        return {
            "graph_metadata": self.graph_metadata,
        }
