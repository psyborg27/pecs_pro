from __future__ import annotations

from typing import Dict

EDGE_TYPE_WEIGHTS: Dict[str, int] = {
    "observed_runtime_activation": 12,
    "signal_slot": 10,
    "dialog_launch": 9,
    "subprocess_launch": 8,
    "overlay_propagation": 8,
    "viewer_sync": 7,
    "runtime_callback": 6,
    "qaction_register": 4,
    "import": 1,
}

DEFAULT_EDGE_WEIGHT = 1


def edge_weight(edge: Dict[str, object]) -> int:
    if not isinstance(edge, dict):
        return DEFAULT_EDGE_WEIGHT
    edge_type = str(edge.get("type", ""))
    return EDGE_TYPE_WEIGHTS.get(edge_type, DEFAULT_EDGE_WEIGHT)


def edge_type_priority(edge_type: str) -> int:
    return EDGE_TYPE_WEIGHTS.get(edge_type, DEFAULT_EDGE_WEIGHT)
