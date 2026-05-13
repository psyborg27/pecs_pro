from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class ToolbarTopologyMapper:
    """
    Toolbar execution-topology mapper.
    """

    toolbar_actions: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_toolbar_action(
        self,
        toolbar_id: str,
        action_id: str,
    ) -> None:
        self.toolbar_actions.setdefault(
            toolbar_id,
            [],
        ).append(action_id)

    def to_dict(self) -> Dict[str, object]:
        return {
            "toolbar_actions": self.toolbar_actions,
        }
