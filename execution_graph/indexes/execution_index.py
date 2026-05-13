from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class ExecutionIndex:
    """
    Execution locality index.

    Optimized for execution-path continuity retrieval.
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

    def get_execution_locality(
        self,
        path_id: str,
    ) -> List[str]:
        return self.execution_paths.get(path_id, [])
