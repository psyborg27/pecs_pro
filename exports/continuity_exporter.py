from __future__ import annotations

import json

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class ContinuityExporter:
    """
    Deterministic continuity export authority.

    Serializes:
    - continuity locality
    - topology-local reconstruction
    - execution-local continuity

    Exports are derived artifacts only.

    They NEVER mutate runtime truth.
    """

    def export_json(
        self,
        export_data: Dict[str, object],
        output_path: Path,
    ) -> None:
        output_path.write_text(
            json.dumps(
                export_data,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
