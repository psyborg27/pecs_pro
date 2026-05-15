from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

    if isinstance(data, dict):
        return data

    return default


def _merge_tasks(tasks_path: Path, repo_root: Path) -> None:
    base = _read_json(tasks_path, {"version": "2.0.0", "tasks": [], "inputs": []})
    tasks: List[Dict[str, Any]] = (
        base.get("tasks", []) if isinstance(base.get("tasks"), list) else []
    )
    inputs: List[Dict[str, Any]] = (
        base.get("inputs", []) if isinstance(base.get("inputs"), list) else []
    )

    launcher = str((repo_root / "launch_pecs_daemon.sh").resolve())

    start_task = {
        "label": "PECS: Start Daemon",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            "&& if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi "
            f'&& PECS_PRO_REPO="{repo_root}" "{launcher}" "${{workspaceFolder}}"\''
        ),
        "isBackground": True,
        "problemMatcher": [],
    }

    auto_start_task = {
        "label": "PECS: Auto Start Daemon On Folder Open",
        "type": "shell",
        "command": start_task["command"],
        "isBackground": True,
        "problemMatcher": [],
        "runOptions": {"runOn": "folderOpen"},
    }

    stop_task = {
        "label": "PECS: Stop Daemon",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            "&& if [[ -f .pecs/daemon.pid ]]; then "
            "pid=$(<.pecs/daemon.pid); "
            'if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then kill "$pid"; fi; '
            "fi'"
        ),
    }

    append_task = {
        "label": "PECS: Append Chat Event",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            "&& if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi "
            '&& python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" '
            '--source "${input:pecsChatSource}" --message "${input:pecsChatMessage}"\''
        ),
    }

    manual_update_task = {
        "label": "PECS: Manual Update Chat History",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            "&& if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi "
            '&& bash .pecs/tools/update_ai_chat_history.sh "${workspaceFolder}" "${input:pecsChatSource}" "${input:pecsChatMessage}"\''
        ),
    }

    refresh_continuity_task = {
        "label": "PECS: Refresh Continuity State",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            "&& if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi "
            '&& python3 .pecs/bridge/run_bridge.py refresh --workspace "${workspaceFolder}"\''
        ),
    }

    validate_continuity_task = {
        "label": "PECS: Validate Continuity State",
        "type": "shell",
        "command": (
            'bash -lc \'cd "${workspaceFolder}" '
            "&& if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi "
            '&& python3 .pecs/bridge/run_bridge.py validate --workspace "${workspaceFolder}"\''
        ),
    }

    desired_tasks = [
        start_task,
        auto_start_task,
        stop_task,
        append_task,
        manual_update_task,
        refresh_continuity_task,
        validate_continuity_task,
    ]

    existing_by_label = {
        task.get("label"): task
        for task in tasks
        if isinstance(task, dict) and task.get("label")
    }
    for task in desired_tasks:
        existing_by_label[task["label"]] = task

    merged_tasks = list(existing_by_label.values())

    desired_inputs = [
        {
            "id": "pecsChatSource",
            "type": "promptString",
            "description": "Chat source (copilot or continue)",
            "default": "copilot",
        },
        {
            "id": "pecsChatMessage",
            "type": "promptString",
            "description": "Message/event text",
            "default": "manual append",
        },
    ]

    existing_inputs = {
        item.get("id"): item
        for item in inputs
        if isinstance(item, dict) and item.get("id")
    }
    for item in desired_inputs:
        existing_inputs[item["id"]] = item

    base["version"] = "2.0.0"
    base["tasks"] = merged_tasks
    base["inputs"] = list(existing_inputs.values())

    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    tasks_path.write_text(
        json.dumps(base, indent=2, ensure_ascii=True), encoding="utf-8"
    )


def _merge_json_dict(path: Path, updates: Dict[str, Any]) -> None:
    current = _read_json(path, {})
    current.update(updates)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, indent=2, ensure_ascii=True), encoding="utf-8")


