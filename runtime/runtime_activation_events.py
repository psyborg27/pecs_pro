from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

EVENT_RECORD_KEYS = (
    "event",
    "metadata",
    "runtime_zone",
    "source",
    "target",
    "ts",
)

ACTIVATION_EVENT_TYPES = [
    "qaction_trigger",
    "dialog_launch",
    "dialog_close",
    "signal_slot_activation",
    "subprocess_launch",
    "subprocess_exit",
    "worker_start",
    "worker_finish",
    "overlay_propagation",
    "viewer_sync",
    "exception",
    "ocr_execution",
    "topology_touch",
]

EVENT_TYPE_WEIGHTS: Dict[str, int] = {
    "qaction_trigger": 8,
    "dialog_launch": 7,
    "dialog_close": 4,
    "signal_slot_activation": 9,
    "subprocess_launch": 6,
    "subprocess_exit": 3,
    "worker_start": 5,
    "worker_finish": 3,
    "overlay_propagation": 7,
    "viewer_sync": 6,
    "exception": 10,
    "ocr_execution": 7,
    "topology_touch": 4,
}

DEFAULT_RUNTIME_ZONE = "general_runtime"


@dataclass
class RuntimeActivationEvent:
    ts: int
    event: str
    source: str
    target: str = ""
    runtime_zone: str = ""
    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "ts": self.ts,
            "event": self.event,
            "source": self.source,
            "target": self.target,
            "runtime_zone": self.runtime_zone,
            "metadata": self.metadata,
        }


def _normalize_string(value: Optional[str]) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_metadata(
    metadata: Optional[Dict[str, object]],
    max_keys: int = 6,
) -> Dict[str, object]:
    if not isinstance(metadata, dict):
        return {}

    normalized: Dict[str, object] = {}
    for key in sorted(metadata)[:max_keys]:
        value = metadata[key]
        if isinstance(value, (str, int, float, bool)) or value is None:
            normalized[str(key)] = value
        else:
            normalized[str(key)] = str(value)
    return normalized


def validate_event(event: Dict[str, object]) -> bool:
    if not isinstance(event, dict):
        return False

    if event.get("event") not in ACTIVATION_EVENT_TYPES:
        return False

    if not _normalize_string(event.get("source")):
        return False

    ts = event.get("ts")
    if ts is not None and not isinstance(ts, int):
        return False

    if "runtime_zone" in event and not isinstance(event.get("runtime_zone"), str):
        return False

    if "metadata" in event and not isinstance(event.get("metadata"), dict):
        return False

    return True


def build_event(
    event: str,
    source: str,
    target: str = "",
    runtime_zone: str = "",
    metadata: Optional[Dict[str, object]] = None,
    ts: Optional[float] = None,
) -> Dict[str, object]:
    event = event.strip()
    if event not in ACTIVATION_EVENT_TYPES:
        raise ValueError(f"Unsupported runtime activation event type: {event}")

    metadata = _normalize_metadata(metadata)
    runtime_zone = _normalize_string(runtime_zone) or DEFAULT_RUNTIME_ZONE

    activation_event = RuntimeActivationEvent(
        ts=int(ts if ts is not None else time.time()),
        event=event,
        source=_normalize_string(source),
        target=_normalize_string(target),
        runtime_zone=runtime_zone,
        metadata=metadata,
    )

    return activation_event.to_dict()


def _event_file_path(workspace_root: Optional[Path] = None) -> Path:
    base = Path(workspace_root or Path.cwd())
    artifact_dir = base / ".pecs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir / "runtime_activation.jsonl"


def _read_event_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return [
        line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _write_event_lines(path: Path, lines: List[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def emit_runtime_activation(
    event: str,
    source: str,
    target: Optional[str] = None,
    runtime_zone: Optional[str] = None,
    metadata: Optional[Dict[str, object]] = None,
    workspace_root: Optional[str] = None,
    max_events: int = 300,
) -> None:
    try:
        activation = build_event(
            event=event,
            source=source,
            target=target or "",
            runtime_zone=runtime_zone or "",
            metadata=metadata,
            ts=int(time.time()),
        )
        path = _event_file_path(Path(workspace_root) if workspace_root else None)
        lines = _read_event_lines(path)
        lines.append(json.dumps(activation, ensure_ascii=False, sort_keys=True))
        if len(lines) > max_events:
            lines = lines[-max_events:]
        _write_event_lines(path, lines)
    except Exception as exc:
        if os.environ.get("PECS_PRO_DEV_MODE") == "1":
            print(
                f"[PECS PRO runtime_activation] emitter failed: {exc}",
                file=sys.stderr,
            )


def event_weight(event: Dict[str, object]) -> int:
    return EVENT_TYPE_WEIGHTS.get(str(event.get("event", "")), 1)
