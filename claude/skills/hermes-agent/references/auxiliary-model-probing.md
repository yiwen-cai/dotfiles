# Auxiliary model probing notes

Session signal: auxiliary tasks were configured with `provider: auto` and `model: kimi-k2.6`, while the main provider was `nowcoding` and its configured model list did not include `kimi-k2.6`.

Observed failure

```text
InternalServerError: Error code: 503 - {'error': {'code': 'model_not_found', 'message': 'No available channel for model kimi-k2.6 under group Codex Pro (distributor) ...', 'type': 'new_api_error'}}
```

Interpretation

- In `provider: auto`, an explicit auxiliary `model` can still be attempted against the resolved/main provider.
- If that provider does not expose the auxiliary model, the request can fail with provider-specific `model_not_found` instead of cleanly falling back.
- For nowcoding, verify the provider's configured/served model list before setting auxiliary models. Known configured models in this session were `gpt-5.5`, `gpt-5.5-openai-compact`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.3-codex`, `gpt-5.2`.

Minimal live probe

Run from the Hermes source checkout so imports resolve:

```bash
cd "$HOME/.hermes/hermes-agent"
if [ -d .venv ]; then . .venv/bin/activate; elif [ -d venv ]; then . venv/bin/activate; elif [ -d "$HOME/.hermes/hermes-agent/venv" ]; then . "$HOME/.hermes/hermes-agent/venv/bin/activate"; fi
python3 - <<'PY'
from agent.auxiliary_client import call_llm

for task in ["compression", "session_search", "title_generation", "approval"]:
    print(f"## TASK {task}")
    try:
        resp = call_llm(
            task=task,
            messages=[{"role": "user", "content": "Reply with exactly OK."}],
            max_tokens=8,
            timeout=60,
        )
        print("SUCCESS")
        print("CONTENT=" + repr(resp.choices[0].message.content))
        print("MODEL=" + repr(getattr(resp, "model", None)))
    except Exception as e:
        print("ERROR")
        print(type(e).__name__ + ": " + str(e)[:2000])
PY
```

Fix pattern

- If using `provider: auto`, set each auxiliary task model to one the resolved/main provider actually serves, for example `gpt-5.3-codex` under nowcoding.
- If using a Kimi model, configure an explicit Kimi-compatible auxiliary provider and verify its auth and endpoint independently. Kimi coding endpoints may require provider-specific headers in raw HTTP probes.
