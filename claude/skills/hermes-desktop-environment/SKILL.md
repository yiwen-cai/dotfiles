---
name: hermes-desktop-environment
description: "Manage Hermes Desktop installation, Node version alignment, and environment troubleshooting."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, desktop, electron, node, nvm, setup, troubleshooting]
    category: devops
---

# Hermes Desktop Environment Management

Handle Hermes Desktop setup, Node version conflicts, Electron download failures, and related environment issues.

## When to Use

- `hermes desktop` fails during installation or build
- Node version mismatch warnings (e.g., "Unsupported engine", "upgrade to 23+")
- Electron binary download fails (`socket hang up`, timeout)
- Need to make Hermes use a system/nvm Node instead of bundled v22

## Node Version Architecture

Hermes bundles its own Node at `~/.hermes/node/bin/node`. It also creates a symlink:

```
~/.local/bin/node -> ~/.hermes/node/bin/node
```

This often precedes nvm in PATH, causing Hermes to use the bundled version even when the shell has a newer nvm Node.

| Node Source | Path | Typical Version |
|-------------|------|-----------------|
| Hermes bundled | `~/.hermes/node/bin/node` | v22 (as of 2026-06) |
| nvm active | `~/.nvm/versions/node/v23.x.x/bin/node` | v23+ |
| System | `/usr/local/bin/node` | varies |

## Switching Hermes to nvm Node (Recommended)

Instead of replacing the bundled Node directory (which breaks if the download fails or Hermes updates), symlink Hermes's internal binaries to nvm:

```bash
cd ~/.hermes/node/bin
mv node node-v22
ln -s ~/.nvm/versions/node/v23.11.1/bin/node node
mv npm npm-v22
ln -s ~/.nvm/versions/node/v23.11.1/bin/npm npm
mv npx npx-v22
ln -s ~/.nvm/versions/node/v23.11.1/bin/npx npx
```

Verify:
```bash
~/.hermes/node/bin/node -v   # should show v23.x.x
```

Benefits:
- Hermes still "owns" its node directory structure
- Future nvm upgrades automatically propagate
- Reversible: just `rm node && mv node-v22 node`

## Electron Download Failures

### Symptom
```
RequestError: socket hang up
```
during `> electron install.js` or `hermes desktop` build.

### Root Cause
Electron postinstall downloads `electron-v*.zip` from GitHub releases. Direct GitHub access may be blocked or slow.

### Fix: Use Electron Mirror
```bash
export ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
hermes desktop
```

Or set persistently:
```bash
npm config set electron_mirror https://npmmirror.com/mirrors/electron/
```

### Fix: Ensure Proxy/TUN Covers Terminal
If using a TUN proxy, verify terminal traffic actually routes through it:
```bash
curl -I --max-time 20 https://github.com/electron/electron/releases/download/v37.6.0/electron-v37.6.0-darwin-arm64.zip
```
Should return HTTP 206/302, not timeout.

## Common Warnings (Non-Fatal)

| Warning | Meaning | Action |
|---------|---------|--------|
| `EBADENGINE Unsupported engine` | Package wants Node 20/22/24+, current is 23 | Usually harmless; Node 23 is newer than required |
| `npm warn deprecated inflight/rimraf/glob` | Old transitive deps | Cosmetic, does not block install |
| `skipped macOS code signing` | No Apple Developer ID | Expected for local builds; app runs unsigned |
| `Skipping notarization` | APPLE_API_KEY not set | Expected for local builds |

Only act if the warning is followed by an actual error or non-zero exit.

## Installation Stage Breakdown

When `hermes desktop` runs, it typically executes:

1. **Python deps** — `pip install` for browser tools, etc.
2. **Node deps** — `npm ci` in workspace root
3. **Desktop build** — `npm run pack` in `apps/desktop`
   - `npm run build` — Vite frontend build
   - `electron-builder` — Package Electron app
   - **Failure point**: Electron binary download during `electron` package postinstall

If stage 1-2 succeed but 3 fails, the issue is almost always Electron download, not npm packages.

