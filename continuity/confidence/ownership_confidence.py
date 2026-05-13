from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OwnershipConfidence:
    """
    Runtime ownership continuity confidence.
    """

    runtime_owner_verified: bool = False
    canonical_owner_verified: bool = False
    execution_locality_verified: bool = False

    confidence_score: float = 0.0

    def calculate(self) -> float:
        score = 0.0

        if self.runtime_owner_verified:
            score += 0.50

        if self.canonical_owner_verified:
            score += 0.30

        if self.execution_locality_verified:
            score += 0.20

        self.confidence_score = min(score, 1.0)
        return self.confidence_score
