from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ...execution_graph.indexes.execution_index import (
    ExecutionIndex,
)
from ...execution_graph.indexes.ownership_index import (
    OwnershipIndex,
)
from ..indexing.locality_index import LocalityIndex
from ..scoring.continuity_score_engine import (
    ContinuityScoreEngine,
)


@dataclass(slots=True)
class TopologyRetriever:
    """
    Consolidated topology-aware continuity retrieval engine.

    This intentionally consolidates:
    - locality retrieval
    - continuity reconstruction
    - ownership locality
    - execution locality
    - ranking

    into ONE authority module.

    PECS avoids retrieval fragmentation deliberately.
    """

    locality_index: LocalityIndex
    execution_index: ExecutionIndex
    ownership_index: OwnershipIndex
    scoring_engine: ContinuityScoreEngine

    retrieval_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def retrieve_object_locality(
        self,
        object_id: str,
    ) -> List[str]:
        return self.locality_index.resolve_locality(
            object_id
        )

    def retrieve_execution_locality(
        self,
        path_id: str,
    ) -> List[str]:
        return self.execution_index.get_execution_locality(
            path_id
        )

    def retrieve_ownership_locality(
        self,
        owner_id: str,
    ) -> List[str]:
        return self.ownership_index.get_owned_locality(
            owner_id
        )

    def build_minimal_context(
        self,
        object_id: str,
    ) -> Dict[str, object]:
        locality = self.retrieve_object_locality(
            object_id
        )

        confidence = self.scoring_engine.score_locality(
            locality
        )

        return {
            "object_id": object_id,
            "locality": locality,
            "confidence": confidence,
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "retrieval_metadata": self.retrieval_metadata,
        }