## Relevant Paths

| Path | Purpose |
|------|---------|
| `~/.hermes/node/bin/node` | Hermes bundled Node |
| `~/.local/bin/node` | Symlink to Hermes Node (often in PATH before nvm) |
| `~/.hermes/hermes-agent/apps/desktop` | Desktop app source |
| `~/.hermes/hermes-agent/apps/desktop/release/mac-arm64` | Packaged app output (macOS ARM) |
| `~/.npm/_logs/` | npm debug logs for failure analysis |

## JSON-RPC Timeout: "request timed out: prompt.submit"

### Symptom
Sending a message in the Desktop app shows:
```
request timed out: prompt.submit
```
The UI may also show repeated `APIConnectionError` / `Connection error.` in the desktop log.

### Root Cause
The Desktop JSON-RPC client has a default request timeout of **30 seconds** (`apps/desktop/src/hermes.ts`). If the LLM API (e.g., a slow or high-latency provider) takes longer to respond, the gateway call times out before the backend finishes.

### Fix: Increase Gateway Timeout
Edit `apps/desktop/src/hermes.ts`:
```typescript
// Before
const DEFAULT_GATEWAY_REQUEST_TIMEOUT_MS = 30_000

// After
const DEFAULT_GATEWAY_REQUEST_TIMEOUT_MS = 120_000
```
Then rebuild:
```bash
cd apps/desktop
npm run build
```

### Verification
Check the compiled value:
```bash
grep -n "DEFAULT_GATEWAY_REQUEST_TIMEOUT_MS" src/hermes.ts
# Should show: const DEFAULT_GATEWAY_REQUEST_TIMEOUT_MS = 120_000
```

## Model Config Not Applied: Session State Overrides config.yaml

### Symptom
Changing `model.default` in `~/.hermes/config.yaml` has no effect — the Desktop app still launches with the previous model.

### Root Cause
The Desktop app restores the model from the most recent session (`state.db`) rather than re-reading `config.yaml` on every boot. The `refreshCurrentModel()` call on startup sees `$currentModel` is already set (from session resume) and skips the update.

### Quick Fix (No Code Change)
Start a **fresh session** instead of resuming the previous one. Fresh sessions read `config.yaml` directly.

### Code Fix
See `references/model-config-not-applied.md` for the two-file patch (`use-model-controls.ts` + `desktop-controller.tsx`) that forces a reseed from global config on every gateway open.

### Related Timeout Layers
| Layer | Timeout | Location | Governs |
|-------|---------|----------|---------|
| Desktop JSON-RPC | 30s → 120s | `apps/desktop/src/hermes.ts` | Gateway method calls (prompt.submit, etc.) |
| TUI JSON-RPC | 120s (env-configurable) | `ui-tui/src/gatewayClient.ts` | TUI gateway calls |
| Shared library default | 120s | `apps/shared/src/json-rpc-gateway.ts` | Fallback for all JSON-RPC clients |
| Session busy retry | 6s | `use-prompt-actions.ts` | Retries when gateway reports "session busy" |
| Approval/sudo/secret | 5 min | Gateway config | Tool approval prompts |

### Historical Fixes (git log)
- `18916376f` — "never surface 'session busy' — retry every submit past it"
- `f66a929a6` — "render approval/sudo/secret prompts so tools stop silently timing out"
- `825629424` — "persist timed-out/cancelled clarify prompts in transcript"

## Related Skills

- `hermes-agent` — Core Hermes CLI reference (bundled, read-only)
- `hermes-web-ui-local-control-and-scroll` — Web UI wrapper and scroll behavior

## References

- `references/electron-download-mirror.md` — Mirror configuration and verification
- `references/node-version-symlink.md` — Detailed symlink workflow and reversal
- `references/json-rpc-timeout-debugging.md` — Timeout debugging, log analysis, and provider-specific latency issues
- `references/model-config-not-applied.md` — When changing `model.default` in `config.yaml` doesn't appear in the Desktop app (session state overrides disk config)
