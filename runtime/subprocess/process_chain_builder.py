from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class ProcessChainBuilder:
    """
    Runtime subprocess execution-chain builder.
    """

    process_chains: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_process_chain(
        self,
        chain_id: str,
        process_nodes: List[str],
    ) -> None:
        self.process_chains[chain_id] = process_nodes

    def to_dict(self) -> Dict[str, object]:
        return {
            "process_chains": self.process_chains,
        }
