# Model Availability Probe Script

Quick probe to verify model endpoints before a subagent delegation session.

## Usage

Run this before ANY delegation session to confirm models are reachable.

```bash
# Probe nowcoding/gpt-5.5 (main agent)
curl -s -X POST https://nowcoding.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"model":"gpt-5.5","messages":[{"role":"user","content":"OK"}],"max_tokens":2}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ gpt-5.5 OK' if 'choices' in d else f'❌ gpt-5.5 FAIL: {d}')"

# Probe nowcoding/gpt-5.3-codex (fallback subagent)
curl -s -X POST https://nowcoding.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"model":"gpt-5.3-codex","messages":[{"role":"user","content":"OK"}],"max_tokens":2}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ gpt-5.3-codex OK' if 'choices' in d else f'❌ gpt-5.3-codex FAIL: {d}')"

# Probe kimi-k2.6 (preferred subagent — requires special headers, likely fails in Hermes)
curl -s -X POST https://api.kimi.com/coding/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "x-coding-agent: claude-code" \
  -H "User-Agent: claude-code/0.1" \
  -d '{"model":"kimi-k2.6","messages":[{"role":"user","content":"OK"}],"max_tokens":2}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ kimi-k2.6 OK' if 'choices' in d else f'❌ kimi-k2.6 FAIL: {d}')"
```

## Known Provider Quirks

### nowcoding.ai
- Standard OpenAI-compatible endpoint: `https://nowcoding.ai/v1`
- Bearer token auth with `sk-` prefix key
- All `gpt-5.*` models available EXCEPT `*-openai-compact` variants (ChatGPT account restriction)
- Key: `REMOVED_SECRET`

### kimi-coding (api.kimi.com/coding)
- **NOT standard OpenAI-compatible** — requires special headers:
  - `x-coding-agent: claude-code`
  - `User-Agent: claude-code/0.1`
- Without these headers: `access_terminated_error`
- Hermes `delegate_task` does NOT send these headers, so **unavailable for subagent use**
- Key: `REMOVED_SECRET`
- Actual returned model name: `kimi-for-coding`

## Fallback Priority (when preferred models fail)

1. `nowcoding/gpt-5.3-codex` — user's preferred fallback
2. `nowcoding/gpt-5.5` — same as main agent (acceptable if no alternative)
3. `nowcoding/gpt-5.4` / `gpt-5.4-mini`
4. `nowcoding/gpt-5.2`
