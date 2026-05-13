from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ContinuityArchaeology:
    """
    Consolidated continuity archaeology infrastructure.

    Tracks:
    - duplicate evolution
    - historical continuity
    - canonical drift
    - regression-prone topology

    This intentionally remains observational only.

    PECS archaeology NEVER mutates runtime truth.
    """

    duplicate_history: Dict[str, List[str]] = field(
        default_factory=dict
    )

    canonical_drift_history: Dict[str, List[str]] = field(
        default_factory=dict
    )

    regression_zones: Dict[str, List[str]] = field(
        default_factory=dict
    )

    def register_duplicate_evolution(
        self,
        cluster_id: str,
        node_ids: List[str],
    ) -> None:
        self.duplicate_history[cluster_id] = node_ids

    def register_regression_zone(
        self,
        zone_id: str,
        node_ids: List[str],
    ) -> None:
        self.regression_zones[zone_id] = node_ids

    def to_dict(self) -> Dict[str, object]:
        return {
            "duplicate_history": (
                self.duplicate_history
            ),
            "canonical_drift_history": (
                self.canonical_drift_history
            ),
            "regression_zones": self.regression_zones,
        }
