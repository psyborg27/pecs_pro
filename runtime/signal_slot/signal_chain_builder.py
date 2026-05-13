from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SignalChainBuilder:
    """
    Runtime signal-chain continuity builder.

    Builds deterministic signal execution chains.
    """

    signal_chains: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_chain(
        self,
        chain_id: str,
        node_ids: List[str],
    ) -> None:
        self.signal_chains[chain_id] = node_ids

    def get_chain(
        self,
        chain_id: str,
    ) -> List[str]:
        return self.signal_chains.get(chain_id, [])

    def to_dict(self) -> Dict[str, object]:
        return {
            "signal_chains": self.signal_chains,
        }
