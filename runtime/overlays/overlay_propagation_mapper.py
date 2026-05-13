from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class OverlayPropagationMapper:
    """
    Overlay propagation continuity mapper.

    Tracks execution-topological overlay propagation.
    """

    propagation_paths: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_propagation_path(
        self,
        overlay_id: str,
        target_nodes: List[str],
    ) -> None:
        self.propagation_paths[overlay_id] = target_nodes

    def to_dict(self) -> Dict[str, object]:
        return {
            "propagation_paths": self.propagation_paths,
        }
