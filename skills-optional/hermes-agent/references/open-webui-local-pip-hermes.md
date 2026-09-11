# Open WebUI local pip setup with Hermes API Server

Session-derived notes for configuring Open WebUI without Docker.

## Working shape

Use Open WebUI's local CLI and point it at the already-running Hermes API Server:

```bash
DATA_DIR="$HOME/.open-webui" \
OPENAI_API_BASE_URL="http://127.0.0.1:<port>/v1" \
OPENAI_API_KEY="<hermes-api-server-key>" \
ENABLE_OLLAMA_API=false \
open-webui serve --host 127.0.0.1 --port 8080
```

Open WebUI then serves at:

```text
http://127.0.0.1:8080
```

## Verification commands

Check whether Open WebUI and Hermes are reachable:

```bash
python3 - <<'PY'
import socket
for port in [8080, 3000, 8642, 8643]:
    s = socket.socket()
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", port))
        print(f"127.0.0.1:{port}=open")
    except Exception:
        print(f"127.0.0.1:{port}=closed")
    finally:
        s.close()
PY
```

Check Hermes API health and models:

```bash
curl -s http://127.0.0.1:<port>/health
curl -s -H "Authorization: Bearer <key>" http://127.0.0.1:<port>/v1/models | python3 -m json.tool
```

Check Open WebUI page:

```bash
curl -I http://127.0.0.1:8080
```

## Pitfalls discovered

- `open-webui` may be installed under `~/.local/bin/open-webui`; verify with `command -v open-webui` before recommending Docker.
- If Open WebUI is not Dockerized, use `http://127.0.0.1:<port>/v1`, not `host.docker.internal`.
- `open-webui serve` can take a while on first run because it performs Alembic migrations. Wait for the port to open rather than assuming failure from long migration logs.
- Run Open WebUI from a stable working directory and set `DATA_DIR=$HOME/.open-webui`; otherwise it may create `.webui_secret_key` and data files under the current project directory.
- If a Hermes gateway is already running, starting `hermes gateway` may fail with "Gateway already running". Probe the existing API server ports before restarting.
- In this session, `hermes config set API_SERVER_PORT 8642` added top-level keys to `config.yaml`, but the running gateway still served API Server on `platforms.api_server.extra.port: 8643`. Trust live `/health` and `/v1/models` probes over config assumptions.
- Open WebUI's unauthenticated `/api/models` can return `{"detail":"Not authenticated"}` even when the UI itself is working; use browser login or Hermes `/v1/models` to verify backend connectivity.

## Recommended no-Docker sequence

1. Verify `open-webui` is installed:

```bash
command -v open-webui
```

2. Configure/generate a Hermes API key. Prefer the effective API server config already used by the running gateway when present.

3. Probe Hermes API ports and identify the live one:

```bash
curl -s http://127.0.0.1:8642/health || true
curl -s http://127.0.0.1:8643/health || true
```

4. Start Open WebUI locally with the live Hermes base URL:

```bash
DATA_DIR="$HOME/.open-webui" \
OPENAI_API_BASE_URL="http://127.0.0.1:8643/v1" \
OPENAI_API_KEY="<key>" \
ENABLE_OLLAMA_API=false \
open-webui serve --host 127.0.0.1 --port 8080
```

5. Open `http://127.0.0.1:8080`, register/login, and choose `hermes-agent`.
