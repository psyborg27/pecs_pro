# PECS Workspace Integration (.pecs/)

THIS DIRECTORY IS GENERATED CONTINUITY INFRASTRUCTURE.
DO NOT EDIT.
DO NOT PATCH.
DO NOT TREAT AS ENGINEERING SOURCECODE.

THIS FILE DOES NOT CONTAIN SOURCECODE.
IT ONLY CONTAINS:
- ENGINEERING TARGET LOCATIONS
- EXECUTION LOCALITY
- CONTINUITY RELATIONSHIPS
- RUNTIME TOPOLOGY

ENGINEERING TRUTH EXISTS ONLY IN:
WORKSPACE RUNTIME MODULES.

## Directory Structure

```
.pecs/
├── README.md (this file)
├── README_WORKSPACE_INTEGRATION.md
├── README_MANUAL_SETUP.md
├── ai_chat_history.json
├── tools/
│   ├── append_ai_chat_history.py
│   └── update_ai_chat_history.sh
├── bridge/
│   ├── run_bridge.py
│   ├── run_bridge.sh
│   ├── export_workspace_continuity.py
│   └── validate_workspace_continuity.py
├── config/
│   └── continuity_bridge.json
├── continuity/
│   ├── active_topology.json
│   ├── locality_state.json
│   ├── architectural_decisions.md
│   ├── current_workspace_focus.md
│   └── unresolved_tensions.md
├── runtime/
│   └── .gitkeep
└── sessions/
    └── (generated at runtime)
```

## Key Files

### Tools

- **append_ai_chat_history.py** — Append events to ai_chat_history.json
- **update_ai_chat_history.sh** — Manual script to update chat history

### Bridge Runtime

- **run_bridge.py** — Python runner for continuity bridge
- **run_bridge.sh** — Shell wrapper for bridge
- **export_workspace_continuity.py** — Export continuity state
- **validate_workspace_continuity.py** — Validate continuity

### Configuration

- **continuity_bridge.json** — Bridge configuration
  - Schema version
  - Mode (deterministic_continuity_stabilization)
  - Output options

### Continuity State

- **active_topology.json** — Current runtime topology
- **locality_state.json** — Workspace locality metrics
- **architectural_decisions.md** — Architecture decisions
- **current_workspace_focus.md** — Current work focus
- **unresolved_tensions.md** — Known issues

### Chat History

- **ai_chat_history.json** — Agent interaction history
  - Copilot interactions
  - Continue interactions
  - Manual annotations

## Operations

### Start Daemon

Via VS Code Task:
```
PECS: Start Daemon
```

Or manually:
```bash
cd $(pwd)
source .venv/bin/activate  # if present
PECS_PRO_REPO=/path/to/pecs-pro ./launch_pecs_daemon.sh $(pwd)
```

### Refresh Continuity State

Via VS Code Task:
```
PECS: Refresh Continuity State
```

Or manually:
```bash
cd $(pwd)
source .venv/bin/activate  # if present
python3 .pecs/bridge/run_bridge.py refresh --workspace $(pwd)
```

### Validate Continuity

Via VS Code Task:
```
PECS: Validate Continuity State
```

Or manually:
```bash
cd $(pwd)
source .venv/bin/activate  # if present
python3 .pecs/bridge/run_bridge.py validate --workspace $(pwd)
```

### Append Chat Event

Manual:
```bash
python3 .pecs/tools/append_ai_chat_history.py $(pwd) \
  --source copilot \
  --message "Summary of work"
```

Via VS Code Task:
```
PECS: Append Chat Event
```

## Continuity Guidance

PECS artifacts are queryable continuity infrastructure only.
They are NOT editable engineering sourcecode.

- Use `.pecs` to derive runtime targets and locality.
- Do not patch `.pecs` files.
- Do not use `.pecs` paths as edit targets.
- Runtime workspace modules are the authoritative implementation.

## Daemon Coordination

PECS daemon:
- Monitors workspace for changes
- Updates continuity artifacts in real-time
- Maintains ai_chat_history.json
- Coordinates with Copilot/Continue via hooks

## Troubleshooting

### Daemon Not Running?

```bash
pecs status
pecs doctor
```

### Artifacts Not Updating?

```bash
pecs refresh-workspace $(pwd)
```

### Validation Failing?

```bash
python3 .pecs/bridge/run_bridge.py validate --workspace $(pwd)
```

## Git Ignore

.pecs/ contains generated and runtime files. Standard .gitignore:

```
# Runtime state
.pecs/runtime/**
!.pecs/runtime/.gitkeep

# Generated continuity
.pecs/continuity/generated/**

# Session artifacts
.pecs/sessions/**

# Temporary files
.pecs/tmp/**
```

Keep in version control:
- tools/
- bridge/
- config/
- continuity/*.md (architecture decisions)
- ai_chat_history.json (interaction history)

## Documentation

For detailed information, see:
- `README_WORKSPACE_INTEGRATION.md` — Integration details
- `README_MANUAL_SETUP.md` — Manual setup guide
- `../README_WORKSPACE_PREPARATION.md` — Preparation guide
- `../WORKSPACE_BOOTSTRAP.md` — Bootstrap checkpoint
