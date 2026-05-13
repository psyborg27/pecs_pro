from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ContinuityScoreEngine:
    """
    Consolidated deterministic continuity scoring engine.

    Consolidates:
    - locality scoring
    - runtime authority scoring
    - ownership confidence
    - topology confidence

    into ONE scoring authority.

    PECS intentionally avoids scoring-layer proliferation.
    """

    runtime_authority_weight: float = 1.0
    execution_locality_weight: float = 0.9
    ownership_weight: float = 0.8
    propagation_weight: float = 0.7

    def score_locality(
        self,
        locality_nodes: List[str],
    ) -> float:
        if not locality_nodes:
            return 0.0

        base_score = min(
            len(locality_nodes) * 0.1,
            1.0,
        )

        return round(base_score, 3)

    def score_runtime_authority(
        self,
        runtime_verified: bool,
    ) -> float:
        return (
            self.runtime_authority_weight
            if runtime_verified
            else 0.0
        )

    def score_ownership(
        self,
        ownership_verified: bool,
    ) -> float:
        return (
            self.ownership_weight
            if ownership_verified
            else 0.0
        )
