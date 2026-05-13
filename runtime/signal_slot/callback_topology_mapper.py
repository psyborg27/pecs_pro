from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CallbackTopologyMapper:
    """
    Runtime callback topology mapper.

    Reconstructs callback execution locality and
    dispatch continuity.
    """

    callback_map: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_callback(
        self,
        source_id: str,
        callback_id: str,
    ) -> None:
        self.callback_map.setdefault(
            source_id,
            [],
        ).append(callback_id)

    def to_dict(self) -> Dict[str, object]:
        return {
            "callback_map": self.callback_map,
        }