def _write_continue_rules(workspace_root: Path) -> None:
    rules_dir = workspace_root / ".continue" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    pecs_context_rule = """# PECS-PRO Authority & PECS-LITE Projection Rule

PECS artifacts are generated continuity infrastructure only.
They do NOT contain editable sourcecode.

## Authority Model

PECS-PRO owns:
- runtime topology
- execution continuity
- workspace state truth

PECS-LITE projects:
- compact runtime locality
- execution neighborhood
- model-adapted guidance

## Before Proposing Edits

Read and respect:
- .pecs/active_context.json (PECS-PRO runtime context)
- .pecs/locality_index.json (PECS-PRO locality weighting)
- .pecs/active_topology.json (PECS-PRO topology authority)

Priority order:
1. Live workspace runtime modules (always authoritative)
2. PECS-PRO continuity artifacts (.pecs/ infrastructure)
3. PECS-LITE projections (ephemeral locality guidance)
4. Structured accepted engineering continuity chains

## Rules

- Never edit or patch .pecs/ files
- Use PECS for locality retrieval only
- Target runtime workspace modules for edits
- Respect execution neighborhood hints from PECS-LITE
- Query PECS-LITE for runtime target projection, not PECS-PRO directly
- Treat continuity guidance as probabilistic (confidence-aware), not deterministic
- Do not use raw chat narrative as engineering locality authority

## Environment

Always run workspace commands with environment activation:
```
cd \"${workspaceFolder}\"
if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi
```

## PECS-LITE Projection Profiles

PECS-LITE adapts its locality guidance based on model constraints.
Profile selection is MIDDLEWARE responsibility, not PECS inference.

### Profile Selection Guidance

**Small Models (Qwen/DeepSeek 16k-32k):**
- Use `projection_profile: small` (default for Continue)
- Receives: 1-3 primary targets, 1-2 secondary candidates
- Focus: aggressive execution-locality narrowing
- Token efficiency: ~850-1500 tokens

**Medium Models (32k-100k context):**
- Use `projection_profile: medium` if default insufficient
- Receives: 3-6 primary targets, nearby execution adjacency
- Focus: balanced locality + execution relationships
- Token efficiency: ~2000-3000 tokens

**Large Models (100k+, GPT-5/Claude-class):**
- Use `projection_profile: large` if high context available
- Receives: broader targets + structured continuity enrichment
- Focus: execution-locality relationships + bounded richness
- Token efficiency: ~4000-8000 tokens

### Important

- CONTINUE DOES NOT INFER MODEL CAPABILITY
- Profile selection is your responsibility based on actual model
- If unsure, use `projection_profile: small` (safest default)

## Engineering Continuity Principle

PECS preserves accepted engineering continuity, not raw conversational history.

Use structured continuity chains:
- issue -> accepted_locality -> outcome
- rejected_locality for downranking failed chains
- continuity_confidence for probabilistic locality guidance

Do NOT treat raw chat transcripts as continuity authority.
Accepted engineering locality is higher signal than conversational narrative.
"""

    pecs_append_rule = """# PECS Chat History Append Rule

For each significant Continue conversation turn, append an event to:
.pecs/ai_chat_history.json

This helps PECS-PRO track execution context over time.

Preferred command:
```
python3 .pecs/tools/append_ai_chat_history.py \"${workspaceFolder}\" \\
  --source continue --message \"<summary>\"
```

If Continue automation can emit structured JSON:
```
python3 .pecs/tools/append_ai_chat_history.py \"${workspaceFolder}\" \\
  --payload-json '<json-object>'
```
"""

    (rules_dir / "PECS_CONTEXT_RULE.md").write_text(pecs_context_rule, encoding="utf-8")
    (rules_dir / "PECS_APPEND_RULE.md").write_text(pecs_append_rule, encoding="utf-8")


