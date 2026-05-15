# PECS Manual Setup Guide

This guide is for users who want to install PECS into a workspace without using the auto-installer script.

## Experimental status

PECS is experimental and currently in an early proof-of-concept stage.
It has been developed through AI-assisted and agentic coding workflows,
primarily by a non-traditional software developer.

Validate all outputs manually.
Do not use on production or commercially critical systems.
Use backups, version control, and human supervision.
PECS does not replace engineering judgment.

## Supported AI tooling

PECS is currently designed and tested primarily for:

- GitHub Copilot Chat
- Continue

Other VS Code AI extensions may not preserve compatible continuity/workflow behavior.
PECS does not claim universal compatibility.

## What to copy into the workspace

Copy these files from the PECS package folder into the target workspace:

- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- `.github/copilot-instructions.md`
- `.pecs/tools/append_ai_chat_history.py`
- `.pecs/tools/update_ai_chat_history.sh`
- `.pecs/README_WORKSPACE_INTEGRATION.md`

**Important:** `.pecs` artifacts are generated continuity infrastructure only. Do not edit `.pecs` files as if they were engineering sourcecode. Use them only to locate runtime workspace targets and verify locality.

Create these files if they do not already exist:

- `.pecs/ai_chat_history.json` with an initial value of `[]` (optional)
- `.vscode/tasks.json`
- `.vscode/settings.json`

## Environment setup commands

Run these in the target workspace:

```bash
cd "/path/to/your/workspace"
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install watchdog
```

Then install PECS itself:

```bash
python3 -m pip install git+https://github.com/YOUR_ORG/PECS_PRO_V2_FINAL.git@main
```

Or from a local source checkout:

```bash
python3 -m pip install /path/to/PECS_PRO_V2_FINAL/pecs_pro
```

## Configure VS Code

The auto-installer normally writes these for you, but manually you should ensure:

- `.vscode/tasks.json` contains PECS start/stop/chat append tasks
- `.vscode/tasks.json` contains `PECS: Manual Update Chat History`
- `.vscode/settings.json` includes `pecs.contextPath` pointing to `.pecs/active_context.json`
- Workspace settings are saved in the target workspace, not in the PECS package folder

After setup, open tasks using:

- VSCode
- Terminal
- Run Task
- select a PECS task

Expected task names include:

- `PECS: Start Daemon`
- `PECS: Stop Daemon`
- `PECS: Refresh Continuity State`
- `PECS: Validate Continuity State`

## Configure Continue

Continue reads rules from `.continue/rules/`.
Make sure these are present:

- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- Keep `.continue/rules/CONTINUITY_MAP.md` in the workspace if you already use it

## Configure Copilot

Copilot reads workspace instructions from:

- `.github/copilot-instructions.md`

Keep the instructions focused on reading `.pecs` artifacts before edits.

## Start the daemon

After installation and workspace setup, start the daemon:

```bash
pecs-pro-daemon "/path/to/your/workspace"
```

If you are starting from the source checkout directly:

```bash
PECS_PRO_REPO="/Users/raj/Downloads/PECS_PRO_V2_FINAL/pecs_pro" \
  /Users/raj/Downloads/PECS_PRO_V2_FINAL/pecs_pro/launch_pecs_daemon.sh "/path/to/your/workspace"
```

The daemon is intentionally manual-start during active AI-assisted development sessions.
It does not auto-start from package installation.
After stabilization, no-op cycles are intentionally mostly silent
(no rewrites, no log spam, no continuity churn).

## Bridge lifecycle

Users normally do not run bridge scripts directly.
Use standard refresh flow (`pecs-pro refresh` or `PECS: Refresh Continuity State`).
The bridge remains lightweight, deterministic, and non-semantic.

## New AI session handoff

For a new AI session, provide:

- current task/problem
- `.pecs` continuity state

Prefer this over large historical chat dumps.
Chat-history replay is optional and experimental.

## What automatic installation does

If you use `pecs-pro-install-workspace`, it installs all of the above for you and also creates the PECS tasks in `.vscode/tasks.json`.
