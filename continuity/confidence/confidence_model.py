from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class ConfidenceModel:
    """
    Deterministic topology-first confidence model.

    Runtime topology evidence always dominates
    static structural evidence.
    """

    runtime_weight: float = 1.0
    execution_weight: float = 0.95
    dispatch_weight: float = 0.90
    signal_slot_weight: float = 0.90
    subprocess_weight: float = 0.85
    propagation_weight: float = 0.85
    ownership_weight: float = 0.80

    import_weight: float = 0.45
    locality_weight: float = 0.40
    semantic_weight: float = 0.10

    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "runtime_weight": self.runtime_weight,
            "execution_weight": self.execution_weight,
            "dispatch_weight": self.dispatch_weight,
            "signal_slot_weight": self.signal_slot_weight,
            "subprocess_weight": self.subprocess_weight,
            "propagation_weight": self.propagation_weight,
            "ownership_weight": self.ownership_weight,
            "import_weight": self.import_weight,
            "locality_weight": self.locality_weight,
            "semantic_weight": self.semantic_weight,
            "metadata": self.metadata,
        }
