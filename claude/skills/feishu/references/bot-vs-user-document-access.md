# Bot vs User Document Access

## Symptom
User asks to "view my cloud documents" / "查看我的云文档". You try `lark-cli docs +search` or the REST API `GET /drive/v1/files`. Both return data, but you get **0 files** even though the user clearly has documents.

## Root Cause
There are **two layers** of document access in Feishu:

| Identity | Sees | Typical Result |
|----------|------|----------------|
| **Bot** (tenant token) | App's own drive folder | **0 files** (app's drive is almost always empty) |
| **User** (OAuth token) | User's personal documents (我的空间, shared spaces) | **Actual documents** |

The `docs +search` command **only supports `--as user`** — `--as bot` produces an error.

## Resolution Flow

### 1. Check current auth status
```bash
lark-cli doctor
lark-cli auth status
```

### 2. If user identity not configured:
```bash
# Install if not present
npm install -g @larksuite/cli

# First-time config
lark-cli config init --new
# → Outputs a verification URL, share with user
# → Command blocks until user completes browser flow

# Then login
lark-cli auth login
# → Another verification URL, share with user
```

### 3. Verify user access works
```bash
lark-cli docs +search --query "" --page-size 10 --format pretty --as user
```

## Session Reproduction (2026-05-06)
- App ID: `cli_a97055dd287a9bc3`
- Initial scopes: only `offline_access`
- Added scopes via Developer Console: `drive:drive`, `drive:drive:readonly`, `space:document:retrieve`
- After adding scopes: `GET /drive/v1/files` returned `code: 0, files: []` (0 files — app drive is empty)
- `docs +search` rejected `--as bot` with: `Error: --as bot is not supported, this command only supports: user`
- `--as user` failed with: `not configured` — user identity had never been set up
- Resolution started: installed lark-cli, ran `config init --new`, got verification URL
