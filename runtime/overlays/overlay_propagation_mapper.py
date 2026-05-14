from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..runtime_activation_events import emit_runtime_activation


@dataclass
class OverlayPropagationMapper:
    """
    Overlay propagation continuity mapper.

    Tracks execution-topological overlay propagation.
    """

    propagation_paths: Dict[str, List[str]] = field(default_factory=dict)

    def register_propagation_path(
        self,
        overlay_id: str,
        target_nodes: List[str],
    ) -> None:
        self.propagation_paths[overlay_id] = target_nodes
        emit_runtime_activation(
            event="overlay_propagation",
            source=overlay_id,
            target=target_nodes[0] if target_nodes else "",
            runtime_zone="overlay_pipeline",
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "propagation_paths": self.propagation_paths,
        }
