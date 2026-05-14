from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .runtime_activation_events import (
    RuntimeActivationEvent,
    build_event,
    validate_event,
)


class RuntimeActivationLogger:
    """Small bounded runtime activation event queue."""

    def __init__(self, artifact_dir: Path, max_events: int = 300) -> None:
        self.artifact_dir = artifact_dir
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.event_path = artifact_dir / "runtime_activation.jsonl"
        self.max_events = max_events

    def append_event(self, event: Dict[str, object]) -> None:
        if not validate_event(event):
            raise ValueError("Invalid runtime activation event")

        normalized_event = build_event(
            event=event["event"],
            source=str(event["source"]),
            target=str(event.get("target", "")),
            runtime_zone=str(event.get("runtime_zone", "")),
            metadata=(
                event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
            ),
            ts=float(event.get("ts", None)) if event.get("ts") is not None else None,
        )

        lines = self._read_lines()
        lines.append(json.dumps(normalized_event, ensure_ascii=False))
        if len(lines) > self.max_events:
            lines = lines[-self.max_events :]

        self.event_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def read_events(self) -> List[Dict[str, object]]:
        events: List[Dict[str, object]] = []
        if not self.event_path.exists():
            return events

        for line in self.event_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if isinstance(record, dict):
                    events.append(record)
            except json.JSONDecodeError:
                continue

        return events

    def _read_lines(self) -> List[str]:
        if not self.event_path.exists():
            return []
        return [
            line
            for line in self.event_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def export_recent_events(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, object]]:
        events = self.read_events()
        if limit is None:
            return events
        return events[-limit:]

    def to_dict(self) -> Dict[str, object]:
        return {
            "event_path": str(self.event_path),
            "max_events": self.max_events,
            "recent_event_count": len(self.read_events()),
        }
