# Provider Authentication Pitfalls

Real-world authentication issues encountered when working with multiple providers in Hermes.

## One key, multiple providers — does NOT work

**Pitfall:** Reusing the same API key across different providers.

**Example from session:**
- `NOWCODING_API_KEY` worked for `nowcoding.ai` (returned 200, model list included gpt-5.5)
- Same key failed for `api.kimi.com/coding` with `invalid_authentication_error`

**Rule:** Each provider requires its own key. Verify each independently.

## Config key vs env key

**Pitfall:** Assuming `config.yaml` provider key overrides `.env` or vice versa.

**Hermes behavior:**
- `config.yaml` `providers.*.api_key` — inline key, readable by agent tools
- `config.yaml` `providers.*.key_env` — references env var name
- `.env` — env vars, protected from agent writes

**From session:** The `kimi-coding` provider had `api_key: ''` in config.yaml and no `key_env` set. The nowcoding key was in `providers.nowcoding.api_key`. Hermes could not find a valid key for kimi-coding.

## Provider key not in .env

**Pitfall:** Looking for provider keys in `.env` when they are actually in `config.yaml`.

**Session check:**
```bash
grep -i "kimi\|api_key" ~/.hermes/config.yaml | head -n 20
```
This revealed the nowcoding key was in config.yaml under `providers.nowcoding.api_key`, while `kimi-coding` had an empty `api_key`.

## How to set a provider key

**Option A — config.yaml (agent-writable):**
```bash
hermes config set providers.kimi-coding.api_key "your-key-here"
```

**Option B — .env (user must do manually):**
```bash
echo 'KIMI_API_KEY=your-key-here' >> ~/.hermes/.env
```
Note: `.env` is protected from agent tool writes. The user must run this themselves.

**Option C — key_env reference in config.yaml:**
```yaml
providers:
  kimi-coding:
    base_url: https://api.kimi.com/coding
    key_env: KIMI_API_KEY
```
Then set `KIMI_API_KEY` in `.env` (user must do manually).

## Pre-delegation verification checklist

Before spawning subagents with model assignments:

1. [ ] Check main agent model is reachable: test chat completion
2. [ ] Check subagent model is reachable: test chat completion
3. [ ] Verify both models are in their respective provider's model list
4. [ ] Confirm auth keys are valid for EACH provider independently
5. [ ] If any check fails, report to user BEFORE starting delegation

## Quick probe commands

```bash
# Test nowcoding/gpt-5.5
curl -s -X POST https://nowcoding.ai/v1/chat/completions \
  -H "Authorization: Bearer $NOWCODING_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.5","messages":[{"role":"user","content":"Say OK"}],"max_tokens":5}'

# Test kimi-k2.6
curl -s -X POST https://api.kimi.com/coding/v1/chat/completions \
  -H "Authorization: Bearer $KIMI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"kimi-k2.6","messages":[{"role":"user","content":"Say OK"}],"max_tokens":5}'
```
