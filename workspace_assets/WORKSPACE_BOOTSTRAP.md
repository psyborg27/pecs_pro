# PECS Workspace Bootstrap

## What This File Does

This file is the workspace bootstrap checkpoint. It confirms PECS workspace assets were successfully installed and configured.

## Installation Status

When you see this file in `.pecs/WORKSPACE_BOOTSTRAP.md`, it means:

- ✓ PECS workspace assets were installed
- ✓ Copilot instructions configured
- ✓ Continue rules installed
- ✓ Daemon infrastructure bootstrapped
- ✓ Continuity directories initialized

## Quick Verification

Run:
```bash
pecs verify-workspace $(pwd)
```

This will validate:
- All required assets present
- Configuration files valid
- Daemon infrastructure ready
- Ingress routing installed

## Next Steps

1. **Start the daemon:**
   ```bash
   # Via VS Code Task: "PECS: Start Daemon"
   # Or manually:
   cd $(pwd)
   source .venv/bin/activate  # if present
   PECS_PRO_REPO=/path/to/pecs-pro ./launch_pecs_daemon.sh $(pwd)
   ```

2. **Refresh continuity state:**
   ```bash
   pecs refresh-workspace $(pwd)
   ```

3. **Open Continue/Copilot:**
   - Both should now respect PECS-first routing
   - Check `.pecs/active_context.json` during edits
   - Verify locality-aware suggestions

## Troubleshooting

### Assets Missing After Install?

```bash
pecs repair-workspace $(pwd)
```

### Daemon Not Running?

```bash
pecs status
pecs doctor
```

### Copilot/Continue Not Using PECS?

1. Verify `.github/copilot-instructions.md` exists
2. Verify `.continue/rules/pecs-first-routing.yaml` exists
3. Reload workspace in VS Code
4. Restart Continue
5. Run `pecs doctor` to diagnose

## Documentation

For detailed information, see:
- `.pecs/README.md` — Workspace-local documentation
- `.github/copilot-instructions.md` — Copilot configuration
- `.continue/rules/pecs-first-routing.yaml` — Continue routing rules

## Support

For issues, run:
```bash
pecs doctor
```

This will diagnose:
- Python environment
- Required packages
- Daemon status
- Asset files
- Configuration validity
