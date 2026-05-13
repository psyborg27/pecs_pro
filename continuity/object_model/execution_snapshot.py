from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass(slots=True)
class ExecutionSnapshot:
    """
    Execution-chain continuity snapshot.
    """

    snapshot_id: str

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    execution_chain_ids: List[str] = field(default_factory=list)

    runtime_dispatch_paths: List[str] = field(default_factory=list)
    callback_execution_paths: List[str] = field(default_factory=list)

    active_runtime_zones: List[str] = field(default_factory=list)

    execution_confidence: float = 0.0

    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at,
            "execution_chain_ids": self.execution_chain_ids,
            "runtime_dispatch_paths": self.runtime_dispatch_paths,
            "callback_execution_paths": (
                self.callback_execution_paths
            ),
            "active_runtime_zones": self.active_runtime_zones,
            "execution_confidence": self.execution_confidence,
            "metadata": self.metadata,
        }
