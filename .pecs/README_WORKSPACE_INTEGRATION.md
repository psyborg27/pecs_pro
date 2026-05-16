# PECS Workspace Integration

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
- .pecs/config/install_root.json
- .pecs/config/continuity_bridge.json
- .pecs/run_pecs.sh
- .pecs/run_pecs.cmd
- .pecs/run_pecs_daemon.sh
- .pecs/run_pecs_daemon.cmd
- .pecs/continuity/engineering_continuity_state.json
- .pecs/continuity/continuity_hydration_report.json
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
