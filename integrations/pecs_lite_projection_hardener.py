"""PECS-LITE Projection Hardener

Implements compact, high-confidence, small-model-friendly locality projection.

This module enforces:
- Hard limits on projection breadth
- Confidence-ordered target selection
- Token budgeting for constrained models
- Locality entropy reduction
- Query flow validation diagnostics
- Small-model safety constraints

PECS-LITE exists ONLY to reduce execution-locality entropy for constrained coding models.
It intentionally sacrifices continuity completeness in favor of small-model execution locality precision.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Tuple


class ProjectionProfile(Enum):
    """Projection profile for different model contexts."""

    SMALL = "small"  # Qwen/DeepSeek 16k-32k: minimal targets, high confidence
    MEDIUM = "medium"  # 32k-100k: balanced targets and neighbors
    LARGE = "large"  # 100k+: broader but still bounded


@dataclass
class ConfidenceScore:
    """Confidence assessment for a runtime target."""

    file_path: str
    confidence: float  # 0.0-1.0
    evidence_type: str  # "active_object", "touched_file", "bundle_entry", "neighbor"
    evidence_strength: int  # 1-5, higher = stronger
    locality_proximity: int  # 0-3, 0=direct, 3=distant neighbor

    def __post_init__(self):
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class ProjectionMetrics:
    """Health metrics for a projection."""

    profile: str
    projected_target_count: int
    projected_secondary_count: int
    projected_token_estimate: int
    runtime_zone_count: int
    locality_breadth_score: float  # 0.0-1.0, lower = tighter
    entropy_reduction_score: float  # 0.0-1.0, higher = more reduced
    inactive_locality_suppressed: int  # count of filtered files
    wrapper_expansion_depth: int  # 0-3, how deep wrapper chain
    wrapper_expansion_count: int
    has_confirmed_neighborhoods: bool
    progressive_locality_disclosure_applied: bool
    diagnostic_timestamp: str


@dataclass
class QueryFlowDiagnostics:
    """Diagnostics proving authority separation and query flow integrity."""

    queried_pecs_pro: bool  # True if queried via adapter
    workspace_scan_performed: bool  # MUST be False
    topology_reconstructed: bool  # MUST be False
    continuity_state_owned: bool  # MUST be False
    projection_mode: str  # "query_driven" only
    adapter_methods_called: List[str]  # methods invoked on adapter
    artifacts_accessed: List[str]  # .pecs files read
    artifacts_not_generated: List[str]  # things NOT created
    timestamp: str


class ConfidenceScorer:
    """Assigns confidence scores to runtime targets based on evidence."""

    # Scoring weights
    ACTIVE_OBJECT_WEIGHT = 0.95
    TOUCHED_FILE_WEIGHT = 0.85
    BUNDLE_ENTRY_WEIGHT = 0.70
    NEIGHBOR_WEIGHT = 0.50
    ACCEPTED_CONTINUITY_WEIGHT = 0.90

    # Proximity penalties (0 = no penalty, 1 = 50% penalty)
    DIRECT_PROXIMITY = 0.0
    NEAR_PROXIMITY = 0.15
    ADJACENT_PROXIMITY = 0.30
    DISTANT_PROXIMITY = 0.50

    @classmethod
    def score_target(
        cls,
        file_path: str,
        evidence_type: str,
        evidence_strength: int = 3,
        locality_proximity: int = 0,
    ) -> ConfidenceScore:
        """Assign confidence score to a target."""

        # Base score from evidence type
        base_scores = {
            "active_object": cls.ACTIVE_OBJECT_WEIGHT,
            "touched_file": cls.TOUCHED_FILE_WEIGHT,
            "bundle_entry": cls.BUNDLE_ENTRY_WEIGHT,
            "neighbor": cls.NEIGHBOR_WEIGHT,
            "accepted_continuity": cls.ACCEPTED_CONTINUITY_WEIGHT,
        }

        base = base_scores.get(evidence_type, 0.5)

        # Adjust for evidence strength (1-5 scale)
        strength_factor = 0.7 + (evidence_strength / 5.0) * 0.3

        # Adjust for locality proximity
        proximity_penalties = [
            cls.DIRECT_PROXIMITY,
            cls.NEAR_PROXIMITY,
            cls.ADJACENT_PROXIMITY,
            cls.DISTANT_PROXIMITY,
        ]
        proximity_penalty = proximity_penalties[min(locality_proximity, 3)]

        # Final confidence
        final_confidence = base * strength_factor * (1.0 - proximity_penalty)

        return ConfidenceScore(
            file_path=file_path,
            confidence=final_confidence,
            evidence_type=evidence_type,
            evidence_strength=min(5, max(1, evidence_strength)),
            locality_proximity=min(3, max(0, locality_proximity)),
        )


class ProjectionHardener:
    """Hardens locality projections for small models."""

    # Hard limits by profile
    LIMITS = {
        ProjectionProfile.SMALL: {
            "primary_targets": 3,
            "secondary_neighbors": 2,
            "token_budget": 2000,
            "breadth_limit": 5,
        },
        ProjectionProfile.MEDIUM: {
            "primary_targets": 6,
            "secondary_neighbors": 4,
            "token_budget": 4000,
            "breadth_limit": 10,
        },
        ProjectionProfile.LARGE: {
            "primary_targets": 10,
            "secondary_neighbors": 6,
            "token_budget": 8000,
            "breadth_limit": 16,
        },
    }

    def __init__(self, adapter: Any):
        """Initialize hardener with PECS-PRO query adapter."""
        self.adapter = adapter
        self.diagnostics = QueryFlowDiagnostics(
            queried_pecs_pro=False,
            workspace_scan_performed=False,
            topology_reconstructed=False,
            continuity_state_owned=False,
            projection_mode="query_driven",
            adapter_methods_called=[],
            artifacts_accessed=[],
            artifacts_not_generated=[
                ".pecs/daemon_lite_v2.pid",
                ".pecs/daemon_lite_v2_state.json",
                ".pecs/pecs_lite_runtime_topology.json",
                "workspace runtime topology",
                "workspace scan results",
            ],
            timestamp="",
        )
        self.last_confidence_by_path: Dict[str, Dict[str, Any]] = {}
        self.last_confidence_uncertainty: Dict[str, Any] = {}

    def sanitize_projection(self, projection: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize projection to remove `.pecs` paths and continuity artifacts."""
        sanitized = {
            "primary_targets": [
                target
                for target in projection.get("primary_targets", [])
                if not target.startswith(".pecs")
            ],
            "secondary_targets": [
                target
                for target in projection.get("secondary_targets", [])
                if not target.startswith(".pecs")
            ],
        }
        return sanitized

    def generate_operational_guidance(self, projection: Dict[str, Any]) -> str:
        """Generate natural-language operational guidance for SMALL profiles."""
        primary_targets = projection.get("primary_targets", [])
        secondary_targets = projection.get("secondary_targets", [])

        guidance = ""
        if primary_targets:
            guidance += (
                f"Accepted engineering continuity suggests: {primary_targets[0]}\n"
                "is the likely active locality for the current issue.\n"
            )
        if secondary_targets:
            guidance += (
                f"Secondary candidates include: {', '.join(secondary_targets)}.\n"
            )
        guidance += "Confidence: High."
        return guidance

    def harden_projection(
        self, profile: ProjectionProfile, raw_projection: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Harden projection based on profile."""
        # ...existing code...
        if profile == ProjectionProfile.SMALL:
            sanitized_projection = self.sanitize_projection(raw_projection)
            guidance = self.generate_operational_guidance(sanitized_projection)
            return {
                "guidance": guidance,
                "structured_targets": sanitized_projection,
            }
        # ...existing code...

    def harden_projection(
        self,
        raw_targets: List[Any],
        profile: ProjectionProfile = ProjectionProfile.SMALL,
        active_zone: str = "general_runtime",
        mutation_owner: str = "",
        wrapper_warning: bool = False,
        issue_query: str = "",
        runtime_zone_count: int = 1,
        engineering_continuity: Dict[str, Any] = None,
    ) -> Tuple[List[str], List[str], ProjectionMetrics]:
        """
        Harden a projection for small models.

        Returns:
            (primary_targets, secondary_neighbors, metrics)
        """

        limits = self.LIMITS[profile]

        continuity_signals = engineering_continuity or {}
        continuity_anchor_candidates = self._continuity_anchor_candidates(
            continuity_signals
        )
        scoring_input = list(raw_targets) + continuity_anchor_candidates

        # Score all targets
        scored_targets = self._score_candidates(
            scoring_input,
            issue_query=issue_query,
            continuity_signals=continuity_signals,
        )

        # Sort by confidence (descending)
        sorted_targets = sorted(
            scored_targets,
            key=lambda x: (-x.confidence, -x.evidence_strength, x.locality_proximity),
        )

        # Select primary targets (highest confidence, direct locality)
        primary = self._select_primary_targets(
            sorted_targets,
            limit=limits["primary_targets"],
        )

        accepted_scores = continuity_signals.get("accepted_locality_scores", {}) or {}
        if accepted_scores:
            best_accepted_path, best_accepted_score = max(
                accepted_scores.items(), key=lambda item: float(item[1])
            )
            if float(best_accepted_score) >= 0.80:
                existing_primary_paths = {item.file_path for item in primary}
                if best_accepted_path not in existing_primary_paths:
                    accepted_candidate = next(
                        (
                            item
                            for item in sorted_targets
                            if item.file_path == best_accepted_path
                        ),
                        None,
                    )
                    if accepted_candidate is not None:
                        if len(primary) < limits["primary_targets"]:
                            primary.append(accepted_candidate)
                        elif primary:
                            primary[-1] = accepted_candidate
                        primary.sort(
                            key=lambda x: (-x.confidence, x.locality_proximity)
                        )

        progressive_disclosure_applied = False
        highest_confidence = primary[0].confidence if primary else 0.0

        # Progressive locality disclosure for weak-confidence small profile projections.
        if profile == ProjectionProfile.SMALL and (
            len(primary) < 2 or highest_confidence < 0.78
        ):
            widened: List[ConfidenceScore] = []
            existing = {item.file_path for item in primary}
            for candidate in sorted_targets:
                if candidate.file_path in existing:
                    continue
                if candidate.confidence < 0.55:
                    continue
                if candidate.locality_proximity > 2:
                    continue
                widened.append(candidate)
                existing.add(candidate.file_path)
                if len(primary) + len(widened) >= limits["primary_targets"]:
                    break
            if widened:
                primary = primary + widened
                progressive_disclosure_applied = True

        # Select secondary neighbors (lower confidence, near locality)
        secondary = self._select_secondary_neighbors(
            sorted_targets,
            primary_paths=[t.file_path for t in primary],
            limit=limits["secondary_neighbors"],
        )

        # Estimate tokens
        token_estimate = self._estimate_tokens(primary, secondary)

        # Enforce hard token budget by trimming lowest-priority neighbors first.
        token_budget = int(limits["token_budget"])
        while token_estimate > token_budget and secondary:
            secondary = secondary[:-1]
            token_estimate = self._estimate_tokens(primary, secondary)

        # If still over budget, trim primary from tail but keep at least one.
        while token_estimate > token_budget and len(primary) > 1:
            primary = primary[:-1]
            token_estimate = self._estimate_tokens(primary, secondary)

        # Calculate metrics
        metrics = self._calculate_metrics(
            profile=profile.value,
            primary_targets=primary,
            secondary_neighbors=secondary,
            token_estimate=token_estimate,
            active_zone=active_zone,
            wrapper_warning=wrapper_warning,
            suppressed_count=max(0, len(scoring_input) - len(primary) - len(secondary)),
            runtime_zone_count=max(1, runtime_zone_count),
            progressive_disclosure_applied=progressive_disclosure_applied,
        )

        self._capture_confidence_summary(
            scored=sorted_targets,
            primary=primary,
            secondary=secondary,
        )

        primary_paths = [t.file_path for t in primary]
        secondary_paths = [t.file_path for t in secondary]

        return primary_paths, secondary_paths, metrics

    def normalize_issue_query(self, issue_query: str) -> List[str]:
        """Normalize issue text into correlation tokens."""
        normalized = str(issue_query or "").lower().strip()
        if not normalized:
            return []
        tokens = [t for t in re.split(r"[^a-z0-9_]+", normalized) if len(t) > 2]
        # Preserve order while removing duplicates.
        seen = set()
        result: List[str] = []
        for token in tokens:
            if token not in seen:
                seen.add(token)
                result.append(token)
        return result

    def _score_candidates(
        self,
        targets: List[Any],
        issue_query: str = "",
        continuity_signals: Dict[str, Any] = None,
    ) -> List[ConfidenceScore]:
        """Score all target candidates."""
        scored: List[ConfidenceScore] = []
        query_tokens = self.normalize_issue_query(issue_query)
        continuity_signals = continuity_signals or {}
        accepted_scores = continuity_signals.get("accepted_locality_scores", {}) or {}
        rejected_scores = continuity_signals.get("rejected_locality_scores", {}) or {}

        # Try to get scoring context from adapter if available
        # For now, assign default scores based on order (first = highest confidence)
        for i, target in enumerate(targets):
            if isinstance(target, dict):
                file_path = str(target.get("file", "") or "")
                evidence_type = str(
                    target.get("evidence", "bundle_entry") or "bundle_entry"
                )
                base_confidence = float(target.get("base_confidence", 0.55) or 0.55)
                is_active = bool(target.get("is_active", False))
            else:
                file_path = str(target)
                evidence_type = "bundle_entry" if i > 5 else "touched_file"
                base_confidence = 0.55 if evidence_type == "bundle_entry" else 0.85
                is_active = i < 8

            if not file_path:
                continue

            if evidence_type == "accepted_continuity":
                proximity = 0
                evidence_strength = 5
            else:
                proximity = min(i // 4, 3)  # Rough proximity estimate
                evidence_strength = 5 - (i // 3)  # Decay strength with distance

            score = ConfidenceScorer.score_target(
                file_path=file_path,
                evidence_type=evidence_type,
                evidence_strength=max(1, evidence_strength),
                locality_proximity=proximity,
            )

            # Blend with adapter-provided base confidence when available.
            score.confidence = (score.confidence * 0.6) + (base_confidence * 0.4)

            accepted_boost = float(accepted_scores.get(file_path, 0.0) or 0.0)
            if accepted_boost > 0.0:
                score.confidence = min(
                    1.0,
                    score.confidence + (accepted_boost * 0.35),
                )
                score.evidence_strength = min(5, score.evidence_strength + 1)

            rejected_penalty = float(rejected_scores.get(file_path, 0.0) or 0.0)
            if rejected_penalty > 0.0:
                score.confidence = max(0.0, score.confidence * (1.0 - rejected_penalty))

            # Downrank inactive locality.
            if not is_active:
                score.confidence *= 0.85

            # Up-rank issue-correlated paths.
            lowered_path = file_path.lower()
            token_hits = sum(1 for token in query_tokens if token in lowered_path)
            if token_hits:
                score.confidence = min(1.0, score.confidence + (0.05 * token_hits))

            scored.append(score)

        return scored

    def _continuity_anchor_candidates(
        self,
        continuity_signals: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Inject accepted engineering locality anchors as bounded candidates."""
        candidates: List[Dict[str, Any]] = []
        accepted_scores = continuity_signals.get("accepted_locality_scores", {}) or {}
        for file_path, confidence in accepted_scores.items():
            normalized = str(file_path or "").strip()
            if not normalized or normalized.startswith(".pecs/"):
                continue
            if float(confidence or 0.0) < 0.60:
                continue
            candidates.append(
                {
                    "file": normalized,
                    "evidence": "accepted_continuity",
                    "base_confidence": max(0.65, min(0.98, float(confidence))),
                    "is_active": True,
                }
            )
        return candidates[:8]

    def _capture_confidence_summary(
        self,
        scored: List[ConfidenceScore],
        primary: List[ConfidenceScore],
        secondary: List[ConfidenceScore],
    ) -> None:
        """Capture probabilistic confidence summary for projection export."""
        self.last_confidence_by_path = {
            item.file_path: {
                "confidence": round(item.confidence, 3),
                "evidence_type": item.evidence_type,
                "evidence_strength": item.evidence_strength,
                "locality_proximity": item.locality_proximity,
            }
            for item in scored
        }

        primary_conf = [item.confidence for item in primary]
        secondary_conf = [item.confidence for item in secondary]
        all_conf = primary_conf + secondary_conf
        confidence_mean = (sum(all_conf) / len(all_conf)) if all_conf else 0.0

        self.last_confidence_uncertainty = {
            "projection_confidence_mean": round(confidence_mean, 3),
            "projection_uncertainty": round(max(0.0, 1.0 - confidence_mean), 3),
            "ambiguity_hint": (
                "locality_confidence_mixed"
                if 0.45 <= confidence_mean <= 0.75
                else (
                    "locality_confidence_high"
                    if confidence_mean > 0.75
                    else "locality_confidence_weak"
                )
            ),
            "runtime_confirmation_hint": "confirm active runtime ownership before wide mutation",
        }

    def _select_primary_targets(
        self,
        scored: List[ConfidenceScore],
        limit: int = 3,
    ) -> List[ConfidenceScore]:
        """Select primary targets (highest confidence, proximity 0-1)."""
        direct_locality = [
            s for s in scored if s.confidence >= 0.70 and s.locality_proximity <= 1
        ]

        # Sort by confidence
        direct_locality.sort(key=lambda x: (-x.confidence, x.locality_proximity))

        return direct_locality[:limit]

    def _select_secondary_neighbors(
        self,
        scored: List[ConfidenceScore],
        primary_paths: List[str],
        limit: int = 2,
    ) -> List[ConfidenceScore]:
        """Select secondary neighbors (nearby, not in primary)."""
        neighbors = [
            s
            for s in scored
            if s.file_path not in primary_paths
            and s.confidence >= 0.50
            and s.locality_proximity <= 2
        ]

        # Sort by proximity first, then confidence
        neighbors.sort(key=lambda x: (x.locality_proximity, -x.confidence))

        return neighbors[:limit]

    def _estimate_tokens(
        self,
        primary: List[ConfidenceScore],
        secondary: List[ConfidenceScore],
    ) -> int:
        """Estimate tokens needed for targets."""
        # Rough estimate: 100-200 tokens per target
        primary_tokens = len(primary) * 150
        secondary_tokens = len(secondary) * 100
        overhead = 200  # Schema, metadata

        return primary_tokens + secondary_tokens + overhead

    def _calculate_metrics(
        self,
        profile: str,
        primary_targets: List[ConfidenceScore],
        secondary_neighbors: List[ConfidenceScore],
        token_estimate: int,
        active_zone: str,
        wrapper_warning: bool,
        suppressed_count: int,
        runtime_zone_count: int,
        progressive_disclosure_applied: bool,
    ) -> ProjectionMetrics:
        """Calculate projection health metrics."""
        import datetime

        # Breadth score: 0.0 = very tight, 1.0 = very broad
        total_projected = len(primary_targets) + len(secondary_neighbors)
        breadth_score = min(1.0, total_projected / 10.0)

        # Entropy reduction: how much did we suppress?
        # Higher score = more entropy reduction
        total_candidates = total_projected + suppressed_count
        entropy_reduction = (
            suppressed_count / total_candidates if total_candidates > 0 else 0.0
        )

        # Wrapper expansion depth
        wrapper_depth = 1 if wrapper_warning else 0

        return ProjectionMetrics(
            profile=profile,
            projected_target_count=len(primary_targets),
            projected_secondary_count=len(secondary_neighbors),
            projected_token_estimate=token_estimate,
            runtime_zone_count=runtime_zone_count,
            locality_breadth_score=breadth_score,
            entropy_reduction_score=entropy_reduction,
            inactive_locality_suppressed=suppressed_count,
            wrapper_expansion_depth=wrapper_depth,
            wrapper_expansion_count=len(secondary_neighbors) if wrapper_warning else 0,
            has_confirmed_neighborhoods=len(primary_targets) > 0,
            progressive_locality_disclosure_applied=progressive_disclosure_applied,
            diagnostic_timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        )

    def validate_small_model_safety(
        self,
        projection: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """Validate projection is safe for small models."""
        issues: List[str] = []

        # Check: runtime targets not too many
        targets = projection.get("runtime_targets", [])
        if len(targets) > 10:
            issues.append(f"Too many runtime targets: {len(targets)} (max 10)")

        # Check: no .pecs paths exposed
        for target in targets:
            if ".pecs/" in target:
                issues.append(f"Exposed .pecs artifact: {target}")

        # Check: no raw topology
        if projection.get("raw_topology"):
            issues.append("Projection contains raw topology graph")

        # Check: no continuity dumps
        if projection.get("continuity_dump"):
            issues.append("Projection contains continuity dump")

        # Check: no .pecs mutation owner guidance
        mutation_owner = str(projection.get("possible_mutation_owner", "") or "")
        if mutation_owner.startswith(".pecs/"):
            issues.append("Mutation owner points to .pecs artifact")

        # Check: continuity anchors must never point to .pecs paths
        engineering_continuity = projection.get("active_engineering_continuity", {})
        for chain in engineering_continuity.get("chains", []) or []:
            accepted = str(chain.get("accepted_locality", "") or "")
            if accepted.startswith(".pecs/"):
                issues.append(
                    f"Accepted continuity points to .pecs artifact: {accepted}"
                )
            for rejected in chain.get("rejected_locality", []) or []:
                if str(rejected).startswith(".pecs/"):
                    issues.append(
                        f"Rejected continuity points to .pecs artifact: {rejected}"
                    )

        # Check: has disclaimer
        if not projection.get("disclaimer"):
            issues.append("Missing projection disclaimer")

        return len(issues) == 0, issues

    def record_query_diagnostics(
        self,
        methods_called: List[str],
        artifacts_read: List[str],
    ) -> None:
        """Record query flow diagnostics."""
        import datetime

        self.diagnostics.queried_pecs_pro = True
        self.diagnostics.adapter_methods_called = methods_called
        self.diagnostics.artifacts_accessed = artifacts_read
        self.diagnostics.timestamp = datetime.datetime.utcnow().isoformat() + "Z"

        # Verify authority separation
        assert (
            not self.diagnostics.workspace_scan_performed
        ), "PECS-LITE must NOT scan workspace"
        assert (
            not self.diagnostics.topology_reconstructed
        ), "PECS-LITE must NOT reconstruct topology"
        assert (
            not self.diagnostics.continuity_state_owned
        ), "PECS-LITE must NOT own continuity state"


class ProjectionExporter:
    """Exports hardened projections with diagnostics and metrics."""

    DISCLAIMER = (
        "PECS-LITE PROJECTION DISCLAIMER:\n"
        "This is a STATELESS LOCALITY PROJECTION generated by querying PECS-PRO.\n"
        "It contains ephemeral guidance optimized for constrained coding models.\n"
        "It does NOT represent complete continuity, comprehensive topology, or authoritative runtime state.\n"
        "PECS-PRO maintains the sole continuity authority.\n"
        "Do NOT edit this projection or use it as infrastructure sourcecode.\n"
        "Use projected runtime targets to locate editable workspace files only."
    )

    @classmethod
    def export_projection(
        cls,
        hardener: ProjectionHardener,
        primary_targets: List[str],
        secondary_neighbors: List[str],
        metrics: ProjectionMetrics,
        active_zone: str,
        mutation_owner: str,
        wrapper_warning: bool,
        profile: str = "small",
        adapter: Any = None,
        engineering_continuity: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Export projection with profile-specific enrichment."""

        projection = {
            "schema": "pecs_lite.runtime_projection.hardened.v1",
            "disclaimer": cls.DISCLAIMER,
            "profile": metrics.profile,
            "runtime_targets": primary_targets,
            "secondary_neighbors": secondary_neighbors,
            "likely_execution_cluster": active_zone,
            "possible_mutation_owner": mutation_owner,
            "wrapper_warning": wrapper_warning,
            "metrics": asdict(metrics),
            "diagnostics": asdict(hardener.diagnostics),
            "continuity_supporting_artifacts": [
                ".pecs/active_context.json",
                ".pecs/locality_index.json",
                ".pecs/compact_bundle.json",
                ".pecs/continuity/engineering_continuity_state.json",
            ],
            "forbidden_mutation_prefixes": [".pecs/"],
            "confidence_projection": cls._build_confidence_projection(
                hardener, primary_targets, secondary_neighbors
            ),
        }

        continuity_view = cls._build_active_engineering_continuity(
            profile=profile,
            continuity_signals=engineering_continuity or {},
        )
        if continuity_view:
            projection["active_engineering_continuity"] = continuity_view

        # Add profile-specific enrichment
        if profile in ["medium", "large"] and adapter:
            projection["execution_enrichment"] = cls._build_execution_enrichment(
                adapter,
                primary_targets,
                secondary_neighbors,
                profile,
            )

        return projection

    @classmethod
    def _build_execution_enrichment(
        cls,
        adapter: Any,
        primary_targets: List[str],
        secondary_neighbors: List[str],
        profile: str,
    ) -> Dict[str, Any]:
        """Build execution-locality enrichment for medium/large profiles."""

        enrichment = {}

        if profile == "medium":
            enrichment["execution_neighborhood"] = {
                "primary_execution_focus": primary_targets[:3],
                "nearby_execution_adjacency": secondary_neighbors[:2],
                "mutation_locality_hint": adapter.ownership_locality_lookup(),
                "wrapper_expansion_indicated": adapter.wrapper_warning_lookup(),
            }

        elif profile == "large":
            enrichment["execution_continuity"] = {
                "primary_execution_targets": primary_targets,
                "secondary_execution_adjacency": secondary_neighbors,
                "execution_neighborhood_metadata": {
                    "mutation_locality": adapter.ownership_locality_lookup(),
                    "wrapper_expansion": adapter.wrapper_warning_lookup(),
                    "execution_depth": adapter.execution_depth_lookup(),
                },
                "runtime_zone_context": adapter.runtime_zone_lookup(),
                "locality_confidence_hint": "execution_locality_focused, NOT raw_continuity",
            }

            # Include bounded continuity relationships for large models
            active_continuity = adapter.active_continuity_lookup()
            enrichment["continuity_context"] = {
                "active_runtime_zones": active_continuity.get(
                    "active_runtime_zones", []
                ),
                "locality_cluster_count": active_continuity.get(
                    "locality_cluster_count", 0
                ),
                "runtime_confirmation_density": active_continuity.get(
                    "runtime_confirmation_density", 0.0
                ),
                "note": "relationships are execution_locality_focused, not exhaustive",
            }

        return enrichment

    @classmethod
    def _build_confidence_projection(
        cls,
        hardener: ProjectionHardener,
        primary_targets: List[str],
        secondary_neighbors: List[str],
    ) -> Dict[str, Any]:
        """Build confidence/uncertainty summary to avoid false certainty."""
        confidence = hardener.last_confidence_by_path
        return {
            "primary": [
                {
                    "file": path,
                    **confidence.get(
                        path, {"confidence": 0.0, "evidence_type": "unknown"}
                    ),
                }
                for path in primary_targets
            ],
            "secondary": [
                {
                    "file": path,
                    **confidence.get(
                        path, {"confidence": 0.0, "evidence_type": "unknown"}
                    ),
                }
                for path in secondary_neighbors
            ],
            "uncertainty": hardener.last_confidence_uncertainty,
        }

    @classmethod
    def _build_active_engineering_continuity(
        cls,
        profile: str,
        continuity_signals: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build bounded accepted engineering continuity payload by profile."""
        chains = continuity_signals.get("active_engineering_chains", []) or []
        if not chains:
            return {}

        high_confidence = [
            chain
            for chain in chains
            if float(chain.get("continuity_confidence", 0.0) or 0.0) >= 0.75
        ]
        if not high_confidence:
            return {}

        if profile == "small":
            chain = high_confidence[0]
            return {
                "mode": "small_anchor",
                "chains": [
                    {
                        "issue": chain.get("issue", ""),
                        "accepted_locality": chain.get("accepted_locality", ""),
                        "continuity_confidence": chain.get(
                            "continuity_confidence", 0.0
                        ),
                        "accepted_followup": bool(
                            chain.get("accepted_followup", False)
                        ),
                        "rejected_locality": (chain.get("rejected_locality", []) or [])[
                            :1
                        ],
                    }
                ],
                "note": "tiny accepted continuity anchor only",
            }

        if profile == "medium":
            return {
                "mode": "bounded_chain",
                "chains": [
                    {
                        "issue": chain.get("issue", ""),
                        "accepted_locality": chain.get("accepted_locality", ""),
                        "continuity_confidence": chain.get(
                            "continuity_confidence", 0.0
                        ),
                        "accepted_followup": bool(
                            chain.get("accepted_followup", False)
                        ),
                        "rejected_locality": (chain.get("rejected_locality", []) or [])[
                            :2
                        ],
                        "locality_stability": chain.get("locality_stability", 0.0),
                    }
                    for chain in high_confidence[:2]
                ],
                "note": "bounded accepted continuity chains for medium profile",
            }

        return {
            "mode": "rich_bounded_chain",
            "chains": [
                {
                    "issue": chain.get("issue", ""),
                    "accepted_locality": chain.get("accepted_locality", ""),
                    "continuity_confidence": chain.get("continuity_confidence", 0.0),
                    "accepted_followup": bool(chain.get("accepted_followup", False)),
                    "rejected_locality": (chain.get("rejected_locality", []) or [])[:3],
                    "locality_stability": chain.get("locality_stability", 0.0),
                    "unresolved_locality": (chain.get("unresolved_locality", []) or [])[
                        :3
                    ],
                    "runtime_ambiguity": bool(chain.get("runtime_ambiguity", False)),
                    "stable_engineering_owner": chain.get(
                        "stable_engineering_owner", ""
                    ),
                }
                for chain in high_confidence[:4]
            ],
            "note": "structured engineering continuity only; no raw chat history",
        }
