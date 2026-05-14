# PECS-PRO

## IMPORTANT WARNING

PECS-PRO is experimental prototype software.
It is provided "AS IS" with no warranties or guarantees.

Do not use PECS-PRO directly on production, safety-critical, financial, medical, or security-sensitive systems.
Always use:
- isolated test workspaces
- cloned repositories
- version control
- backups
- human supervision

PECS may:
- misclassify locality
- infer incorrect continuity
- generate incomplete retrieval state
- produce unstable context bundles
- damage workspace assumptions

## Requirements

- Python 3.9
- `pip install -e .` from the package root to install in editable mode
- `watchdog` for live daemon monitoring

## What PECS-PRO v2 does

PECS-PRO v2 is a continuity stabilization system and topology-aware context builder.
It is designed to preserve:
- topology-local continuity
- object locality
- ownership continuity
- execution continuity

PECS-PRO does not replace LLM reasoning.
The LLM performs reasoning, inference, reconstruction, and ambiguity resolution.
PECS stabilizes continuity anchors so the LLM can reconstruct state reliably from compact workspace evidence.

PECS-PRO v2 is intentionally:
- deterministic
- topology-first
- low-token
- incremental
- non-invasive
- cache-only

PECS-PRO intentionally avoids:
- telemetry architectures
- tracing infrastructures
- vector databases
- semantic indexing
- orchestration layers
- runtime analytics

## What changed in v2 vs v1

### v1
- line-number continuity anchors like `file.py:42`
- file-based locality tokens
- heavier continuity payloads
- no persistent live daemon

### v2
- canonical symbolic anchors like `PECS_ID:viewer.overlay.sync`
- compact anchor-based locality storage
- topology-aware retrieval via `TopologyRetriever`
- incremental live daemon generating `.pecs/` artifacts
- low-token compact context export via `CompactContextBuilder`
- no AST-heavy reconstruction or large continuity payloads

## Minimal Continuity Algorithm

PECS minimal continuity works as a small stabilization loop:

1. Static topology extraction
- collect structural topology anchors and compact locality artifacts

2. Sparse runtime validation
- use sparse runtime activation evidence only to reinforce active topology paths

3. Locality heuristics
- track edit clusters, repeated locality, runtime-touched files, and continuity hotspots

4. Continuity snapshots
- compress architectural state into compact JSON and Markdown exports

5. LLM reconstruction
- the LLM performs synthesis, reasoning, and reconstruction from these compact continuity anchors

PECS does not perform the reasoning itself.

## Installation

### Recommended: Install PECS-PRO externally (no workspace contamination)

You can install PECS-PRO from GitHub or a release tarball/zip into a dedicated Python environment (system, user, or venv) OUTSIDE your development workspace.

#### Install from GitHub (latest main branch):

```bash
# In a dedicated location (not your dev workspace):
python3 -m venv ~/pecs-pro-venv
source ~/pecs-pro-venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install git+https://github.com/YOUR_ORG/PECS_PRO_V2_FINAL.git@main
# Or from a release tarball/zip:
# python3 -m pip install /path/to/PECS_PRO_V2_FINAL.zip

# Install watchdog (required for live daemon):
python3 -m pip install watchdog
```

#### Verify install:

```bash
pecs-pro-daemon --help
```

#### Launch the daemon for a target workspace (from anywhere):

```bash
# Example: monitor a workspace at /path/to/your/workspace
pecs-pro-daemon /path/to/your/workspace
```

This will create and update a disposable `.pecs/` directory inside the monitored workspace.

### Automatic workspace setup

If you want PECS to install the workspace integration files automatically, run:

```bash
pecs-pro-install-workspace "/path/to/your/workspace"
```

Or, from the source checkout:

```bash
/Users/raj/Downloads/PECS_PRO_V2_FINAL/pecs_pro/install_pecs_workspace.sh "/path/to/your/workspace"
```

This installs the following into the target workspace:

