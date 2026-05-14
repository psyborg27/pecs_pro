from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List

from export_workspace_continuity import export_workspace_continuity

EXPECTED_JSON_KEYS = {
    "active_topology.json": [
        "active_runtime_zones",
        "active_topology_zone",
        "continuity_hotspots",
        "runtime_validation",
        "schema",
        "validation_metrics",
        "workspace_trajectory",
    ],
    "locality_state.json": [
        "active_locality_clusters",
        "active_runtime_touched_files",
        "continuity_hotspots",
        "ownership_hotspots",
        "repeated_edit_clusters",
        "schema",
        "validation_metrics",
    ],
}

MAX_FILE_SIZES = {
    "active_topology.json": 16_000,
    "locality_state.json": 24_000,
    "architectural_decisions.md": 4_000,
    "current_workspace_focus.md": 8_000,
    "unresolved_tensions.md": 4_000,
}


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> Dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def validate_workspace_continuity(workspace_root: Path) -> Dict[str, object]:
    export_workspace_continuity(workspace_root)
    continuity_dir = workspace_root / ".pecs" / "continuity"

    baseline_hashes = {
        path.name: _hash_file(path)
        for path in sorted(continuity_dir.iterdir())
        if path.is_file()
    }
    export_workspace_continuity(workspace_root)
    second_hashes = {
        path.name: _hash_file(path)
        for path in sorted(continuity_dir.iterdir())
        if path.is_file()
    }

    deterministic = baseline_hashes == second_hashes

    schema_checks: Dict[str, bool] = {}
    compact_checks: Dict[str, bool] = {}
    for file_name, expected_keys in EXPECTED_JSON_KEYS.items():
        payload = _load_json(continuity_dir / file_name)
        schema_checks[file_name] = list(payload.keys()) == expected_keys
        compact_checks[file_name] = (
            continuity_dir / file_name
        ).stat().st_size <= MAX_FILE_SIZES[file_name]

    for file_name, max_size in MAX_FILE_SIZES.items():
        if file_name not in compact_checks:
            compact_checks[file_name] = (
                continuity_dir / file_name
            ).stat().st_size <= max_size

    active_topology = _load_json(continuity_dir / "active_topology.json")
    runtime_validation = active_topology.get("runtime_validation", {})
    runtime_sparse = (
        isinstance(runtime_validation, dict)
        and int(runtime_validation.get("runtime_evidence_count", 0)) <= 300
    )

    return {
        "deterministic": deterministic,
        "schema_stable": all(schema_checks.values()),
        "runtime_evidence_sparse": runtime_sparse,
        "files_compact": all(compact_checks.values()),
        "no_unexpected_growth": all(compact_checks.values()),
        "schema_checks": schema_checks,
        "compact_checks": compact_checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate PECS continuity export determinism and compactness."
    )
    parser.add_argument(
        "workspace_root",
        nargs="?",
        default=".",
        help="Workspace root containing .pecs artifacts (default: current directory).",
    )
    args = parser.parse_args()

    result = validate_workspace_continuity(Path(args.workspace_root).resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all(
        [
            result["deterministic"],
            result["schema_stable"],
            result["runtime_evidence_sparse"],
            result["files_compact"],
            result["no_unexpected_growth"],
        ]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
