# JSON-RPC Timeout Debugging Reference

## Problem Signature

```
request timed out: prompt.submit
```

Error originates from `apps/shared/src/json-rpc-gateway.ts:238`:
```typescript
pending.timer = setTimeout(() => {
  if (this.pending.delete(id)) {
    reject(new Error(`request timed out: ${method}`))
  }
}, timeoutMs)
```

## Log Analysis Workflow

### 1. Check Desktop Logs
```bash
ls -la ~/.hermes/logs/
# Key files:
# - ~/.hermes/logs/desktop.log          # Desktop app boot and events
# - ~/.hermes/logs/errors.log            # Python errors from backend
# - ~/.hermes/logs/gateway.log           # Gateway runtime
# - ~/.hermes/logs/tui_gateway_crash.log # TUI gateway crashes
```

### 2. Identify the Actual Failure Layer

| Log Pattern | Meaning | Fix |
|-------------|---------|-----|
| `APIConnectionError` / `Connection error.` | LLM API unreachable or slow | Check network, increase timeout, switch provider |
| `Request timed out.` (in agent.log) | OpenAI client-level timeout | Provider latency issue, not Desktop |
| `session busy` | Gateway concurrency guard | Already auto-retried in recent versions (commit 18916376f) |
| `The handshake operation timed out` | SSL/TLS connection slow | Network or proxy issue |

### 3. Distinguish Desktop vs TUI vs Gateway Timeouts

- **Desktop** (`platform=desktop` in agent.log): Uses `apps/desktop/src/hermes.ts` (30s default)
- **TUI** (`platform=tui` in agent.log): Uses `ui-tui/src/gatewayClient.ts` (120s default, env-configurable)
- **Gateway** (backend): Uses Python-level timeouts for LLM API calls

If the user says "Desktop" but agent.log shows `platform=tui`, they're actually using the TUI mode.

## Provider-Specific Latency Notes

### nowcoding.ai / custom providers
- Often slower than major providers (OpenAI, Anthropic)
- May require 60-120s timeout for complex prompts
- SSL handshake can also be slow (`_ssl.c:999: The handshake operation timed out`)

### kimi-coding (Kimi API)
- Models: `kimi-for-coding`, `kimi-k2.7-code`, `kimi-k2.6`, etc.
- Usually responsive but can spike during peak hours

## Timeout Configuration Hierarchy

```
User env var (TUI only)
  → HERMES_TUI_RPC_TIMEOUT_MS=180000

Desktop app code
  → apps/desktop/src/hermes.ts: DEFAULT_GATEWAY_REQUEST_TIMEOUT_MS

Shared library fallback
  → apps/shared/src/json-rpc-gateway.ts: DEFAULT_REQUEST_TIMEOUT_MS = 120_000
```

## Relevant Code Paths

| File | Line | Purpose |
|------|------|---------|
| `apps/desktop/src/hermes.ts` | 46 | Desktop timeout constant |
| `apps/desktop/src/hermes.ts` | 116 | Gateway client instantiation |
| `apps/shared/src/json-rpc-gateway.ts` | 61 | Shared library default timeout |
| `apps/shared/src/json-rpc-gateway.ts` | 220-240 | request() method with timeout logic |
| `ui-tui/src/gatewayClient.ts` | 18 | TUI timeout (env-configurable) |
| `tui_gateway/server.py` | 6097 | `prompt.submit` handler |

## Build Verification

After modifying timeout:
```bash
cd apps/desktop
npm run build
# Verify dist built:
ls dist/index.html dist/assets/
```

## Related Git Commits

- `18916376f` — fix(desktop): never surface "session busy" — retry every submit past it
- `f66a929a6` — fix(desktop): render approval/sudo/secret prompts so tools stop silently timing out (#38578)
- `825629424` — fix(tui): persist timed-out/cancelled clarify prompts in transcript