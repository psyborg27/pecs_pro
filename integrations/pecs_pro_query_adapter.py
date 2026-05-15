from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class PECSProQueryAdapter:
    """PECS-PRO query adapter for stateless locality projection."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root).resolve()
        self.pecs_root = self.workspace_root / ".pecs"
        self.continuity_dir = self.pecs_root / "continuity"
        self._load_artifacts()

    def _load_json(self, path: Path, default: Any = None) -> Any:
        if default is None:
            default = {}
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default

    def _load_artifacts(self) -> None:
        self.active_context = self._load_json(
            self.pecs_root / "active_context.json", {}
        )
        self.compact_bundle = self._load_json(
            self.pecs_root / "compact_bundle.json", {}
        )
        self.locality_index = self._load_json(
            self.pecs_root / "locality_index.json", {}
        )
        self.topology_compact = self._load_json(
            self.pecs_root / "topology_compact.json", {}
        )
        self.locality_state = self._load_json(
            self.continuity_dir / "locality_state.json", {}
        )
        self.active_topology = self._load_json(
            self.continuity_dir / "active_topology.json", {}
        )
        self.engineering_continuity = self._load_json(
            self.continuity_dir / "engineering_continuity_state.json",
            {
                "schema": "pecs.engineering_continuity.v1",
                "active_engineering_chains": [],
                "updated_at": "",
            },
        )

    def refresh(self) -> None:
        self._load_artifacts()

    def _normalize_path(self, path: str) -> str:
        if not path:
            return ""
        normalized = path.replace("\\", "/").strip()
        normalized = re.sub(r"^\.\/", "", normalized)
        normalized = normalized.replace(
            str(self.workspace_root).replace("\\", "/") + "/", ""
        )
        return normalized

    def _build_file_map(self) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        if isinstance(self.locality_index, dict):
            for object_id, value in self.locality_index.items():
                if isinstance(value, dict):
                    file_path = value.get("file")
                    if isinstance(file_path, str) and file_path.strip():
                        mapping[str(object_id)] = self._normalize_path(
                            file_path.strip()
                        )
        return mapping

    def _file_from_bundle_entry(self, entry: Dict[str, Any]) -> Optional[str]:
        if not isinstance(entry, dict):
            return None
        file_path = entry.get("file") or entry.get("path") or entry.get("source_file")
        if isinstance(file_path, str) and file_path.strip():
            return self._normalize_path(file_path.strip())
        return None

    def issue_term_lookup(self, term: str) -> List[Dict[str, Any]]:
        term_lower = str(term or "").lower().strip()
        if not term_lower:
            return []
        matches: List[Dict[str, Any]] = []
        for entry in (
            self.compact_bundle.get("bundle", [])
            if isinstance(self.compact_bundle, dict)
            else []
        ):
            if not isinstance(entry, dict):
                continue
            combined = " ".join(
                str(entry.get(field, "") or "")
                for field in ["pecs_id", "title", "summary", "description"]
            ).lower()
            if term_lower in combined:
                matches.append(entry)
        return matches

    def runtime_zone_lookup(self, zone_id: Optional[str] = None) -> List[str]:
        zone_id = str(zone_id or "").strip()
        zones = []
        if isinstance(self.active_topology, dict):
            zones = self.active_topology.get("active_runtime_zones", []) or []
        if zone_id:
            return [zone for zone in zones if zone_id in zone]
        return zones

    def locality_cluster_lookup(self, cluster_id: str) -> Dict[str, Any]:
        if not cluster_id:
            return {}
        for cluster in (
            self.locality_state.get("active_locality_clusters", [])
            if isinstance(self.locality_state, dict)
            else []
        ):
            if cluster.get("cluster") == cluster_id:
                return cluster
        return {}

    def runtime_target_candidates(self, max_targets: int = 48) -> List[Dict[str, Any]]:
        """Return confidence-ordered runtime target candidates.

        This method is query-only and reads PECS-PRO artifacts. It never scans the workspace.
        """
        file_map = self._build_file_map()
        candidates: List[Dict[str, Any]] = []

        for object_id in (
            self.active_context.get("activated_objects", [])
            if isinstance(self.active_context, dict)
            else []
        ):
            file_path = file_map.get(str(object_id))
            if file_path:
                candidates.append(
                    {
                        "file": file_path,
                        "evidence": "active_object",
                        "base_confidence": 0.95,
                        "is_active": True,
                    }
                )

        for touched in (
            self.locality_state.get("active_runtime_touched_files", [])
            if isinstance(self.locality_state, dict)
            else []
        ):
            file_path = touched.get("file")
            if isinstance(file_path, str) and file_path.strip():
                candidates.append(
                    {
                        "file": self._normalize_path(file_path),
                        "evidence": "touched_file",
                        "base_confidence": 0.85,
                        "is_active": True,
                    }
                )

        for entry in (
            self.compact_bundle.get("bundle", [])
            if isinstance(self.compact_bundle, dict)
            else []
        ):
            file_path = self._file_from_bundle_entry(entry)
            if file_path:
                candidates.append(
                    {
                        "file": file_path,
                        "evidence": "bundle_entry",
                        "base_confidence": 0.55,
                        "is_active": False,
                    }
                )

        dedup: Dict[str, Dict[str, Any]] = {}
        for candidate in candidates:
            path = str(candidate.get("file", "") or "")
            if not path or path.startswith(".pecs/"):
                continue

            existing = dedup.get(path)
            if existing is None or float(candidate.get("base_confidence", 0.0)) > float(
                existing.get("base_confidence", 0.0)
            ):
                dedup[path] = candidate

        ranked = sorted(
            dedup.values(),
            key=lambda x: (
                -float(x.get("base_confidence", 0.0)),
                not bool(x.get("is_active", False)),
                str(x.get("file", "")),
            ),
        )

        return ranked[:max_targets]

    def runtime_target_lookup(
        self, max_targets: int = 12, model_size: str = "small"
    ) -> List[str]:
        candidates = self.runtime_target_candidates(max_targets=max_targets)
        unique_targets = [
            str(item.get("file", "")) for item in candidates if item.get("file")
        ]

        if model_size == "small":
            return unique_targets[:6]
        if model_size == "medium":
            return unique_targets[:12]
        return unique_targets[:20]

    def ownership_locality_lookup(self) -> str:
        top_touched = (
            self.locality_state.get("active_runtime_touched_files", [])
            if isinstance(self.locality_state, dict)
            else []
        )
        if top_touched:
            return self._normalize_path(
                top_touched[0].get("file", "")
                if isinstance(top_touched[0], dict)
                else ""
            )
        hotspot = (
            self.locality_state.get("ownership_hotspots", [])
            if isinstance(self.locality_state, dict)
            else []
        )
        if hotspot and isinstance(hotspot[0], dict):
            return self._normalize_path(hotspot[0].get("id", ""))
        return ""

    def wrapper_warning_lookup(self) -> bool:
        clusters = (
            self.locality_state.get("active_locality_clusters", [])
            if isinstance(self.locality_state, dict)
            else []
        )
        touched_files = (
            self.locality_state.get("active_runtime_touched_files", [])
            if isinstance(self.locality_state, dict)
            else []
        )
        return len(clusters) > 3 and len(touched_files) > 8

    def execution_depth_lookup(self) -> str:
        zone_count = len(self.runtime_zone_lookup())
        cluster_count = len(
            self.locality_state.get("active_locality_clusters", [])
            if isinstance(self.locality_state, dict)
            else []
        )
        if zone_count >= 3 or cluster_count >= 4:
            return "deep"
        if zone_count == 2 or cluster_count == 3:
            return "moderate"
        return "shallow"

    def active_continuity_lookup(self) -> Dict[str, Any]:
        return {
            "active_topology_zone": self.active_topology.get(
                "active_topology_zone", "general_runtime"
            ),
            "active_runtime_zones": self.active_topology.get(
                "active_runtime_zones", []
            ),
            "active_context_size": (
                len(self.active_context.get("activated_objects", []))
                if isinstance(self.active_context, dict)
                else 0
            ),
            "locality_cluster_count": (
                len(self.locality_state.get("active_locality_clusters", []))
                if isinstance(self.locality_state, dict)
                else 0
            ),
            "runtime_confirmation_density": (
                float(
                    self.active_topology.get("runtime_validation", {}).get(
                        "runtime_confirmation_density", 0.0
                    )
                )
                if isinstance(self.active_topology, dict)
                else 0.0
            ),
            "engineering_chain_count": (
                len(self.engineering_continuity.get("active_engineering_chains", []))
                if isinstance(self.engineering_continuity, dict)
                else 0
            ),
        }

    def engineering_continuity_lookup(
        self,
        issue_query: str = "",
        max_chains: int = 4,
    ) -> Dict[str, Any]:
        """Return compact engineering continuity signals.

        This returns structured signals only (issue->locality->outcome chains).
        It never returns raw chat transcripts or verbose conversational history.
        """

        chains = (
            self.engineering_continuity.get("active_engineering_chains", [])
            if isinstance(self.engineering_continuity, dict)
            else []
        )

        query_tokens = [
            token
            for token in re.split(r"[^a-z0-9_]+", str(issue_query or "").lower())
            if len(token) > 2
        ]

        accepted_scores: Dict[str, float] = {}
        rejected_scores: Dict[str, float] = {}
        normalized_chains: List[Dict[str, Any]] = []

        for item in chains:
            if not isinstance(item, dict):
                continue

            issue = str(item.get("issue", "") or "").strip()
            accepted_locality = self._normalize_path(
                str(item.get("accepted_locality", "") or "")
            )
            if not accepted_locality or accepted_locality.startswith(".pecs/"):
                continue

            rejected_locality = [
                self._normalize_path(str(path or ""))
                for path in (item.get("rejected_locality", []) or [])
                if str(path or "").strip()
                and not self._normalize_path(str(path or "")).startswith(".pecs/")
            ]

            if query_tokens:
                lowered_issue = issue.lower()
                token_hits = sum(1 for token in query_tokens if token in lowered_issue)
                if token_hits == 0:
                    continue

            base_strength = float(item.get("continuity_strength", 0.55) or 0.55)
            locality_stability = float(item.get("locality_stability", 0.55) or 0.55)
            accepted_followup = bool(item.get("accepted_followup", False))
            repeat_success = int(item.get("repeat_success_count", 0) or 0)
            rollback_count = int(item.get("rollback_count", 0) or 0)
            abandoned_count = int(item.get("abandoned_count", 0) or 0)
            contradictory_followups = int(item.get("contradictory_followups", 0) or 0)

            confidence = base_strength
            if accepted_followup:
                confidence += 0.08
            if locality_stability >= 0.80:
                confidence += 0.06
            if repeat_success >= 2:
                confidence += 0.06
            if rollback_count == 0:
                confidence += 0.03
            if rollback_count > 0:
                confidence -= min(0.24, 0.12 * rollback_count)
            if abandoned_count > 0:
                confidence -= min(0.16, 0.08 * abandoned_count)
            if contradictory_followups > 0:
                confidence -= min(0.18, 0.06 * contradictory_followups)

            confidence = max(0.0, min(1.0, confidence))

            accepted_scores[accepted_locality] = max(
                accepted_scores.get(accepted_locality, 0.0), confidence
            )

            for rejected in rejected_locality:
                rejected_scores[rejected] = max(
                    rejected_scores.get(rejected, 0.0),
                    0.45 + (0.30 if rollback_count > 0 else 0.0),
                )

            unresolved = [
                self._normalize_path(str(path or ""))
                for path in (item.get("unresolved_locality", []) or [])
                if str(path or "").strip()
                and not self._normalize_path(str(path or "")).startswith(".pecs/")
            ]

            normalized_chains.append(
                {
                    "issue": issue,
                    "accepted_locality": accepted_locality,
                    "rejected_locality": rejected_locality,
                    "continuity_confidence": round(confidence, 3),
                    "accepted_followup": accepted_followup,
                    "locality_stability": round(locality_stability, 3),
                    "stable_engineering_owner": str(
                        item.get("stable_engineering_owner", accepted_locality) or ""
                    ),
                    "unresolved_locality": unresolved,
                    "runtime_ambiguity": bool(item.get("runtime_ambiguity", False)),
                    "continuity_outcome": str(
                        item.get("continuity_outcome", "accepted") or "accepted"
                    ),
                }
            )

        normalized_chains.sort(
            key=lambda chain: (-float(chain["continuity_confidence"]), chain["issue"])
        )
        bounded_chains = normalized_chains[: max(1, max_chains)]

        return {
            "schema": "pecs.engineering_continuity_projection.v1",
            "active_engineering_chains": bounded_chains,
            "accepted_locality_scores": accepted_scores,
            "rejected_locality_scores": rejected_scores,
            "has_high_confidence_continuity": any(
                float(chain.get("continuity_confidence", 0.0)) >= 0.75
                for chain in bounded_chains
            ),
        }

    def runtime_confirmed_neighborhood_lookup(
        self, max_neighbors: int = 12
    ) -> List[str]:
        neighborhood: List[str] = []
        for obj in (
            self.active_context.get("activated_objects", [])
            if isinstance(self.active_context, dict)
            else []
        ):
            file_path = self._build_file_map().get(str(obj))
            if file_path and file_path not in neighborhood:
                neighborhood.append(file_path)
        for touched in (
            self.locality_state.get("active_runtime_touched_files", [])
            if isinstance(self.locality_state, dict)
            else []
        ):
            file_path = touched.get("file")
            if isinstance(file_path, str) and file_path.strip():
                normalized = self._normalize_path(file_path)
                if normalized not in neighborhood:
                    neighborhood.append(normalized)
        return neighborhood[:max_neighbors]

    def get_query_diagnostics(self) -> Dict[str, Any]:
        """Return diagnostics proving query-driven architecture."""
        return {
            "queried_pecs_pro": True,
            "workspace_scan_performed": False,
            "topology_reconstructed": False,
            "continuity_state_owned": False,
            "projection_mode": "query_driven",
            "artifacts_accessed": [
                ".pecs/active_context.json",
                ".pecs/compact_bundle.json",
                ".pecs/locality_index.json",
                ".pecs/topology_compact.json",
                ".pecs/continuity/locality_state.json",
                ".pecs/continuity/active_topology.json",
                ".pecs/continuity/engineering_continuity_state.json",
            ],
            "artifacts_not_generated": [
                ".pecs/daemon_lite_v2.pid",
                ".pecs/daemon_lite_v2_state.json",
                ".pecs/pecs_lite_runtime_topology.json",
            ],
        }

    def get_health_metrics(self) -> Dict[str, Any]:
        """Return adapter health and load metrics."""
        return {
            "artifacts_loaded": sum(
                [
                    1 if self.active_context else 0,
                    1 if self.compact_bundle else 0,
                    1 if self.locality_index else 0,
                    1 if self.topology_compact else 0,
                    1 if self.locality_state else 0,
                    1 if self.active_topology else 0,
                ]
            ),
            "activated_object_count": len(
                self.active_context.get("activated_objects", [])
                if isinstance(self.active_context, dict)
                else []
            ),
            "touched_file_count": len(
                self.locality_state.get("active_runtime_touched_files", [])
                if isinstance(self.locality_state, dict)
                else []
            ),
            "bundle_entry_count": len(
                self.compact_bundle.get("bundle", [])
                if isinstance(self.compact_bundle, dict)
                else []
            ),
            "locality_cluster_count": len(
                self.locality_state.get("active_locality_clusters", [])
                if isinstance(self.locality_state, dict)
                else []
            ),
            "runtime_zone_count": len(self.runtime_zone_lookup()),
            "engineering_chain_count": len(
                self.engineering_continuity.get("active_engineering_chains", [])
                if isinstance(self.engineering_continuity, dict)
                else []
            ),
        }
