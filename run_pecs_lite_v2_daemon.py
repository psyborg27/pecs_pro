"""
DEPRECATED — PECS-LITE DAEMON REMOVED.

PECS-LITE is now STATELESS and QUERY-DRIVEN ONLY.

Per the final architectural refactor (May 2026):
- PECS-PRO is the ONLY persistent continuity daemon.
- PECS-LITE is invocation-driven, not daemon-driven.
- PECS-LITE queries PECS-PRO and projects locality.

This file is kept as a historical reference only.
Do not use or invoke this module.

For workspace continuity management, use:
- launch_pecs_daemon.sh (PECS-PRO daemon)
- workspace_bridge_cli.py refresh (one-shot continuity update)
- run_pecs_pro.py (PECS-PRO main interface)

If you need PECS-LITE projection:
- Use: PECS_LITE v2/pecs_lite v2/runtime/run_lite.py
- This invokes the stateless projection on demand.

For workspace continuity daemon operations:
- pecs daemon start <workspace>
- pecs daemon stop <workspace>
- pecs daemon status

PECS-LITE will NEVER again:
- run as a persistent daemon
- maintain its own continuity state
- reconstruct topology independently
- own runtime authority
- scan workspace for continuity discovery
"""

import sys

print(__doc__, file=sys.stderr)
sys.exit(1)
