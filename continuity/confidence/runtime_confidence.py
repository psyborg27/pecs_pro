from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeConfidence:
    """
    Runtime authority confidence evaluation.

    Highest-authority confidence category.
    """

    runtime_verified: bool = False
    active_execution_chain: bool = False
    runtime_trace_verified: bool = False

    confidence_score: float = 0.0

    def calculate(self) -> float:
        score = 0.0

        if self.runtime_verified:
            score += 0.45

        if self.active_execution_chain:
            score += 0.35

        if self.runtime_trace_verified:
            score += 0.20

        self.confidence_score = min(score, 1.0)
        return self.confidence_score
