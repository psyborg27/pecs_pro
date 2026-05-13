from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..retrieval.topology_retriever import (
    TopologyRetriever,
)


@dataclass(slots=True)
class CompactContextBuilder:
    """
    Consolidated compact continuity reconstruction builder.

    This intentionally consolidates:
    - compact context generation
    - locality compression
    - minimal continuity reconstruction
    - token-budget-aware continuity export
    - execution-local context shaping

    into ONE authority module.

    PECS intentionally avoids:
    - summarization forests
    - compression middleware
    - recursive context pipelines
    - layered export coordinators

    The builder remains:
    deterministic
    locality-oriented
    topology-aware
    low-token
    continuity-safe
    """

    topology_retriever: TopologyRetriever

    default_locality_limit: int = 12

    builder_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def build_compact_object_context(
        self,
        object_id: str,
        locality_limit: Optional[int] = None,
    ) -> Dict[str, object]:
        locality = (
            self.topology_retriever
            .retrieve_object_locality(object_id)
        )

        limit = (
            locality_limit
            if locality_limit is not None
            else self.default_locality_limit
        )

        compact_locality = locality[:limit]

        minimal_context = (
            self.topology_retriever
            .build_minimal_context(object_id)
        )

        return {
            "object_id": object_id,
            "locality": compact_locality,
            "confidence": minimal_context.get(
                "confidence",
                0.0,
            ),
            "locality_count": len(compact_locality),
        }

    def build_multi_object_context(
        self,
        object_ids: List[str],
        locality_limit: Optional[int] = None,
    ) -> Dict[str, object]:
        compact_contexts = []

        for object_id in object_ids:
            compact_contexts.append(
                self.build_compact_object_context(
                    object_id=object_id,
                    locality_limit=locality_limit,
                )
            )

        return {
            "contexts": compact_contexts,
            "context_count": len(compact_contexts),
        }

    def build_execution_local_context(
        self,
        object_id: str,
        path_id: str,
        locality_limit: Optional[int] = None,
    ) -> Dict[str, object]:
        object_context = (
            self.build_compact_object_context(
                object_id=object_id,
                locality_limit=locality_limit,
            )
        )

        execution_locality = (
            self.topology_retriever
            .retrieve_execution_locality(path_id)
        )

        limit = (
            locality_limit
            if locality_limit is not None
            else self.default_locality_limit
        )

        return {
            "object_context": object_context,
            "execution_locality": (
                execution_locality[:limit]
            ),
            "execution_path": path_id,
        }

    def export_low_token_bundle(
        self,
        object_ids: List[str],
    ) -> Dict[str, object]:
        bundle = (
            self.build_multi_object_context(
                object_ids=object_ids,
                locality_limit=self.default_locality_limit,
            )
        )

        return {
            "bundle_type": "low_token_continuity",
            "bundle": bundle,
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "default_locality_limit": (
                self.default_locality_limit
            ),
            "builder_metadata": self.builder_metadata,
        }
