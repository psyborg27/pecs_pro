from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class StatePropagationTracker:
    """
    Runtime state propagation tracker.

    Tracks execution-local state continuity.
    """

    state_flows: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_state_flow(
        self,
        state_id: str,
        target_nodes: List[str],
    ) -> None:
        self.state_flows[state_id] = target_nodes

    def to_dict(self) -> Dict[str, object]:
        return {
            "state_flows": self.state_flows,
        }
