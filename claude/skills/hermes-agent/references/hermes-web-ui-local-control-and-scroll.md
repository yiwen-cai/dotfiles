# Hermes Web UI local control and scroll behavior notes

Use this reference when modifying the community `EKKOLearnAI/hermes-web-ui` checkout or similar local Hermes WebUI deployments.

## Global `hermes-ui` command pattern

Preferred shape:

- Keep lifecycle logic in the repo-local `ctl.sh`.
- Add a thin wrapper such as `scripts/hermes-ui` that resolves its real path through symlinks and then `exec`s `<repo>/ctl.sh "$@"`.
- Expose it via a symlink in an existing PATH directory, commonly `~/.local/bin/hermes-ui`.
- Do not auto-edit `~/.zshrc`, `~/.bashrc`, or `~/.bash_profile`; these shell profile files may be protected. If `~/.local/bin` is not in PATH, tell the user the manual command to add it.

Wrapper must resolve symlinks before computing repo root. A naive `dirname "${BASH_SOURCE[0]}"/..` breaks when invoked through `~/.local/bin/hermes-ui` and tries to find `~/.local/ctl.sh`.

Sketch:

```bash
#!/usr/bin/env bash
set -euo pipefail

SOURCE="${BASH_SOURCE[0]}"
while [[ -L "${SOURCE}" ]]; do
  DIR="$(cd -P "$(dirname "${SOURCE}")" && pwd)"
  TARGET="$(readlink "${SOURCE}")"
  if [[ "${TARGET}" == /* ]]; then
    SOURCE="${TARGET}"
  else
    SOURCE="${DIR}/${TARGET}"
  fi
done
SCRIPT_DIR="$(cd -P "$(dirname "${SOURCE}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
exec "${REPO_ROOT}/ctl.sh" "$@"
```

Useful command set: `start`, `status`, `restart`, `stop`, `update`, `logs`, `help`.

## `ctl.sh` pitfalls

When `ctl.sh` sources repo `.env`, filter Bash readonly variables before `source`ing:

- `UID`
- `GID`
- `EUID`
- `EGID`
- `PPID`

Docker-oriented `.env` files commonly contain `UID=$(id -u)` / `GID=$(id -g)`. Bash treats some of these names as readonly, so local `ctl.sh start` can fail unless they are filtered. Keep external environment values taking precedence over `.env` values.

For `update`, prefer conservative behavior:

1. Refuse if not in a git checkout.
2. If daemon is running, call `/health` and refuse when active streams are present.
3. Refuse dirty trees unless the user explicitly passes `--force`.
4. Default to `git fetch --prune` + `git pull --ff-only`.
5. If it was running before update, restart after update unless `--no-restart` is passed.

## Disabling automatic transcript scrolling

User preference for this project: the main chat transcript should not auto-scroll on send, streaming output, completion, DOM rerender, or layout changes. The user should control scroll manually, with explicit top/bottom buttons.

**Important exception:** when opening or switching to an already-existing idle session, the initial render should land at the bottom of the loaded conversation. This is a navigation default, not live auto-follow. In `static/sessions.js`, the idle-session load branch can do:

```js
syncTopbar();renderMessages();scrollToBottom();
```

Do not reintroduce auto-follow elsewhere: keep send, token streaming, completion, dock/layout changes, and ordinary rerenders from calling `scrollToBottom()` automatically.

Primary files and hooks:

- `static/ui.js`
  - `scrollIfPinned()` can be made a no-op to disable streaming/tool/thinking auto-follow while preserving manual `scrollToBottom()`.
  - `_scrollAfterMessageRender()` should not default to `scrollToBottom()`; it should only restore snapshots when explicitly preserving scroll.
  - Leave `scrollToBottom()` and `jumpToSessionStart()` intact for explicit button clicks.
- `static/messages.js`
  - Remove done-handler auto `scrollToBottom()` after `renderMessages({preserveScroll:true})`.
  - Remove `/btw` `scrollIntoView({behavior:'smooth', block:'end'})`.
- `static/terminal.js`
  - Remove terminal dock open/close layout calls to `scrollToBottom()`.
- `static/sessions.js`
  - Remove handoff dock show/hide layout calls to `scrollToBottom()`.
  - Keep the idle-session initial render default at the bottom by calling `scrollToBottom()` immediately after `renderMessages()` in the non-streaming session load path.
- `static/index.html` / `static/style.css`
  - For always-visible Start/End controls, keep the buttons outside `.messages` scroll content and position them as a `#mainChat` / `.main-view` overlay; see `references/hermes-web-ui-scroll-buttons.md` for the DOM/CSS pattern and sticky/absolute pitfalls.

Verification:

```bash
node --check static/ui.js
node --check static/messages.js
node --check static/terminal.js
node --check static/sessions.js
```

Manual behavior check:

1. Open a long historical/idle session; viewport should start at the bottom.
2. Scroll to the middle.
3. Send a message; viewport should not move.
4. Let streaming output run; viewport should not follow tokens.
5. Wait for completion; viewport should not jump.
6. Click the bottom button; it should scroll down.
7. Click the top button; it should scroll up.
