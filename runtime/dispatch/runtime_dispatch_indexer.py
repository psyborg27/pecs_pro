from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class RuntimeDispatchIndexer:
    """
    Runtime dispatch locality indexer.

    Maintains execution-local dispatch indexes.
    """

    dispatch_index: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def index_dispatch_target(
        self,
        source_id: str,
        target_id: str,
    ) -> None:
        self.dispatch_index.setdefault(
            source_id,
            [],
        ).append(target_id)

    def to_dict(self) -> Dict[str, object]:
        return {
            "dispatch_index": self.dispatch_index,
        }