def _write_copilot_instructions(workspace_root: Path) -> None:
    github_dir = workspace_root / ".github"
    github_dir.mkdir(parents=True, exist_ok=True)

    content = """# Copilot Workspace Instructions — PECS v2 Architecture

PECS artifacts are generated continuity infrastructure only.
They do NOT contain editable engineering sourcecode.

## Authority Model

PECS-PRO owns and maintains:
- runtime topology reconstruction
- execution graph continuity
- workspace state truth
- continuity persistence

PECS-LITE is a stateless projection layer:
- queries PECS-PRO
- returns compact locality guidance
- never owns topology or state
- never runs as independent daemon

## Before Suggesting Edits

Inspect these authoritative files when present:
- .pecs/active_context.json (PECS-PRO context)
- .pecs/locality_index.json (PECS-PRO locality)
- .pecs/active_topology.json (PECS-PRO topology)
- .continue/rules/CONTINUITY_MAP.md (if present)

Copilot guidance:
1. Live workspace runtime modules are authoritative and editable
2. Use .pecs artifacts ONLY to narrow locality and identify runtime targets
3. Never edit .pecs files or treat them as sourcecode
4. Query PECS-LITE for runtime target projection
5. Respect execution neighborhood and continuity hints
6. Trust PECS-PRO topology over ad-hoc repository search

## Editing Rules

- Target only live workspace runtime modules for changes
- Use PECS-LITE locality guidance to narrow search scope
- Do NOT edit .pecs infrastructure files
- Do NOT treat PECS artifacts as authoritative sourcecode
- When in doubt, rely on PECS-PRO continuity authority
- Use accepted engineering continuity chains to continue prior accepted locality
- Downrank repeatedly rejected locality before proposing edits

## Environment

When running workspace commands, prefer:
```
cd \"${workspaceFolder}\"
if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi
```

For chat continuity tracking:
```
python3 .pecs/tools/append_ai_chat_history.py \"${workspaceFolder}\" \\
  --source copilot --message \"<summary>\"
```

## PECS-LITE Adaptive Projection Profiles

PECS-LITE adapts locality projection richness based on model constraints.
Projection profile selection belongs to middleware/client integrations, NOT PECS.

### Profile Selection for Copilot

**Default Profile: MEDIUM**
- Suitable for Claude/GPT-4 class reasoning models
- Default: `projection_profile: medium` unless overridden
- Receives: 3-6 primary targets, execution adjacency hints
- Token efficiency: ~2000-3000 tokens

**For Small Models (if using local/constrained models):**
- Override: `projection_profile: small`
- Receives: 1-3 primary targets, 1-2 secondary candidates
- Focus: extreme execution-locality precision
- Token efficiency: ~850-1500 tokens

**For Very Large Models:**
- Override: `projection_profile: large`
- Receives: fuller execution-locality relationships + bounded richness
- Focus: structured continuity exploration
- Token efficiency: ~4000-8000 tokens

### Important

- COPILOT DOES NOT INFER MODEL CAPABILITY
- Profile selection is YOUR responsibility
- Default (medium) is conservative and well-tested
- Always verify projected targets make sense for your edit scope
- When uncertain, use profile: medium

## Engineering Continuity Principle

PECS preserves structured accepted engineering continuity only:
- accepted locality
- rejected locality chains
- continuity confidence
- unresolved engineering locality tensions

PECS does NOT preserve raw conversational transcripts as projection context.
Use confidence-aware continuity signals as probabilistic guidance.

## Important

- This file is guidance for PECS integration, not authoritative sourcecode
- PECS improves locality certainty but does not replace reasoning
- Always verify changes against actual runtime behavior
- Test before committing
"""

    (github_dir / "copilot-instructions.md").write_text(content, encoding="utf-8")


