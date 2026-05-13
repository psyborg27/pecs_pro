from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DispatchGraph:
    """
    Dispatch continuity graph.

    Represents runtime dispatch-topological continuity.
    """

    dispatch_chains: Dict[str, List[str]] = field(
        default_factory=dict
    )

    dispatch_targets: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_dispatch_chain(
        self,
        chain_id: str,
        node_ids: List[str],
    ) -> None:
        self.dispatch_chains[chain_id] = node_ids

    def to_dict(self) -> Dict[str, object]:
        return {
            "dispatch_chains": self.dispatch_chains,
            "dispatch_targets": self.dispatch_targets,
        }
