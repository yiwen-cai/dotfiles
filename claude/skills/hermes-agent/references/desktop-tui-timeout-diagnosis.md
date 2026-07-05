# Desktop/TUI "request timed out: prompt.submit" Diagnosis

## Problem

Hermes Desktop or TUI shows `request timed out: prompt.submit` when sending messages. The error comes from `apps/shared/src/json-rpc-gateway.ts:238` — the JSON-RPC client's request timeout mechanism.

## Root Causes

### 1. Desktop Default Timeout Too Short

**Location:** `apps/desktop/src/hermes.ts:46`

```typescript
const DEFAULT_GATEWAY_REQUEST_TIMEOUT_MS = 30_000  // 30 seconds
```

The desktop uses 30 seconds, while the shared library defaults to 120 seconds (`apps/shared/src/json-rpc-gateway.ts:61`). When LLM processing takes longer (tool calls, reasoning, slow API), the request times out.

### 2. TUI Configurable Timeout

**Location:** `ui-tui/src/gatewayClient.ts:18`

```typescript
const REQUEST_TIMEOUT_MS = Math.max(30000, parseInt(process.env.HERMES_TUI_RPC_TIMEOUT_MS ?? '120000', 10) || 120000)
```

TUI defaults to 120 seconds but can be overridden via environment variable.

### 3. API Provider Slowness

Check `~/.hermes/logs/agent.log` for:
- `APIConnectionError` / `Connection error`
- `Request timed out.` from the LLM provider
- SSL handshake timeouts: `The handshake operation timed out`

## Diagnostic Steps

### 1. Check Which Client Is Being Used

```bash
# Desktop logs
tail -100 ~/.hermes/logs/desktop.log

# TUI logs (if running via dashboard)
tail -100 ~/.hermes/logs/gateway.log

# Agent logs (shows platform)
grep "platform=" ~/.hermes/logs/agent.log | tail -5
# Look for: platform=desktop, platform=tui, platform=cli
```

### 2. Verify Timeout Configuration

**Desktop:** Check `apps/desktop/src/hermes.ts` for `DEFAULT_GATEWAY_REQUEST_TIMEOUT_MS`

**TUI:** Check environment variable:
```bash
echo $HERMES_TUI_RPC_TIMEOUT_MS
```

### 3. Check API Provider Health

```bash
# Look for connection errors in agent log
grep -E "APIConnectionError|Request timed out|handshake" ~/.hermes/logs/agent.log | tail -20

# Test provider endpoint directly
curl -s -o /dev/null -w "%{http_code}" https://your-provider-endpoint/v1/models -H "Authorization: Bearer $YOUR_API_KEY"
```

## Fixes

### Fix 1: Increase Desktop Timeout (Recommended)

Edit `apps/desktop/src/hermes.ts`:

```typescript
// Change from:
const DEFAULT_GATEWAY_REQUEST_TIMEOUT_MS = 30_000
// To:
const DEFAULT_GATEWAY_REQUEST_TIMEOUT_MS = 120_000
```

Then rebuild:
```bash
cd ~/.hermes/hermes-agent/apps/desktop
npm run build
```

### Fix 2: Increase TUI Timeout via Environment Variable

```bash
export HERMES_TUI_RPC_TIMEOUT_MS=180000  # 3 minutes
```

Add to shell profile for persistence:
```bash
echo 'export HERMES_TUI_RPC_TIMEOUT_MS=180000' >> ~/.zshrc
```

### Fix 3: Address API Provider Issues

If the provider is slow:
- Check network stability
- Consider switching providers: `hermes model`
- Increase provider-specific timeouts in `config.yaml`

## Related GitHub Fixes

- **#38578** (`f66a929a6`) — fix(desktop): render approval/sudo/secret prompts so tools stop silently timing out
- **18916376f** — fix(desktop): never surface "session busy" — retry every submit past it
- **825629424** — fix(tui): persist timed-out/cancelled clarify prompts in transcript

## Key Code Locations

| Component | File | Key Line |
|-----------|------|----------|
| Desktop timeout config | `apps/desktop/src/hermes.ts` | Line 46 |
| TUI timeout config | `ui-tui/src/gatewayClient.ts` | Line 18 |
| Shared timeout default | `apps/shared/src/json-rpc-gateway.ts` | Line 61 |
| Timeout error throw | `apps/shared/src/json-rpc-gateway.ts` | Line 238 |
| Session busy retry | `apps/desktop/src/app/session/hooks/use-prompt-actions.ts` | Lines 127-148 |

## Log Files to Check

| Log File | Path | What to Look For |
|----------|------|-----------------|
| Desktop log | `~/.hermes/logs/desktop.log` | Bootstrap errors, connection issues |
| Agent log | `~/.hermes/logs/agent.log` | API timeouts, provider errors |
| Gateway log | `~/.hermes/logs/gateway.log` | Gateway health, WebSocket issues |
| Errors log | `~/.hermes/logs/errors.log` | Stack traces, exceptions |
| TUI crash log | `~/.hermes/logs/tui_gateway_crash.log` | Signal handlers, thread dumps |
