# Copilot Instructions — PECS Workspace Integration

## PECS IS CONTINUITY INFRASTRUCTURE

PECS artifacts are generated continuity infrastructure only.
They do NOT contain editable engineering sourcecode.
Runtime workspace modules are the authoritative implementation.

## Decision Guidance

Before suggesting or applying edits, inspect these files when present:

- `.pecs/active_context.json` — Continuity-local execution context
- `.pecs/compact_bundle.json` — Compressed continuity snapshot
- `.pecs/session_context.json` — Session-specific context
- `.pecs/locality_index.json` — Locality projection index
- `.continue/rules/CONTINUITY_MAP.md` — Continuity guidance map (if present)

### 1. Authority Order

1. Live workspace runtime modules
2. PECS locality projection and continuity artifacts
3. Historical chat memory

### 2. Locality & Targeting

- Use `.pecs` to identify runtime target files and execution locality
- Do not treat `.pecs` paths as editable targets
- Prefer runtime workspace files for actual code edits
- Avoid patching or editing `.pecs` files

### 3. Context Narrowing

- Narrow scope with PECS locality data
- Verify candidate edits against live code
- Use filesystem search only after runtime locality is understood

## Command Execution

When running workspace commands, always activate the environment:

```bash
cd "${workspaceFolder}"
if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
fi
```

For PECS-specific operations:

```bash
python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" \
  --source copilot \
  --message "Summary of changes"
```

## Chat Continuity

After significant Copilot interactions:

```bash
python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" \
  --source copilot \
  --message "Description of work completed"
```

## Principle

- Live runtime workspace modules are authoritative
- PECS artifacts are continuity infrastructure only
- Use PECS for locality/projection, not for source edits
- Do not edit or patch continuity artifacts

## Errors and Warnings

### If PECS Artifacts Are Missing

Copilot will continue to work, but:
- Search will be broader (filesystem-based)
- Context narrowing will be less effective
- Run `pecs repair-workspace` to recover assets

### If PECS Artifacts Are Stale

- The daemon may have stopped
- Run `pecs status`
- Run `pecs refresh-workspace`

## Useful PECS Commands

```bash
# Check status
pecs status

# Refresh artifacts
pecs refresh-workspace $(pwd)

# Validate continuity
pecs verify-workspace $(pwd)

# Diagnose issues
pecs doctor

# Repair installation
pecs repair-workspace $(pwd)
```

## Notes

- This file is installed by the PECS workspace installer
- Do NOT delete or edit `.pecs` files
- PECS is a locality projection layer, not editable sourcecode
