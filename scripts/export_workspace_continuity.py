from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

ARTIFACT_DIR = ".pecs"
CONTINUITY_DIR = ".pecs/continuity"
ACTIVE_TOPOLOGY_SCHEMA = "pecs.active_topology.v1"
LOCALITY_STATE_SCHEMA = "pecs.locality_state.v1"


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return data


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
            if isinstance(record, dict):
                records.append(record)
        except Exception:
            continue
    return records


def _cluster_paths(paths: Iterable[str]) -> List[Dict[str, Any]]:
    cluster_counts: Counter[str] = Counter()
    for raw in paths:
        path = str(raw).replace("\\", "/").strip()
        if not path:
            continue
        parts = [p for p in path.split("/") if p]
        if not parts:
            continue
        if len(parts) >= 2:
            cluster = "/".join(parts[:2])
        else:
            cluster = parts[0]
        cluster_counts[cluster] += 1

    return [
        {"cluster": key, "count": cluster_counts[key]}
        for key in sorted(cluster_counts, key=lambda k: (-cluster_counts[k], k))
    ]


def _build_locality_file_map(locality_index: Dict[str, Any]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for object_id, value in locality_index.items():
        if isinstance(value, dict):
            file_path = value.get("file")
            if isinstance(file_path, str) and file_path.strip():
                mapping[str(object_id)] = file_path.strip()
    return mapping


def _normalize_runtime_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        normalized.append(
            {
                "event": str(event.get("event", "")).strip(),
                "runtime_zone": str(event.get("runtime_zone", "")).strip(),
                "source": str(event.get("source", "")).strip(),
                "target": str(event.get("target", "")).strip(),
                "ts": (
                    int(event.get("ts", 0)) if str(event.get("ts", "")).isdigit() else 0
                ),
            }
        )
    normalized.sort(
        key=lambda item: (
            item["ts"],
            item["event"],
            item["source"],
            item["target"],
            item["runtime_zone"],
        )
    )
    return normalized


def _resolve_runtime_touched_files(
    events: List[Dict[str, Any]],
    locality_file_map: Dict[str, str],
) -> List[Dict[str, Any]]:
    touched: Counter[str] = Counter()

    def _resolve_id(maybe_id: Any) -> str:
        value = str(maybe_id or "").strip()
        if not value:
            return ""
        if value in locality_file_map:
            return locality_file_map[value]

        # Prefix fallback for anchors like PECS_ID:file.symbol.method
        for key, file_path in locality_file_map.items():
            if value.startswith(key + "."):
                return file_path
        return ""

    for event in events:
        src_file = _resolve_id(event.get("source"))
        tgt_file = _resolve_id(event.get("target"))
        if src_file:
            touched[src_file] += 1
        if tgt_file:
            touched[tgt_file] += 1

    return [
        {"file": file_path, "touch_count": touched[file_path]}
        for file_path in sorted(touched, key=lambda p: (-touched[p], p))
    ]


def _collect_hotspots(
    compact_bundle: Dict[str, Any],
    runtime_touched_files: List[Dict[str, Any]],
    active_context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    hotspot_scores: Counter[str] = Counter()
    reasons: Dict[str, List[str]] = defaultdict(list)

    for entry in compact_bundle.get("bundle", []):
        if not isinstance(entry, dict):
            continue
        object_id = str(entry.get("pecs_id", "")).strip()
        score = (
            int(entry.get("score", 0)) if str(entry.get("score", "")).isdigit() else 0
        )
        if not object_id:
            continue
        hotspot_scores[object_id] += max(1, score)
        reasons[object_id].append("compact_bundle")

    for item in active_context.get("activated_objects", [])[:30]:
        object_id = str(item).strip()
        if not object_id:
            continue
        hotspot_scores[object_id] += 2
        reasons[object_id].append("runtime_activation")

    for touched in runtime_touched_files[:20]:
        file_path = str(touched.get("file", "")).strip()
        count = int(touched.get("touch_count", 0))
        if not file_path:
            continue
        synthetic_id = f"PECS_ID:{file_path.replace('/', '.').removesuffix('.py')}"
        hotspot_scores[synthetic_id] += max(1, count)
        reasons[synthetic_id].append("runtime_touched_file")

    ordered = sorted(hotspot_scores, key=lambda k: (-hotspot_scores[k], k))
    return [
        {
            "id": object_id,
            "score": hotspot_scores[object_id],
            "signals": sorted(set(reasons[object_id])),
        }
        for object_id in ordered[:20]
    ]


def _validate_runtime_topology(
    topology_compact: Dict[str, Any],
    events: List[Dict[str, Any]],
    compact_bundle: Dict[str, Any],
) -> Dict[str, Any]:
    edge_pairs = {
        (
            str(edge.get("from", "")).strip(),
            str(edge.get("to", "")).strip(),
        )
        for edge in topology_compact.get("edges", [])
        if isinstance(edge, dict)
    }

    runtime_pairs = {
        (
            str(event.get("source", "")).strip(),
            str(event.get("target", "")).strip(),
        )
        for event in events
        if isinstance(event, dict)
    }

    supported_pairs = runtime_pairs.intersection(edge_pairs)

    bundled_ids = {
        str(entry.get("pecs_id", "")).strip()
        for entry in compact_bundle.get("bundle", [])
        if isinstance(entry, dict)
    }

    activated_ids = {
        str(event.get("source", "")).strip()
        for event in events
        if isinstance(event, dict)
    }
    bundled_activated = activated_ids.intersection(bundled_ids)

    evidence_count = len(events)
    runtime_confirmation_density = _safe_ratio(len(supported_pairs), evidence_count)
    active_topology_targeting = _safe_ratio(len(bundled_activated), len(bundled_ids))

    return {
        "runtime_evidence_count": evidence_count,
        "runtime_confirmations": len(supported_pairs),
        "active_topology_targeting": active_topology_targeting,
        "runtime_confirmation_density": runtime_confirmation_density,
    }


def _build_validation_metrics(
    recent_edit_clusters: List[Dict[str, Any]],
    repeated_modifications: List[Dict[str, Any]],
    compact_bundle: Dict[str, Any],
    hotspots: List[Dict[str, Any]],
    runtime_validation: Dict[str, Any],
) -> Dict[str, float]:
    bundle_count = (
        len(compact_bundle.get("bundle", [])) if isinstance(compact_bundle, dict) else 0
    )
    hotspot_count = len(hotspots)
    cluster_count = len(recent_edit_clusters)
    repeated_count = len(repeated_modifications)

    return {
        "edit_locality_improvement": _safe_ratio(repeated_count, cluster_count),
        "active_topology_targeting": float(
            runtime_validation.get("active_topology_targeting", 0.0)
        ),
        "continuity_hotspot_identification": _safe_ratio(
            hotspot_count, max(bundle_count, hotspot_count)
        ),
        "runtime_confirmation_density": float(
            runtime_validation.get("runtime_confirmation_density", 0.0)
        ),
        "continuity_compression_effectiveness": _safe_ratio(
            hotspot_count + cluster_count, max(bundle_count, 1)
        ),
    }


def _build_workspace_trajectory(
    active_topology_zone: str,
    recent_edit_clusters: List[Dict[str, Any]],
) -> str:
    if recent_edit_clusters:
        return f"{active_topology_zone}:{recent_edit_clusters[0]['cluster']}"
    return active_topology_zone


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, lines: List[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def export_workspace_continuity(workspace_root: Path) -> Dict[str, Any]:
    artifact_dir = workspace_root / ARTIFACT_DIR
    continuity_dir = workspace_root / CONTINUITY_DIR
    continuity_dir.mkdir(parents=True, exist_ok=True)

    topology_compact = _read_json(artifact_dir / "topology_compact.json", {})
    locality_index = _read_json(artifact_dir / "locality_index.json", {})
    compact_bundle = _read_json(artifact_dir / "compact_bundle.json", {})
    active_context = _read_json(artifact_dir / "active_context.json", {})
    session_context = _read_json(artifact_dir / "session_context.json", {})
    daemon_state = _read_json(artifact_dir / "daemon_state.json", {})
    runtime_events = _normalize_runtime_events(
        _read_jsonl(artifact_dir / "runtime_activation.jsonl")
    )

    locality_file_map = _build_locality_file_map(
        locality_index if isinstance(locality_index, dict) else {}
    )

    changed_files = daemon_state.get("changed_files", [])
    active_paths = session_context.get("active_paths", [])
    recent_edit_clusters = _cluster_paths([*changed_files, *active_paths])

    repeated_modifications = [
        cluster for cluster in recent_edit_clusters if int(cluster.get("count", 0)) >= 2
    ]

    runtime_touched_files = _resolve_runtime_touched_files(
        runtime_events, locality_file_map
    )

    active_regions = {
        "active_topology_zone": compact_bundle.get(
            "active_topology_zone", "general_runtime"
        ),
        "active_runtime_zones": compact_bundle.get("active_runtime_zones", []),
    }

    hotspots = _collect_hotspots(
        compact_bundle if isinstance(compact_bundle, dict) else {},
        runtime_touched_files,
        active_context if isinstance(active_context, dict) else {},
    )

    runtime_validation = _validate_runtime_topology(
        topology_compact if isinstance(topology_compact, dict) else {},
        runtime_events,
        compact_bundle if isinstance(compact_bundle, dict) else {},
    )
    validation_metrics = _build_validation_metrics(
        recent_edit_clusters,
        repeated_modifications,
        compact_bundle if isinstance(compact_bundle, dict) else {},
        hotspots,
        runtime_validation,
    )
    workspace_trajectory = _build_workspace_trajectory(
        str(active_regions.get("active_topology_zone", "general_runtime")),
        recent_edit_clusters,
    )

    ownership_density_counter: Counter[str] = Counter()
    for edge in (
        topology_compact.get("edges", []) if isinstance(topology_compact, dict) else []
    ):
        if not isinstance(edge, dict):
            continue
        source_id = str(edge.get("from", "")).strip()
        if source_id:
            ownership_density_counter[source_id] += 1

    ownership_density = [
        {"id": key, "edge_count": ownership_density_counter[key]}
        for key in sorted(
            ownership_density_counter, key=lambda k: (-ownership_density_counter[k], k)
        )[:20]
    ]

    active_topology_payload = {
        "schema": ACTIVE_TOPOLOGY_SCHEMA,
        "active_topology_zone": active_regions["active_topology_zone"],
        "active_runtime_zones": active_regions["active_runtime_zones"],
        "workspace_trajectory": workspace_trajectory,
        "continuity_hotspots": hotspots,
        "runtime_validation": runtime_validation,
        "validation_metrics": validation_metrics,
    }

    locality_state_payload = {
        "schema": LOCALITY_STATE_SCHEMA,
        "active_locality_clusters": recent_edit_clusters[:12],
        "repeated_edit_clusters": repeated_modifications[:8],
        "active_runtime_touched_files": runtime_touched_files[:12],
        "ownership_hotspots": ownership_density[:12],
        "continuity_hotspots": hotspots[:10],
        "validation_metrics": validation_metrics,
    }

    unresolved_tensions: List[str] = []
    if not topology_compact:
        unresolved_tensions.append("topology_compact.json missing or empty")
    if runtime_validation.get("runtime_evidence_count", 0) == 0:
        unresolved_tensions.append("no runtime activation evidence available")
    if (
        runtime_validation.get("runtime_confirmation_density", 0.0) < 0.2
        and runtime_validation.get("runtime_evidence_count", 0) > 0
    ):
        unresolved_tensions.append(
            "runtime evidence weakly aligned with topology edges"
        )
    if not hotspots:
        unresolved_tensions.append("continuity hotspots unresolved")

    _write_json(continuity_dir / "active_topology.json", active_topology_payload)
    _write_json(continuity_dir / "locality_state.json", locality_state_payload)

    _write_markdown(
        continuity_dir / "architectural_decisions.md",
        [
            "# Architectural Decisions",
            "",
            "- PECS continuity state remains topology-first and deterministic.",
            "- Runtime activation is used as sparse validation evidence, not reconstruction authority.",
            "- Continuity exports are compact, human-readable, and append-light.",
            "- Continuity snapshots preserve only architectural state, locality, hotspots, and unresolved tensions.",
            f"- Active topology zone: {active_regions['active_topology_zone']}.",
        ],
    )

    _write_markdown(
        continuity_dir / "unresolved_tensions.md",
        [
            "# Unresolved Tensions",
            "",
            *(
                [f"- {item}" for item in unresolved_tensions]
                if unresolved_tensions
                else ["- no unresolved tensions detected"]
            ),
        ],
    )

    focus_lines = [
        "# Current Workspace Focus",
        "",
        f"- Active topology zone: {active_regions['active_topology_zone']}",
        f"- Workspace trajectory: {workspace_trajectory}",
        f"- Runtime evidence count: {runtime_validation['runtime_evidence_count']}",
        f"- Runtime confirmation density: {runtime_validation['runtime_confirmation_density']}",
        "",
        "## Active Locality Clusters",
    ]

    if recent_edit_clusters:
        for cluster in recent_edit_clusters[:5]:
            focus_lines.append(f"- {cluster['cluster']} (count={cluster['count']})")
    else:
        focus_lines.append("- none")

    focus_lines.extend(
        [
            "",
            "## Continuity Hotspots",
        ]
    )

    if hotspots:
        for item in hotspots[:10]:
            focus_lines.append(
                f"- {item['id']} (score={item['score']}, signals={','.join(item['signals'])})"
            )
    else:
        focus_lines.append("- none")

    _write_markdown(continuity_dir / "current_workspace_focus.md", focus_lines)

    return {
        "continuity_dir": str(continuity_dir),
        "active_topology": str(continuity_dir / "active_topology.json"),
        "locality_state": str(continuity_dir / "locality_state.json"),
        "architectural_decisions": str(continuity_dir / "architectural_decisions.md"),
        "unresolved_tensions": str(continuity_dir / "unresolved_tensions.md"),
        "current_workspace_focus": str(continuity_dir / "current_workspace_focus.md"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export minimal PECS workspace continuity stabilization state."
    )
    parser.add_argument(
        "workspace_root",
        nargs="?",
        default=".",
        help="Workspace root containing .pecs artifacts (default: current directory).",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    result = export_workspace_continuity(workspace_root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
