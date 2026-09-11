# Hermes WebUI 8787 restart shell fallback diagnosis

Reference for the failure mode where the community Hermes WebUI on port `8787` returns the HTML fallback page:

> Hermes is restarting… The WebUI shell could not load cleanly.

## Failure signature

- Browser at `http://127.0.0.1:8787/` or `http://localhost:8787/` shows the restart fallback page.
- `curl -D - http://127.0.0.1:8787/` returns `HTTP/1.0 503 Service Unavailable` and the fallback HTML.
- `curl http://127.0.0.1:8787/health` may still return `{"status":"ok"...}` because the server loop is alive; only shell serving failed.
- Gateway health may be unrelated and healthy, e.g. `curl http://127.0.0.1:8642/health` returns ok.

## Root cause found in session

A stale WebUI daemon was still listening on `8787`, launched from a path that no longer existed:

```text
/Users/yiwencai/.hermes/hermes-agent/venv/bin/python /Users/yiwencai/code/hermes-webui/server.py
```

The real repo had moved to:

```text
/Users/yiwencai/Documents/code/hermes-webui
```

Because the running process had imported code from the old launch path / environment, it could not serve `static/index.html` cleanly and fell back to `_SHELL_ERROR_HTML` in `api/routes.py`.

## Diagnostic sequence

```bash
# 1. Identify the listener and command.
lsof -nP -iTCP:8787 -sTCP:LISTEN || true
ps -p <PID> -o pid,ppid,etime,command

# 2. Check whether the command path still exists.
python3 - <<'PY'
from pathlib import Path
for p in [
    '/Users/yiwencai/code/hermes-webui/server.py',
    '/Users/yiwencai/Documents/code/hermes-webui/server.py',
]:
    q = Path(p)
    print(p, q.exists(), q.stat().st_size if q.exists() else None)
PY

# 3. Confirm health vs shell mismatch.
curl -sS -D - http://127.0.0.1:8787/ -o /tmp/hermes_webui_root.html | head -40
curl -sS http://127.0.0.1:8787/health | python3 -m json.tool

# 4. Check gateway separately, because this fallback is often not a gateway problem.
curl -sS --max-time 2 http://127.0.0.1:8642/health
```

## Fix

Stop the stale listener, then start from the actual repo path:

```bash
# Replace <PID> with the PID from lsof.
kill <PID> || true
sleep 1
kill -0 <PID> 2>/dev/null && kill -KILL <PID> || true

cd /Users/yiwencai/Documents/code/hermes-webui
./ctl.sh start 8787
./ctl.sh status
```

Verify the shell now serves normally:

```bash
curl -sS -D /tmp/hw_headers.txt http://127.0.0.1:8787/ -o /tmp/hw_root.html
head -40 /tmp/hw_headers.txt
python3 - <<'PY'
from pathlib import Path
s = Path('/tmp/hw_root.html').read_text(errors='replace')
print('has restarting', 'Hermes is restarting' in s)
print('len', len(s))
PY
```

Expected: status `200 OK`, `has restarting False`, and a large HTML body.

## ctl.sh pitfalls encountered

In one session, `ctl.sh start` failed before starting the daemon with:

```text
./ctl.sh: line 42: conditional binary operator expected
```

The cause was `[[ -v ${key} ]]` under the active shell / bash compatibility. Replace it with a portable environment lookup:

```bash
if env | grep -F -q -- "${key}="; then
  value="${!key}"
  preserved+=("${key}=${value}")
fi
```

Then `ctl.sh start` failed with:

```text
CTL_BOOTSTRAP_ARGS[@]: unbound variable
```

under `set -u` when no extra bootstrap args were passed. Guard the array expansion:

```bash
if ((${#CTL_BOOTSTRAP_ARGS[@]})); then
  exec "${python_exe}" "${REPO_ROOT}/bootstrap.py" --no-browser --foreground --host "${CTL_HOST}" "${CTL_PORT}" "${CTL_BOOTSTRAP_ARGS[@]}"
else
  exec "${python_exe}" "${REPO_ROOT}/bootstrap.py" --no-browser --foreground --host "${CTL_HOST}" "${CTL_PORT}"
fi
```

Run `bash -n ctl.sh` after patching shell scripts.
