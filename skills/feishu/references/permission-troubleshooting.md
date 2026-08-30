# Hermes-Bound Feishu App: Permission Troubleshooting

## Context
The user's Feishu environment has `FEISHU_APP_ID` / `FEISHU_APP_SECRET` set in env vars.
After running `lark-cli config bind --source hermes`, the app could authenticate as bot
but had insufficient scopes for document operations.

## App Details
- **App ID**: `cli_a9705f9286389bd3`
- **Brand**: feishu
- **Domain**: feishu.cn
- **Bound via**: `lark-cli config bind --source hermes`
- **Strict mode**: `bot` (prevents user login)

## Permission Flow (from the session)

1. **Check scopes** → `lark-cli auth scopes` showed only `offline_access`
2. **Try document search** → failed with error code `99991672`
3. **Error details**:
   ```
   Required scopes: [drive:drive, drive:drive:readonly, space:document:retrieve]
   Permission_violations: drive:drive, drive:drive:readonly, space:document:retrieve
   ```
4. **Error provided a direct link** to the app's auth page:
   ```
   https://open.feishu.cn/app/cli_a9705f9286389bd3/auth?q=drive:drive,drive:drive:readonly,space:document:retrieve
   ```
5. **Login required** — the auth page redirects to Feishu login (QR code scan).
   The user must manually log in to enable permissions.

## Second App (User-Logged-In)
A second Feishu app existed in the original `~/.lark-cli/config.json`:
- **App ID**: `cli_a9707acd2cb85bc1`
- **User**: OpenID `ou_b87d26d46f935ee0767ce39129c6931c` ("用户276881")
- **Secret**: Stored in macOS keychain under service `lark-cli`, account `master.key`
- **Not bound to Hermes** — only the original app was bound

## Key Takeaway
The `FEISHU_APP_ID`/`FEISHU_APP_SECRET` in env vars were configured for a bot-only app
(probably for the Feishu messaging platform integration). To access documents,
either (a) add `drive:drive:readonly` scope to this app in the Feishu Developer Console,
or (b) use a different app that already has these permissions and a logged-in user.
