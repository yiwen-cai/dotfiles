# hermes-web-ui "disconnected" diagnosis recipe

Reference for the specific failure mode where `hermes-web-ui` starts successfully but shows the gateway as disconnected, while the Hermes gateway process is actually running and serving requests.

## Failure signature

- Browser opens `http://localhost:8648` → UI loads, but status indicator shows "disconnected"
- `hermes-web-ui` logs contain: `Gateway health check timed out after 15000ms`
- Gateway process is alive and listening on a TCP port
- Direct API calls to the gateway succeed with the correct API key

## Root cause

The Web UI's `GatewayManager` reads `platforms.api_server.extra.port` from `config.yaml` to decide which port to health-check. If this value diverges from the actual gateway listen port (controlled by `API_SERVER_PORT` / `.env`), the manager probes the wrong port, gets connection refused, and marks the gateway as down.

This divergence can happen when:
1. A previous Web UI startup detected a port conflict and auto-reassigned `extra.port` to a new value (e.g. 8643)
2. The gateway itself was later restarted and bound back to the original `API_SERVER_PORT` (e.g. 8642)
3. The two values are now out of sync

## Diagnostic commands (run in order)

```bash
# 1. Check all relevant ports
for p in 8642 8643 8644 8645 8646 8648; do
  printf 'PORT %s: ' "$p"
  lsof -nP -iTCP:$p -sTCP:LISTEN | tail -n +2 || true
done

# 2. Verify gateway health on the port you expect
curl -sS --max-time 3 http://127.0.0.1:8642/health

# 3. Verify models endpoint with API key
curl -sS --max-time 3 http://127.0.0.1:8642/v1/models \
  -H "Authorization: Bearer $(grep '^API_SERVER_KEY:' ~/.hermes/config.yaml | awk '{print $2}')"

# 4. Check the config value the Web UI reads
grep -n "extra:" -A3 ~/.hermes/config.yaml | grep -A2 api_server

# 5. Read Web UI startup log for the exact upstream it chose
tail -40 ~/.hermes-web-ui/server.log | grep -E "Upstream|port|health check timed out"
```

## Fix

Align `platforms.api_server.extra.port` with the actual gateway listen port, then restart:

```bash
# Example: gateway is on 8642, but extra.port was stale at 8646
hermes config set platforms.api_server.extra.port 8642
hermes gateway restart
```

After restart, verify the Web UI health endpoint reports `"gateway":"running"`:

```bash
curl -sS --max-time 3 http://127.0.0.1:8648/health | python3 -m json.tool
```

## Prevention

- After any `hermes-web-ui` auto-port-reassignment event, manually verify that `platforms.api_server.extra.port` matches `API_SERVER_PORT`.
- Avoid running multiple gateway instances (e.g. `hermes gateway run` in one terminal + background service in another) — this creates port confusion.
