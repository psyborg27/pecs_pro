# PECS-PRO

## IMPORTANT WARNING

PECS-PRO is experimental prototype software.
PECS-PRO is in an early proof-of-concept stage.

This project has been developed through AI-assisted and agentic coding workflows,
primarily by a non-traditional software developer.

All outputs require manual engineering validation.
Do not use PECS-PRO on production or commercially critical systems.
Use backups, version control, and human supervision for all usage.
PECS does not replace engineering judgment.

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

PECS stabilizes continuity for AI-assisted development.
The LLM performs reasoning.
PECS preserves deterministic continuity anchors.

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

## Architecture Separation

PECS keeps a strict separation between engine and workspace state:

- PECS engine (this repository):
	exporters, validators, normalization logic, topology tooling, runtime reinforcement, bridge installers/templates.
- Workspace continuity state (inside target workspace):
	`.pecs/` artifacts, continuity snapshots, runtime evidence, and bridge runtime/config.

This separation keeps PECS small, deterministic, and maintainable.

## Context Bridge

The workspace-local context bridge exists only to:

- normalize continuity inputs deterministically
- compare-before-write
- suppress no-op rewrites
- persist stable continuity anchors

The bridge does not:

- act as conversational authority
- perform semantic summarization
- orchestrate AI decisions
- replace LLM reasoning

## Supported AI Tooling

PECS is currently designed and tested primarily for:

- GitHub Copilot Chat
- Continue

Compatibility note:
- Other VS Code AI extensions may not preserve compatible continuity/workflow behavior.
- PECS does not claim universal compatibility across all AI extensions.

PECS continuity is built around deterministic workspace state,
topology continuity, locality stabilization, and sparse runtime reinforcement.
It is not a full conversational replay system.

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

### Deterministic install and workspace initialization

Use this flow for a new workspace user.

#### macOS/Linux

```bash
python3 -m pip install pecs-pro
pecs-pro init "/path/to/workspace"
```

#### Windows (PowerShell)

```powershell
py -m pip install pecs-pro
pecs-pro init "C:\path\to\workspace"
```

`pecs-pro init` prepares deterministic workspace-local integration and scaffolding:

- `.pecs` structure
- continuity scaffolding
- bridge runtime
- VS Code tasks

### If `pecs-pro` is unavailable on your index

Install from source and run the same initialization flow:

```bash
python3 -m pip install /path/to/PECS_PRO_V2_FINAL/pecs_pro
pecs-pro init "/path/to/workspace"
```

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

Bridge/runtime artifacts are installed minimally under:

```text
.pecs/
	continuity/
	runtime/
	config/
	bridge/
```

## Minimal Invocation Flow

You can run PECS as a minimal deterministic flow:

```bash
pecs-pro init /path/to/your/workspace
pecs-pro refresh /path/to/your/workspace
pecs-pro validate /path/to/your/workspace
```

Equivalent workspace-local bridge invocation:

```bash
python3 .pecs/bridge/run_bridge.py refresh --workspace /path/to/your/workspace
python3 .pecs/bridge/run_bridge.py validate --workspace /path/to/your/workspace
```

PECS favors deterministic continuity stabilization over conversational memory systems.
The bridge remains intentionally lightweight and non-semantic.

## VS Code Task Workflow

After initialization, PECS tasks become available in VS Code.

Workflow:

- VSCode
- Terminal
- Run Task
- select a PECS task

Expected PECS task names:

- `PECS: Start Daemon`
- `PECS: Stop Daemon`
- `PECS: Refresh Continuity State`
- `PECS: Validate Continuity State`
- `PECS: Append Chat Event`
- `PECS: Manual Update Chat History`
- `PECS: Auto Start Daemon On Folder Open` (optional)

## Daemon Lifecycle (Intentional Manual Control)

The PECS daemon does NOT automatically start from package installation.
The user manually starts the daemon during active AI-assisted development sessions.
This is intentional to preserve deterministic and lightweight runtime behavior.

## Bridge Lifecycle

Normal users do NOT need to run the context bridge script directly.
Use standard PECS refresh flow (`pecs-pro refresh` or `PECS: Refresh Continuity State`).
Daemon/refresh operational flow is the supported path.
Bridge execution is handled automatically by the daemon/refresh flow.

The bridge remains:

- lightweight
- deterministic
- non-semantic

## No-Op Silence (Expected Behavior)

After stabilization, PECS intentionally becomes mostly silent.

No-op cycles are expected to produce:

- no rewrites
- no log spam
- no continuity churn

This is intentional and indicates deterministic steady-state behavior.

## New AI Session Workflow

For a new AI session, provide:

- current task/problem
- `.pecs` continuity state

Prefer this over large historical chat dumps.

PECS exists to reduce:

- continuity collapse
- search entropy
- edit locality ambiguity

Chat-history replay is optional and experimental.
Deterministic `.pecs` continuity state should be the primary handoff.

---

For manual setup procedures, see `README_MANUAL_SETUP.md`.
For optional chat-history workflows, see `README_AI_CHAT_HISTORY.md`.

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
