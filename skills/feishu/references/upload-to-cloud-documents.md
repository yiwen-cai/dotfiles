# Uploading Content to Feishu Cloud Documents

Workflow for uploading local content (study plans, notes, reports) to the user's personal Feishu/Lark cloud documents.

## Prerequisites

User-level OAuth **must** be active. Bot identity cannot create or write to personal documents.

## Step-by-Step Workflow

### 1. Check Current Identity
```bash
lark-cli doctor
lark-cli auth status
lark-cli config show
```

Look for:
- `strictMode` — if `"bot"`, user auth is blocked
- `users` — if `null` or empty, no user is logged in
- `identity` in error responses — bot operations fail for personal docs

### 2. If Strict Mode is "bot", Switch to User

**⚠️ AI agents must NOT modify strict mode directly.** Ask the user to run:

```bash
lark-cli config strict-mode off
```

Then login as user:
```bash
lark-cli auth login
```
This outputs a verification URL. The user must open it in a browser to complete OAuth.

### 3. Verify User Access
```bash
lark-cli doctor
lark-cli auth status
lark-cli docs +search --query "" --page-size 10 --as user
```

### 4. Create Folder (Optional)
```bash
lark-cli drive +create-folder --name "Folder Name"
```

### 5. Create Document
```bash
lark-cli docs +create --title "Document Title" --content "Initial content"
```

Or upload a file:
```bash
lark-cli drive +upload --file /path/to/file.md
```

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `strict_mode` error on login | `strictMode: "bot"` | User runs `lark-cli config strict-mode off` |
| `app secret invalid` (10014) | Secret mismatch or expired | Check `lark-cli config show`, verify app in Feishu console |
| Empty drive file list | Bot identity | Switch to user identity |
| `docs +search` fails with auth error | Using `--as bot` | Add `--as user` or ensure user is logged in |

## Session Example

From a real session (2026-05-06):

```
$ lark-cli doctor
"checks": [
  { "name": "token_exists", "status": "fail", "message": "no user logged in" },
  ...
]

$ lark-cli config show
{
  "appId": "cli_a97055dd287a9bc3",
  "strictMode": "bot",
  "users": "(no logged-in users)"
}

$ lark-cli auth login
{ "ok": false, "error": { "type": "strict_mode", "message": "strict mode is \"bot\"..." } }
```

Resolution: User manually ran `lark-cli config strict-mode off`, then `lark-cli auth login`, completed browser OAuth, and agent could then proceed with document operations.
