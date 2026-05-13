from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from ..object_model.runtime_node import RuntimeNode


@dataclass(slots=True)
class ContinuityRegistry:
    """
    Master deterministic continuity registry.
    """

    runtime_nodes: Dict[str, RuntimeNode] = field(
        default_factory=dict
    )

    def register_runtime_node(self, node: RuntimeNode) -> None:
        self.runtime_nodes[node.node_id] = node

    def has_runtime_node(self, node_id: str) -> bool:
        return node_id in self.runtime_nodes

    def get_runtime_node(self, node_id: str):
        return self.runtime_nodes.get(node_id)

    def to_dict(self) -> Dict[str, object]:
        return {
            "runtime_nodes": {
                node_id: node.to_dict()
                for node_id, node in self.runtime_nodes.items()
            }
        }
