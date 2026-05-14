from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set

from .runtime_activation_logger import RuntimeActivationLogger
from .runtime_activation_events import EVENT_TYPE_WEIGHTS, build_event


class LocalityActivationEngine:
    """Infer active runtime locality from structured activation signals."""

    def __init__(self, activation_logger: RuntimeActivationLogger) -> None:
        self.activation_logger = activation_logger

    def infer_locality(
        self,
        current_issue: str = "",
        edited_files: Optional[Iterable[str]] = None,
        dissatisfaction_signals: Optional[Iterable[str]] = None,
    ) -> Dict[str, object]:
        edited_files = list(edited_files or [])
        dissatisfaction_signals = list(dissatisfaction_signals or [])

        events = self.activation_logger.export_recent_events(limit=250)
        active_runtime_zones: Set[str] = set()
        activated_objects: Set[str] = set()
        activation_scores: Dict[str, int] = defaultdict(int)
        activation_reasons: Dict[str, List[str]] = defaultdict(list)
        observed_edges: List[Dict[str, object]] = []

        for event in events:
            event_type = str(event.get("event", ""))
            weight = EVENT_TYPE_WEIGHTS.get(event_type, 1)
            source = str(event.get("source", ""))
            target = str(event.get("target", ""))
            runtime_zone = str(event.get("runtime_zone", "")) or "general_runtime"

            if source:
                activated_objects.add(source)
                activation_scores[source] += weight
                activation_reasons[source].append(f"event:{event_type}")

            if target:
                activated_objects.add(target)
                activation_scores[target] += max(weight - 1, 1)
                activation_reasons[target].append(f"event_target:{event_type}")

            if runtime_zone:
                active_runtime_zones.add(runtime_zone)

            if source and target:
                observed_edges.append(
                    {
                        "from": source,
                        "to": target,
                        "type": "observed_runtime_activation",
                        "weight": weight,
                    }
                )

        if current_issue:
            issue_tokens = set(
                re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{3,}", current_issue.lower())
            )
            for token in issue_tokens:
                activated_objects.add(f"PECS_ID:{token}")
                activation_scores[f"PECS_ID:{token}"] += 2
                activation_reasons[f"PECS_ID:{token}"].append("issue_term")

        for path in edited_files:
            normalized = self._normalize_edited_path(path)
            if normalized:
                activated_objects.add(normalized)
                activation_scores[normalized] += 4
                activation_reasons[normalized].append("recent_edit")

        for signal in dissatisfaction_signals:
            normalized = signal.strip().lower()
            if normalized:
                active_runtime_zones.add("general_runtime")
                activation_reasons[f"dissatisfaction:{normalized}"].append(
                    "dissatisfaction"
                )

        if not active_runtime_zones and events:
            active_runtime_zones.add("general_runtime")

        ranked_objects = sorted(
            activated_objects,
            key=lambda obj: (-activation_scores.get(obj, 0), obj),
        )

        return {
            "active_runtime_zones": sorted(active_runtime_zones),
            "activated_objects": ranked_objects[:40],
            "activation_confidence": {
                "total_score": sum(activation_scores.values()),
                "object_scores": {
                    obj: activation_scores[obj] for obj in ranked_objects[:40]
                },
            },
            "activation_reasons": {
                key: list(values) for key, values in activation_reasons.items()
            },
            "observed_edges": observed_edges,
        }

    def _normalize_edited_path(self, path: str) -> Optional[str]:
        path = path.strip()
        if not path:
            return None
        if path.startswith("PECS_ID:"):
            return path
        safe = path.replace("\\", "/").strip("/ ")
        if safe:
            return f"PECS_ID:{safe.replace('/', '.') }"
        return None
