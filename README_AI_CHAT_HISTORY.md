# PECS Workspace Automation (Copilot + Continue)

## One-command setup

Run this once per workspace:

```bash
/Users/raj/Downloads/PECS_PRO_V2_FINAL/pecs_pro/install_pecs_workspace.sh "/path/to/workspace"
```

Or, if installed via pip:

```bash
pecs-pro-install-workspace "/path/to/workspace"
```

## What gets installed automatically

- `.vscode/tasks.json`
	- `PECS: Start Daemon`
	- `PECS: Auto Start Daemon On Folder Open`
	- `PECS: Stop Daemon`
	- `PECS: Append Chat Event`
- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- `.github/copilot-instructions.md`
- `.pecs/tools/append_ai_chat_history.py`
- `.pecs/tools/update_ai_chat_history.sh`
- `.pecs/ai_chat_history.json`

## Environment command behavior

Installed tasks and scripts run this when present:

```bash
cd "${workspaceFolder}"
source .venv/bin/activate
```

So workspace-local Python dependencies are used automatically.

## Chat append usage

Manual append (works now):

```bash
python3 .pecs/tools/append_ai_chat_history.py "/path/to/workspace" --source copilot --message "session started"
```

Manual shell updater:

```bash
bash .pecs/tools/update_ai_chat_history.sh "/path/to/workspace" copilot "session started"
```

Structured payload append:

```bash
python3 .pecs/tools/append_ai_chat_history.py "/path/to/workspace" --payload-json '{"source":"continue","messages":[{"role":"user","content":"..."}]}'
```

## Important limitation

Neither Copilot Chat nor Continue currently exposes a universal built-in "append every turn to file" switch in this repository by default.

What is now automated:
- rules/instructions are installed so agents use `.pecs`
- VS Code tasks are installed so daemon startup and manual appends are one-click
- the manual updater script is copied into `.pecs/tools/`
- `.pecs/ai_chat_history.json` watcher is active in daemon

If your Continue or custom tooling supports post-message hooks, point the hook to:

```bash
python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" --payload-json '<json-object>'
```
