# Desktop Model Config Not Applied — Session State Overrides config.yaml

## Problem Signature

User changes `model.default` in `~/.hermes/config.yaml` (e.g., to `kimi-for-coding`), rebuilds the Desktop app, but on launch the composer still shows the **old model** (e.g., `deepseek-v4-flash`).

## Root Cause

The Desktop app **restores the model from the most recent session's state** (`state.db`) rather than re-reading `config.yaml` on every boot. Specifically:

1. `use-session-actions.ts` calls `setCurrentModel(info.model)` when a session is resumed
2. `use-model-controls.ts` has `refreshCurrentModel()` which calls `getGlobalModelInfo()` (reads `config.yaml`)
3. **But** `refreshCurrentModel()` skips the update if `$currentModel` already has a value (from the resumed session)
4. The `desktop-controller.tsx` effect on `gatewayState === 'open'` calls `refreshCurrentModel()` **without** `force=true`

So the sequence is:
```
Boot → gateway opens → route resume fires → session restored → model set from state.db
       → refreshCurrentModel() called → sees $currentModel is already set → skips
```

## Verification

Check the most recent sessions in `state.db`:
```bash
sqlite3 ~/.hermes/state.db "SELECT id, model, started_at FROM sessions ORDER BY started_at DESC LIMIT 5;"
```
If the latest session has a different model than `config.yaml`, that's the source.

Also verify the backend sees the correct config:
```bash
cd ~/.hermes/hermes-agent
python -c "from hermes_cli.web_server import get_model_info; import json; print(json.dumps(get_model_info(), indent=2))"
# Should show: {"model": "kimi-for-coding", "provider": "kimi-coding", ...}
```

## Fix: Force Reseed from Global Config on Boot

Two files need changes:

### 1. `apps/desktop/src/app/session/hooks/use-model-controls.ts`

Change `refreshCurrentModel` so that when `force=true`, it **always** updates from `getGlobalModelInfo()` regardless of whether `$currentModel` already has a value:

```typescript
const refreshCurrentModel = useCallback(async (force = false) => {
  try {
    if ($activeSessionId.get()) {
      return
    }

    if (!force && $currentModel.get()) {
      return
    }

    const result = await getGlobalModelInfo()

    if ($activeSessionId.get()) {
      return
    }

    // When force=true, always update; when force=false, only update if empty
    if (force || !$currentModel.get()) {
      if (typeof result.model === 'string') {
        setCurrentModel(result.model)
      }

      if (typeof result.provider === 'string') {
        setCurrentProvider(result.provider)
      }
    }
  } catch {
    // The delayed session.info event still updates this once the agent is ready.
  }
}, [])
```

### 2. `apps/desktop/src/app/desktop-controller.tsx`

Change the `gatewayState === 'open'` effect to pass `force=true`:

```typescript
useEffect(() => {
  if (gatewayState === 'open') {
    // Force reseed on initial gateway open so config.yaml changes are picked up
    // immediately (e.g. switching from deepseek to kimi-coding).
    void refreshCurrentModel(true)
    void refreshActiveProfile()
    void refreshSessions().catch(() => undefined)
  }
}, [gatewayState, refreshCurrentModel, refreshSessions])
```

## Rebuild

```bash
cd apps/desktop
npm run build
```

## Alternative Workarounds (No Code Change)

1. **Start a fresh session** (instead of resuming the previous one) — fresh sessions read `config.yaml` directly
2. **Manually switch model** via the composer model picker after launch
3. **Clear session state** (nuclear): `rm ~/.hermes/state.db` and restart (loses all session history)

## Related Code Paths

| File | Line | Purpose |
|------|------|---------|
| `apps/desktop/src/app/session/hooks/use-model-controls.ts` | 49 | `refreshCurrentModel()` — seeds composer model from global config |
| `apps/desktop/src/app/session/hooks/use-session-actions.ts` | 312 | `setCurrentModel(info.model)` — restores model from resumed session |
| `apps/desktop/src/app/desktop-controller.tsx` | 855 | `gatewayState === 'open'` effect that triggers model refresh |
| `hermes_cli/web_server.py` | 3420 | `get_model_info()` — reads `config.yaml` model configuration |
| `hermes_cli/inventory.py` | 79 | `load_picker_context()` — loads disk config for model picker |
