from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DispatchConfidence:
    """
    Runtime dispatch continuity confidence.
    """

    dispatch_chain_verified: bool = False
    qaction_verified: bool = False
    callback_verified: bool = False

    confidence_score: float = 0.0

    def calculate(self) -> float:
        score = 0.0

        if self.dispatch_chain_verified:
            score += 0.45

        if self.qaction_verified:
            score += 0.35

        if self.callback_verified:
            score += 0.20

        self.confidence_score = min(score, 1.0)
        return self.confidence_score
