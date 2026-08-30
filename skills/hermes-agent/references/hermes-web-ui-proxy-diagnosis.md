# Hermes Web UI proxy diagnosis and injection

Use this when WebUI or provider/network calls appear to time out and the user suggests a local proxy port such as `7897`.

## What was learned

- Testing a proxy with `curl -x` only proves the proxy itself works; it does not prove the running WebUI process is using that proxy.
- Check both the current shell env and the WebUI process env before deciding whether a restart/config change is needed.
- If `hermes-ui status` / `./ctl.sh status` reports active streams, avoid restarting WebUI unless the user explicitly accepts interrupting active runs.

## Diagnostic commands

From the `hermes-webui` checkout:

```bash
# Current shell proxy env
env | grep -Ei '^(http|https|all|no)_proxy=' || true

# WebUI status and active streams
./ctl.sh status

# Probe whether the proxy port can reach external services
curl -I -L --connect-timeout 5 --max-time 15 \
  -x http://127.0.0.1:7897 \
  https://api.github.com

curl -sS --connect-timeout 5 --max-time 10 \
  -x http://127.0.0.1:7897 \
  https://api.ipify.org

curl -sS --connect-timeout 5 --max-time 10 \
  -x socks5h://127.0.0.1:7897 \
  https://api.ipify.org

# Inspect proxy env inherited by the running WebUI process
pid=$(cat ~/.hermes/webui.pid 2>/dev/null || true)
if [[ -n "$pid" ]]; then
  ps eww -p "$pid" | tr ' ' '\n' | grep -Ei '^(HTTP|HTTPS|ALL|NO)_PROXY=' || true
fi
```

## Interpreting results

- `HTTP/1.1 200 Connection established` or any provider HTTP response means the proxy path connected; API-level `403`, `401`, or rate-limit responses are not network timeouts.
- An IP from `api.ipify.org` confirms outbound traffic went through the proxy.
- Empty process-env output means the already-running WebUI process is not using the proxy, even if the shell probe succeeded.

## Injecting proxy into WebUI

Only restart when there are no active streams, or after user confirmation:

```bash
HTTP_PROXY=http://127.0.0.1:7897 \
HTTPS_PROXY=http://127.0.0.1:7897 \
ALL_PROXY=socks5h://127.0.0.1:7897 \
NO_PROXY=localhost,127.0.0.1 \
./ctl.sh restart
```

After restart, re-run the process-env inspection above to verify the proxy variables are present in the WebUI process.
