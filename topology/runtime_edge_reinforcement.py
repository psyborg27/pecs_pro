from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

from .topology_edge_weights import edge_weight


class RuntimeEdgeReinforcement:
    """Reinforce topology adjacency using observed runtime activation."""

    def __init__(self) -> None:
        self.observed_counts: Dict[Tuple[str, str], int] = defaultdict(int)

    def reinforce_edges(self, observed_edges: Iterable[Dict[str, object]]) -> None:
        for edge in observed_edges:
            source = str(edge.get("from", ""))
            target = str(edge.get("to", ""))
            if source and target:
                self.observed_counts[(source, target)] += int(edge.get("weight", 1))

    def reset(self) -> None:
        self.observed_counts.clear()

    def weighted_edges(self, edges: List[Dict[str, object]]) -> List[Dict[str, object]]:
        result: List[Dict[str, object]] = []
        for edge in edges:
            source = str(edge.get("from", ""))
            target = str(edge.get("to", ""))
            base_weight = edge_weight(edge)
            bonus = self.observed_counts.get((source, target), 0)
            result.append(
                {
                    **edge,
                    "weight": base_weight + bonus,
                    "observed_bonus": bonus,
                }
            )
        return result

    def edge_confidence(self, source: str, target: str) -> float:
        return min(1.0, self.observed_counts.get((source, target), 0) / 10.0)

    def to_dict(self) -> Dict[str, object]:
        return {
            "observed_counts": {
                f"{source}->{target}": count
                for (source, target), count in self.observed_counts.items()
            }
        }
