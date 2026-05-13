from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class TopologySnapshot:
    """
    Runtime topology snapshot.
    """

    snapshot_id: str

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    execution_paths: List[str] = field(default_factory=list)

    dispatch_chains: List[str] = field(default_factory=list)
    signal_slot_chains: List[str] = field(default_factory=list)
    subprocess_chains: List[str] = field(default_factory=list)

    overlay_propagation_paths: List[str] = field(default_factory=list)
    viewer_propagation_paths: List[str] = field(default_factory=list)

    topology_confidence: float = 0.0

    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at,
            "execution_paths": self.execution_paths,
            "dispatch_chains": self.dispatch_chains,
            "signal_slot_chains": self.signal_slot_chains,
            "subprocess_chains": self.subprocess_chains,
            "overlay_propagation_paths": (
                self.overlay_propagation_paths
            ),
            "viewer_propagation_paths": (
                self.viewer_propagation_paths
            ),
            "topology_confidence": self.topology_confidence,
            "metadata": self.metadata,
        }
