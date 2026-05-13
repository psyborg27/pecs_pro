from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class DispatchChainMapper:
    """
    Runtime dispatch-chain reconstruction mapper.

    Dispatch chains represent execution-topological continuity.
    """

    dispatch_chains: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_dispatch_chain(
        self,
        chain_id: str,
        node_ids: List[str],
    ) -> None:
        self.dispatch_chains[chain_id] = node_ids

    def get_dispatch_chain(
        self,
        chain_id: str,
    ) -> List[str]:
        return self.dispatch_chains.get(chain_id, [])

    def to_dict(self) -> Dict[str, object]:
        return {
            "dispatch_chains": self.dispatch_chains,
        }
