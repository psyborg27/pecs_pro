from __future__ import annotations

from collections import deque, defaultdict
from typing import Dict, Iterable, List, Set, Tuple

from .topology_edge_weights import edge_weight


class LocalityTraversal:
    """Bounded locality traversal over weighted runtime topology."""

    def traverse(
        self,
        seed_ids: Iterable[str],
        edges: Iterable[Dict[str, object]],
        max_nodes: int = 40,
        max_budget: int = 120,
    ) -> Set[str]:
        adjacency: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        reverse: Dict[str, List[Tuple[str, int]]] = defaultdict(list)

        for edge in edges:
            source = str(edge.get("from", ""))
            target = str(edge.get("to", ""))
            if not source or not target:
                continue
            weight = edge_weight(edge)
            adjacency[source].append((target, weight))
            reverse[target].append((source, weight))

        seeds = [str(seed) for seed in seed_ids if str(seed)]
        visited: Set[str] = set(seeds)
        queue = deque((seed, 0) for seed in seeds)
        budget = 0

        while queue and len(visited) < max_nodes and budget < max_budget:
            current, distance = queue.popleft()
            neighbors = adjacency.get(current, []) + reverse.get(current, [])
            neighbors.sort(key=lambda item: item[1])

            for neighbor_id, weight in neighbors:
                if neighbor_id in visited:
                    continue
                if budget + weight > max_budget:
                    continue
                visited.add(neighbor_id)
                budget += weight
                queue.append((neighbor_id, distance + weight))
                if len(visited) >= max_nodes or budget >= max_budget:
                    break

        return visited