- `.vscode/tasks.json`
- `.vscode/settings.json` with `pecs.contextPath`
- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- `.github/copilot-instructions.md`
- `.pecs/tools/append_ai_chat_history.py`
- `.pecs/tools/update_ai_chat_history.sh`
- `.pecs/ai_chat_history.json`
- `.pecs/README_WORKSPACE_INTEGRATION.md`

The generated tasks include:

- `PECS: Start Daemon`
- `PECS: Auto Start Daemon On Folder Open`
- `PECS: Stop Daemon`
- `PECS: Append Chat Event`
- `PECS: Manual Update Chat History`

The installed task commands automatically run the workspace environment setup when present:

```bash
cd "${workspaceFolder}"
source .venv/bin/activate
```

---

### Sample install and launch script (external, safe)

Save as `install_and_run_pecs.sh`:

```bash
#!/bin/bash
set -e

# 1. Create a dedicated venv for PECS-PRO (outside your workspace)
VENV_DIR="$HOME/pecs-pro-venv"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python3 -m pip install --upgrade pip

# 2. Install PECS-PRO from GitHub
python3 -m pip install git+https://github.com/YOUR_ORG/PECS_PRO_V2_FINAL.git@main
python3 -m pip install watchdog

# 3. Launch the daemon for your workspace
pecs-pro-daemon "$1"
```

Usage:

```bash
chmod +x install_and_run_pecs.sh
./install_and_run_pecs.sh /path/to/your/workspace
```

### Manual setup guide

If you need to install PECS without the installer script, copy these files into the target workspace:

- `.continue/rules/PECS_CONTEXT_RULE.md`
- `.continue/rules/PECS_APPEND_RULE.md`
- `.github/copilot-instructions.md`
- `.pecs/tools/append_ai_chat_history.py`
- `.pecs/README_WORKSPACE_INTEGRATION.md`

Create these files if they do not exist:

- `.pecs/ai_chat_history.json` with `[]`
- `.vscode/tasks.json`
- `.vscode/settings.json`

Minimum manual commands:

```bash
cd "/path/to/your/workspace"
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install watchdog
```

Then install PECS itself from the package folder or GitHub source:

```bash
python3 -m pip install /path/to/PECS_PRO_V2_FINAL/pecs_pro
```

or:

```bash
python3 -m pip install git+https://github.com/YOUR_ORG/PECS_PRO_V2_FINAL.git@main
```

Then start the daemon:

```bash
pecs-pro-daemon "/path/to/your/workspace"
```

If you are running from source checkout instead of an installed package, use:

```bash
PECS_PRO_REPO="/Users/raj/Downloads/PECS_PRO_V2_FINAL/pecs_pro" \
	/Users/raj/Downloads/PECS_PRO_V2_FINAL/pecs_pro/launch_pecs_daemon.sh "/path/to/your/workspace"
```

---

## Running the daemon

To start the live continuity daemon for a workspace (from anywhere):

```bash
pecs-pro-daemon /path/to/your/workspace
```

Or, if running directly from source (not recommended for production):

```bash
python3 /path/to/PECS_PRO_V2_FINAL/pecs_pro/run_pecs_daemon.py /path/to/your/workspace
```

The daemon creates and updates a disposable `.pecs/` directory inside the monitored workspace.

## Notes

- Installing the package does not automatically start the daemon.
- The daemon must be running for `.pecs/` artifacts to be generated.
- `.pecs/` is cache-only and disposable.
- Do not edit `.pecs/` manually.

## Recommended workflow

1. Install PECS-PRO in editable mode.
2. Start the daemon before editing the target workspace.
3. Make sure `.pecs/` is present and being updated.
4. Periodically export continuity state from `.pecs/` into compact continuity snapshots.
5. Consume `.pecs/` JSON exports from tooling or integrations.

New projects benefit from early continuity initialization so topology anchors and continuity snapshots exist before sessions become fragmented.

## Disclaimer

PECS-PRO is not an autonomous AI project manager.
It is a continuity infrastructure layer only.
Use it to support human-directed workflows, not to replace them.
