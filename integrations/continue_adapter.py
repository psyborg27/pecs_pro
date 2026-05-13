from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..topology.retrieval.topology_retriever import (
    TopologyRetriever,
)


@dataclass
class ContinueAdapter:
    """
    Consolidated Continue integration adapter.

    Intentionally consolidates:
    - context preparation
    - continuity export
    - locality reconstruction
    - compact context generation

    into ONE integration authority.

    PECS avoids integration fragmentation deliberately.
    """

    topology_retriever: TopologyRetriever

    adapter_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def build_continue_context(
        self,
        object_id: str,
    ) -> Dict[str, object]:
        continuity_context = (
            self.topology_retriever
            .build_minimal_context(object_id)
        )

        return {
            "adapter": "continue",
            "continuity_context": continuity_context,
        }

    def build_compact_context_window(
        self,
        object_ids: List[str],
    ) -> Dict[str, object]:
        reconstructed = []

        for object_id in object_ids:
            reconstructed.append(
                self.build_continue_context(object_id)
            )

        return {
            "contexts": reconstructed,
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "adapter_metadata": self.adapter_metadata,
        }
