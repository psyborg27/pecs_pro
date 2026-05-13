from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MenuTopologyMapper:
    """
    Menu execution-topology mapper.

    Menus are treated as dispatch-local continuity surfaces.
    """

    menu_actions: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_menu_action(
        self,
        menu_id: str,
        action_id: str,
    ) -> None:
        self.menu_actions.setdefault(
            menu_id,
            [],
        ).append(action_id)

    def to_dict(self) -> Dict[str, object]:
        return {
            "menu_actions": self.menu_actions,
        }
