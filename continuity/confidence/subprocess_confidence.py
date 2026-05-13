from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SubprocessConfidence:
    """
    Runtime subprocess continuity confidence.
    """

    subprocess_verified: bool = False
    execution_chain_verified: bool = False
    runtime_launch_verified: bool = False

    confidence_score: float = 0.0

    def calculate(self) -> float:
        score = 0.0

        if self.subprocess_verified:
            score += 0.40

        if self.execution_chain_verified:
            score += 0.35

        if self.runtime_launch_verified:
            score += 0.25

        self.confidence_score = min(score, 1.0)
        return self.confidence_score
