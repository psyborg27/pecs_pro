from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CanonicalConfidence:
    """
    Canonical continuity arbitration confidence.
    """

    runtime_authority_verified: bool = False
    topology_verified: bool = False
    duplicate_cluster_stable: bool = False

    confidence_score: float = 0.0

    def calculate(self) -> float:
        score = 0.0

        if self.runtime_authority_verified:
            score += 0.50

        if self.topology_verified:
            score += 0.30

        if self.duplicate_cluster_stable:
            score += 0.20

        self.confidence_score = min(score, 1.0)
        return self.confidence_score
