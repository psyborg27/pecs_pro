from __future__ import annotations

from dataclasses import dataclass

from ..graph.runtime_graph import RuntimeGraph
from ..graph.execution_graph import ExecutionGraph
from ..graph.ownership_graph import OwnershipGraph
from ..graph.dispatch_graph import DispatchGraph
from ..graph.propagation_graph import PropagationGraph


@dataclass
class GraphConsolidator:
    """
    Deterministic execution-topology graph consolidator.

    Consolidates runtime reconstruction into stable
    queryable continuity graphs.
    """

    runtime_graph: RuntimeGraph
    execution_graph: ExecutionGraph
    ownership_graph: OwnershipGraph
    dispatch_graph: DispatchGraph
    propagation_graph: PropagationGraph

    def consolidate(self) -> dict:
        return {
            "runtime_graph": self.runtime_graph.to_dict(),
            "execution_graph": (
                self.execution_graph.to_dict()
            ),
            "ownership_graph": (
                self.ownership_graph.to_dict()
            ),
            "dispatch_graph": (
                self.dispatch_graph.to_dict()
            ),
            "propagation_graph": (
                self.propagation_graph.to_dict()
            ),
        }