def _install_chat_tools(workspace_root: Path, repo_root: Path) -> None:
    tools_dir = workspace_root / ".pecs" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)

    source_script = repo_root / "append_ai_chat_history.py"
    target_script = tools_dir / "append_ai_chat_history.py"
    target_script.write_text(
        source_script.read_text(encoding="utf-8"), encoding="utf-8"
    )

    manual_source_script = repo_root / "update_ai_chat_history.sh"
    manual_target_script = tools_dir / "update_ai_chat_history.sh"
    if manual_source_script.exists():
        manual_target_script.write_text(
            manual_source_script.read_text(encoding="utf-8"), encoding="utf-8"
        )

    chat_history = workspace_root / ".pecs" / "ai_chat_history.json"
    if not chat_history.exists():
        chat_history.write_text("[]\n", encoding="utf-8")


def _install_bridge_runtime(workspace_root: Path, repo_root: Path) -> None:
    bridge_dir = workspace_root / ".pecs" / "bridge"
    config_dir = workspace_root / ".pecs" / "config"
    runtime_dir = workspace_root / ".pecs" / "runtime"
    continuity_dir = workspace_root / ".pecs" / "continuity"

    bridge_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    continuity_dir.mkdir(parents=True, exist_ok=True)

    (runtime_dir / ".gitkeep").write_text("", encoding="utf-8")

    export_source = repo_root / "scripts" / "export_workspace_continuity.py"
    validate_source = repo_root / "scripts" / "validate_workspace_continuity.py"

    (bridge_dir / "export_workspace_continuity.py").write_text(
        export_source.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (bridge_dir / "validate_workspace_continuity.py").write_text(
        validate_source.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    bridge_runner = """from __future__ import annotations

import argparse
import json
from pathlib import Path

from export_workspace_continuity import export_workspace_continuity
from validate_workspace_continuity import validate_workspace_continuity


def main() -> None:
    parser = argparse.ArgumentParser(
        description=\"Workspace-local PECS deterministic continuity bridge\"
    )
    parser.add_argument(
        \"command\",
        choices=[\"refresh\", \"validate\"],
        help=\"Bridge command to run\",
    )
    parser.add_argument(
        \"workspace_root\",
        nargs=\"?\",
        default=None,
        help=\"Workspace root path (default: current directory).\",
    )
    parser.add_argument(
        \"--workspace\",
        dest=\"workspace_flag\",
        default=None,
        help=\"Workspace root path.\",
    )
    args = parser.parse_args()

    workspace_value = args.workspace_flag or args.workspace_root or \".\"
    workspace_root = Path(workspace_value).resolve()

    if args.command == \"refresh\":
        result = export_workspace_continuity(workspace_root)
    else:
        result = validate_workspace_continuity(workspace_root)

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == \"__main__\":
    main()
"""
    (bridge_dir / "run_bridge.py").write_text(bridge_runner, encoding="utf-8")

    bridge_sh = """#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="${1:-.}"
COMMAND="${2:-refresh}"

cd "$WORKSPACE_ROOT"
if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
fi

python3 .pecs/bridge/run_bridge.py "$COMMAND" --workspace "$WORKSPACE_ROOT"
"""
    (bridge_dir / "run_bridge.sh").write_text(bridge_sh, encoding="utf-8")

    bridge_config = {
        "schema": "pecs.bridge.config.v1",
        "mode": "deterministic_continuity_stabilization",
        "compare_before_write": True,
        "omit_empty_sections": True,
        "sparse_output": True,
    }
    (config_dir / "continuity_bridge.json").write_text(
        json.dumps(bridge_config, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    continuity_scaffold = {
        "active_topology.json": {
            "schema": "pecs.active_topology.v1",
            "active_topology_zone": "general_runtime",
            "active_runtime_zones": [],
            "runtime_validation": {
                "runtime_evidence_count": 0,
                "runtime_confirmations": 0,
                "active_topology_targeting": 0.0,
                "runtime_confirmation_density": 0.0,
            },
            "validation_metrics": {
                "edit_locality_improvement": 0.0,
                "active_topology_targeting": 0.0,
                "continuity_hotspot_identification": 0.0,
                "runtime_confirmation_density": 0.0,
                "continuity_compression_effectiveness": 0.0,
            },
            "workspace_trajectory": "general_runtime",
        },
        "locality_state.json": {
            "schema": "pecs.locality_state.v1",
            "validation_metrics": {
                "edit_locality_improvement": 0.0,
                "active_topology_targeting": 0.0,
                "continuity_hotspot_identification": 0.0,
                "runtime_confirmation_density": 0.0,
                "continuity_compression_effectiveness": 0.0,
            },
        },
        "engineering_continuity_state.json": {
            "schema": "pecs.engineering_continuity.v1",
            "active_engineering_chains": [],
            "updated_at": "",
        },
    }

    for file_name, payload in continuity_scaffold.items():
        path = continuity_dir / file_name
        if not path.exists():
            path.write_text(
                json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
            )

    markdown_scaffold = {
        "architectural_decisions.md": "# Architectural Decisions\n",
        "current_workspace_focus.md": "# Current Workspace Focus\n",
        "unresolved_tensions.md": "# Unresolved Tensions\n",
    }
    for file_name, content in markdown_scaffold.items():
        path = continuity_dir / file_name
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def _write_readme(workspace_root: Path) -> None:
    readme = workspace_root / ".pecs" / "README_WORKSPACE_INTEGRATION.md"
    content = """# PECS Workspace Integration

This workspace was configured by PECS workspace installer.

PECS artifacts are generated continuity infrastructure only.
Do NOT edit or patch .pecs files.
PECS does not contain engineering sourcecode.
Runtime workspace modules are the authoritative implementation.

Installed items:
- .vscode/tasks.json (PECS tasks, including folder-open auto-start)
- .vscode/settings.json with pecs.contextPath
- .continue/rules/PECS_CONTEXT_RULE.md
- .continue/rules/PECS_APPEND_RULE.md
- .github/copilot-instructions.md
- .pecs/tools/append_ai_chat_history.py
- .pecs/ai_chat_history.json
- .pecs/bridge/run_bridge.py
- .pecs/bridge/export_workspace_continuity.py
- .pecs/bridge/validate_workspace_continuity.py
- .pecs/config/continuity_bridge.json
- .pecs/continuity/engineering_continuity_state.json
- .pecs/README_MANUAL_SETUP.md

PECS v2 Process Flow:
1. Install workspace assets to configure VS Code, Continue, Copilot, and .pecs infrastructure.
2. Start or auto-start the workspace daemon to generate `.pecs/` continuity artifacts from runtime workspace modules.
3. PECS-PRO writes deterministic continuity outputs such as active context and locality index.
4. PECS-LITE reads those outputs and returns runtime target projections to the AI model.
5. The model uses runtime workspace modules for edits; `.pecs` files remain infrastructure only.
6. Accepted engineering continuity chains preserve high-signal issue-locality-outcome guidance.

Key rules:
- Workspace runtime modules are authoritative.
- `.pecs` files are not sourcecode.
- Use `.pecs` only to identify locality and execution neighborhood.
- Do not edit or patch `.pecs` artifacts.
- Do not use raw chat narratives as locality authority.
- Use structured accepted/rejected locality continuity with confidence.

Run manually:
- Task: PECS: Start Daemon
- Task: PECS: Stop Daemon
- Task: PECS: Refresh Continuity State
- Task: PECS: Validate Continuity State

Notes:
- Auto-start task may require VS Code confirmation for automatic tasks.
- Continue/Copilot integration is configured to use PECS locality projection and runtime targets.
- PECS-LITE is stateless and query-driven. It does not scan the workspace.
"""
    # PECS Workspace Integration\n\nThis workspace was configured by PECS workspace installer.\n\nPECS artifacts are generated continuity infrastructure only.\nDo NOT edit or patch .pecs files.\nPECS does not contain engineering sourcecode.\nRuntime workspace modules are the authoritative implementation.\n\nInstalled items:\n- .vscode/tasks.json (PECS tasks, including folder-open auto-start)\n- .vscode/settings.json with pecs.contextPath\n- .continue/rules/PECS_CONTEXT_RULE.md\n- .continue/rules/PECS_APPEND_RULE.md\n- .github/copilot-instructions.md\n- .pecs/tools/append_ai_chat_history.py\n- .pecs/ai_chat_history.json\n- .pecs/bridge/run_bridge.py\n- .pecs/bridge/export_workspace_continuity.py\n- .pecs/bridge/validate_workspace_continuity.py\n- .pecs/config/continuity_bridge.json\n- .pecs/README_MANUAL_SETUP.md\n\nRun manually:\n- Task: PECS: Start Daemon\n- Task: PECS: Stop Daemon\n- Task: PECS: Refresh Continuity State\n- Task: PECS: Validate Continuity State\n\nNotes:\n- Auto-start task may require VS Code confirmation for automatic tasks.\n- Continue/Copilot integration is configured to use PECS locality projection and runtime targets.\n- PECS artifacts are infrastructure only; do not treat them as source.\n"""
    readme.parent.mkdir(parents=True, exist_ok=True)
    readme.write_text(content, encoding="utf-8")


def _copy_manual_setup_guide(workspace_root: Path, repo_root: Path) -> None:
    source = repo_root / "README_MANUAL_SETUP.md"
    target = workspace_root / ".pecs" / "README_MANUAL_SETUP.md"
    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def install_workspace(workspace_root: Path, repo_root: Path) -> None:
    _install_chat_tools(workspace_root, repo_root)
    _install_bridge_runtime(workspace_root, repo_root)
    _merge_tasks(workspace_root / ".vscode" / "tasks.json", repo_root)
    _merge_json_dict(
        workspace_root / ".vscode" / "settings.json",
        {
            "pecs.contextPath": str(
                (workspace_root / ".pecs" / "active_context.json").resolve()
            ),
        },
    )
    _write_continue_rules(workspace_root)
    _write_copilot_instructions(workspace_root)
    _copy_manual_setup_guide(workspace_root, repo_root)
    _write_readme(workspace_root)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install PECS VS Code/Continue/Copilot integration files into a workspace"
    )
    parser.add_argument("workspace_root", help="Target workspace root path")
    parser.add_argument(
        "--repo-root",
        default="",
        help="PECS repository root (defaults to this script's directory)",
    )
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Preserve existing user configuration during upgrade",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify installation without installing",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        logger.error(f"Workspace does not exist: {workspace_root}")
        sys.exit(1)

    try:
        logger.info(f"PECS workspace integration installer started")
        logger.info(f"Workspace: {workspace_root}")
        logger.info(f"PECS repository: {repo_root}")

        # Try to use manifest-based manager if available
        try:
            from .workspace_assets_manager import WorkspaceAssetsManager

            logger.info("Using manifest-based workspace assets manager")
            manager = WorkspaceAssetsManager(repo_root, workspace_root)

            if args.verify_only:
                logger.info("Running verification only (no changes)")
                result = manager.verify_installation()
                print(json.dumps(result, indent=2))
                sys.exit(0 if result["valid"] else 1)

            # Install assets
            install_result = manager.install_assets(upgrade=args.upgrade, verify=True)
            logger.info(f"Asset installation status: {install_result['status']}")
            logger.info(f"Installed {len(install_result['installed_assets'])} asset(s)")

            if install_result.get("errors"):
                logger.warning(f"Installation warnings: {install_result['errors']}")

        except ImportError:
            logger.warning(
                "Manifest-based manager not available, using legacy installer"
            )

        # Always run legacy installer as fallback/supplementary
        logger.info("Installing workspace integration (legacy flow)")
        install_workspace(workspace_root, repo_root)
        logger.info("Legacy installation completed")

        logger.info(
            f"PECS workspace integration successfully installed at: {workspace_root}"
        )
        print(
            f"Installation complete. Run 'pecs verify-workspace {workspace_root}' to verify."
        )

    except Exception as e:
        logger.error(f"Installation failed: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()
