from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class PropagationGraph:
    """
    Overlay and state propagation continuity graph.
    """

    propagation_paths: Dict[str, List[str]] = field(
        default_factory=dict
    )

    state_flows: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_propagation_path(
        self,
        propagation_id: str,
        node_ids: List[str],
    ) -> None:
        self.propagation_paths[propagation_id] = node_ids

    def to_dict(self) -> Dict[str, object]:
        return {
            "propagation_paths": self.propagation_paths,
            "state_flows": self.state_flows,
        }
