# Feishu Error 10014: App Secret Invalid — Reproduction & Resolution

## Symptom

`lark-cli` commands fail with:

```json
{
  "ok": false,
  "error": {
    "type": "api_error",
    "message": "API call failed: TAT API error: [10014] app secret invalid"
  }
}
```

## Context

- `lark-cli doctor` shows `token_exists: fail` with hint `no user logged in`.
- `lark-cli config show` reveals `strictMode: "bot"`.
- The app secret is stored in the macOS keychain (`security find-generic-password -s "lark-cli"`), not in plaintext.
- The profile is the only one (`cli_a97055dd287a9bc3`) and is bound to the `hermes` workspace.

## Root Cause

Error 10014 means the app secret used to request a tenant access token is rejected by the Feishu server. This can happen when:

1. The app secret was **rotated or revoked** in the Feishu Developer Console.
2. The app was **deleted or disabled**.
3. The keychain entry is **corrupted or stale** (e.g., after a macOS migration or keychain reset).
4. The app is configured for a **different region/brand** (Feishu vs Lark) than the endpoint being hit.

## What Does NOT Work

- `lark-cli auth login` — blocked by `strictMode: "bot"`.
- `lark-cli auth login --profile <name>` — same strict-mode block.
- Re-running `lark-cli config bind --source hermes` — the env vars may be stale, and the `.env` file is write-protected from agent tools.

## Resolution Path

### Step 1: Verify the app in the Feishu Developer Console

1. Go to https://open.feishu.cn/app/cli_a97055dd287a9bc3/auth (replace with your actual app ID).
2. Log in with the Feishu account that owns the app.
3. Check:
   - Is the app status "Active"?
   - Is the app secret the same as what's in the keychain?
   - Are the required scopes enabled?

### Step 2: If the secret was rotated, update it

Since `.env` is write-protected and the keychain is opaque, the user must do this manually:

```bash
# Option A: Re-initialize lark-cli with the new secret
lark-cli config init --new
# Then follow the device-flow URL to re-authenticate.

# Option B: If you have the new secret, add it to .env manually
echo 'FEISHU_APP_SECRET=your-new-secret' >> ~/.hermes/.env
# Then re-bind:
lark-cli config bind --source hermes
```

### Step 3: If user-level access is needed (for personal docs)

Bot identity cannot access personal drive documents. You **must** switch off strict mode and use user OAuth:

```bash
# User must run this themselves (agent cannot modify strict mode)
lark-cli config strict-mode off
lark-cli auth login
# Open the verification URL in a browser.
```

## Prevention

- Document the Feishu app ID and secret in a password manager, not just the macOS keychain.
- If the app is shared across multiple integrations (Hermes bot, lark-cli user, home channel), rotate the secret proactively when any integration is decommissioned.

## Related

- `references/bot-vs-user-document-access.md` — Why bot identity returns 0 files.
- `references/decommissioning.md` — Full cleanup of Feishu integration.
