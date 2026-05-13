from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class ExecutionGraph:
    """
    Execution continuity graph.

    Represents execution-topological continuity paths.
    """

    execution_paths: Dict[str, List[str]] = field(
        default_factory=dict
    )

    execution_chains: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_execution_path(
        self,
        path_id: str,
        node_ids: List[str],
    ) -> None:
        self.execution_paths[path_id] = node_ids

    def register_execution_chain(
        self,
        chain_id: str,
        node_ids: List[str],
    ) -> None:
        self.execution_chains[chain_id] = node_ids

    def to_dict(self) -> Dict[str, object]:
        return {
            "execution_paths": self.execution_paths,
            "execution_chains": self.execution_chains,
        }
