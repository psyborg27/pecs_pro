from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from ..execution_graph.indexes.graph_index import (
    GraphIndex,
)
from ..topology.indexing.locality_index import (
    LocalityIndex,
)


@dataclass
class ContinuityValidator:
    """
    Consolidated PECS continuity integrity validator.

    This intentionally consolidates:
    - topology integrity validation
    - locality integrity validation
    - duplicate authority detection
    - continuity fragmentation detection
    - runtime continuity safeguards

    into ONE validation authority.

    PECS intentionally avoids:
    - validation orchestration layers
    - multi-validator forests
    - recursive integrity daemons

    Validation remains:
    deterministic
    observational
    topology-oriented
    continuity-safe

    Validation NEVER mutates runtime truth.
    """

    graph_index: GraphIndex
    locality_index: LocalityIndex

    validation_metadata: Dict[str, object] = field(
        default_factory=dict
    )

    def validate_graph_integrity(
        self,
    ) -> Dict[str, object]:
        orphan_nodes: List[str] = []

        for node_id in self.graph_index.node_index:
            referenced = False

            for edge_data in (
                self.graph_index.edge_index.values()
            ):
                edge_values = str(edge_data)

                if node_id in edge_values:
                    referenced = True
                    break

            if not referenced:
                orphan_nodes.append(node_id)

        return {
            "orphan_nodes": orphan_nodes,
            "orphan_count": len(orphan_nodes),
        }

    def validate_locality_integrity(
        self,
    ) -> Dict[str, object]:
        empty_localities: List[str] = []

        for (
            object_id,
            locality,
        ) in self.locality_index.object_locality.items():
            if not locality:
                empty_localities.append(object_id)

        return {
            "empty_localities": empty_localities,
            "empty_locality_count": (
                len(empty_localities)
            ),
        }

    def detect_duplicate_authorities(
        self,
    ) -> Dict[str, object]:
        duplicate_zones: Dict[str, Set[str]] = {}

        for (
            zone_id,
            node_ids,
        ) in self.graph_index.zone_index.items():
            duplicate_zones.setdefault(
                zone_id,
                set(),
            ).update(node_ids)

        duplicates = {
            zone_id: sorted(nodes)
            for zone_id, nodes
            in duplicate_zones.items()
            if len(nodes) > 1
        }

        return {
            "duplicate_authority_zones": duplicates,
            "duplicate_zone_count": len(
                duplicates
            ),
        }

    def validate_continuity_state(
        self,
    ) -> Dict[str, object]:
        return {
            "graph_integrity": (
                self.validate_graph_integrity()
            ),
            "locality_integrity": (
                self.validate_locality_integrity()
            ),
            "duplicate_authorities": (
                self.detect_duplicate_authorities()
            ),
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "validation_metadata": (
                self.validation_metadata
            ),
        }
