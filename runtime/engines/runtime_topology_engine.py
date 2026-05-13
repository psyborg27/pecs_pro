from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from ...continuity.registry.continuity_registry import (
    ContinuityRegistry,
)
from ...continuity.registry.runtime_registry import RuntimeRegistry


@dataclass(slots=True)
class RuntimeTopologyEngine:
    """
    Primary runtime topology reconstruction engine.

    PECS-PRO v2 reconstructs execution-topological continuity
    rather than filesystem hierarchy continuity.
    """

    workspace_root: Path

    continuity_registry: ContinuityRegistry
    runtime_registry: RuntimeRegistry

    reconstructed_paths: List[str] = field(default_factory=list)

    topology_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def initialize_runtime_scan(self) -> None:
        """
        Initialize deterministic runtime reconstruction state.
        """

        self.topology_metadata["workspace_root"] = str(
            self.workspace_root
        )

        self.topology_metadata["runtime_initialized"] = True

    def register_execution_path(
        self,
        path_id: str,
        node_ids: List[str],
    ) -> None:
        self.runtime_registry.register_execution_path(
            path_id=path_id,
            node_ids=node_ids,
        )

        self.reconstructed_paths.append(path_id)

    def get_registered_paths(self) -> List[str]:
        return list(self.reconstructed_paths)
