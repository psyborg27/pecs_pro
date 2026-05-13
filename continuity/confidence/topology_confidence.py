from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TopologyConfidence:
    """
    Execution-topology continuity confidence.
    """

    execution_verified: bool = False
    propagation_verified: bool = False
    dispatch_verified: bool = False

    confidence_score: float = 0.0

    def calculate(self) -> float:
        score = 0.0

        if self.execution_verified:
            score += 0.40

        if self.propagation_verified:
            score += 0.30

        if self.dispatch_verified:
            score += 0.30

        self.confidence_score = min(score, 1.0)
        return self.confidence_score
