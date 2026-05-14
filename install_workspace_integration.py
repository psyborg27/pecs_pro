from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


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

    pecs_context_rule = """# PECS CONTEXT RULE\n\nBefore proposing edits, read and respect: \n- .pecs/active_context.json\n- .pecs/compact_bundle.json\n- .pecs/session_context.json\n- .pecs/locality_index.json\n- .continue/rules/CONTINUITY_MAP.md (if present)\n\nPriority order:\n1. Live workspace files\n2. .pecs runtime artifacts\n3. Historical chat memory\n\nDo not treat chat history as architectural authority.\nUse it as continuity telemetry only.\n\nAlways run workspace commands with environment activation when available:\ncd \"${workspaceFolder}\"\nsource .venv/bin/activate\n"""

    pecs_append_rule = """# PECS CHAT APPEND RULE\n\nFor each new Continue conversation or significant turn, append an event to:\n.pecs/ai_chat_history.json\n\nPreferred command:\npython3 .pecs/tools/append_ai_chat_history.py \"${workspaceFolder}\" --source continue --message \"<summary>\"\n\nIf your Continue automation can emit a structured JSON payload, use:\npython3 .pecs/tools/append_ai_chat_history.py \"${workspaceFolder}\" --payload-json '<json-object>'\n"""

    (rules_dir / "PECS_CONTEXT_RULE.md").write_text(pecs_context_rule, encoding="utf-8")
    (rules_dir / "PECS_APPEND_RULE.md").write_text(pecs_append_rule, encoding="utf-8")


def _write_copilot_instructions(workspace_root: Path) -> None:
    github_dir = workspace_root / ".github"
    github_dir.mkdir(parents=True, exist_ok=True)

    content = """# Copilot Workspace Instructions (PECS)\n\nBefore suggesting or applying edits, inspect these files when present:\n- .pecs/active_context.json\n- .pecs/compact_bundle.json\n- .pecs/session_context.json\n- .pecs/locality_index.json\n- .continue/rules/CONTINUITY_MAP.md\n\nUse .pecs as a continuity aid, not as absolute source of truth.\nLive code wiring in the workspace is authoritative.\n\nWhen running workspace commands, prefer:\ncd \"${workspaceFolder}\"\nsource .venv/bin/activate\n\nFor chat continuity append events:\npython3 .pecs/tools/append_ai_chat_history.py \"${workspaceFolder}\" --source copilot --message \"<summary>\"\n"""

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
    content = """# PECS Workspace Integration\n\nThis workspace was configured by PECS workspace installer.\n\nInstalled items:\n- .vscode/tasks.json (PECS tasks, including folder-open auto-start)\n- .vscode/settings.json with pecs.contextPath\n- .continue/rules/PECS_CONTEXT_RULE.md\n- .continue/rules/PECS_APPEND_RULE.md\n- .github/copilot-instructions.md\n- .pecs/tools/append_ai_chat_history.py\n- .pecs/ai_chat_history.json\n- .pecs/bridge/run_bridge.py\n- .pecs/bridge/export_workspace_continuity.py\n- .pecs/bridge/validate_workspace_continuity.py\n- .pecs/config/continuity_bridge.json\n- .pecs/README_MANUAL_SETUP.md\n\nRun manually:\n- Task: PECS: Start Daemon\n- Task: PECS: Stop Daemon\n- Task: PECS: Refresh Continuity State\n- Task: PECS: Validate Continuity State\n\nNotes:\n- Auto-start task may require VS Code confirmation for automatic tasks.\n- Extension-level automatic chat append depends on each extension's hook/event support.\n"""
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
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )

    if not workspace_root.exists():
        raise FileNotFoundError(f"Workspace does not exist: {workspace_root}")

    install_workspace(workspace_root, repo_root)
    print(f"PECS workspace integration installed at: {workspace_root}")


if __name__ == "__main__":
    main()
