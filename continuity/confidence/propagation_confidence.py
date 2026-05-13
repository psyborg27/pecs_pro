from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PropagationConfidence:
    """
    Overlay and state propagation confidence.
    """

    overlay_verified: bool = False
    viewer_verified: bool = False
    state_flow_verified: bool = False

    confidence_score: float = 0.0

    def calculate(self) -> float:
        score = 0.0

        if self.overlay_verified:
            score += 0.40

        if self.viewer_verified:
            score += 0.35

        if self.state_flow_verified:
            score += 0.25

        self.confidence_score = min(score, 1.0)
        return self.confidence_score
