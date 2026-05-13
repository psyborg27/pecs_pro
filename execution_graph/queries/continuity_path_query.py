from __future__ import annotations

from dataclasses import dataclass

from ..indexes.execution_index import ExecutionIndex


@dataclass
class ContinuityPathQuery:
    """
    Execution-local continuity query interface.

    Used to reconstruct minimal continuity context for
    targeted engineering operations.
    """

    execution_index: ExecutionIndex

    def resolve_execution_locality(
        self,
        path_id: str,
    ):
        return self.execution_index.get_execution_locality(
            path_id
        )
