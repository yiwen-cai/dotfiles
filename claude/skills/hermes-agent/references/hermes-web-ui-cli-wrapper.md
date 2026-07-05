# Hermes Web UI CLI wrapper and ctl.sh lifecycle commands

Use this when a user wants a global command such as `hermes-ui` for a local Hermes WebUI checkout.

## Recommended architecture

Keep lifecycle logic in the project-local `ctl.sh`. Add only a thin wrapper for the global command:

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
CTL="${REPO_ROOT}/ctl.sh"

cmd="${1:-help}"
case "${cmd}" in
  -h|--help|help)
    # print wrapper help
    ;;
  start|stop|restart|status|update|logs)
    exec "${CTL}" "$@"
    ;;
  *)
    echo "[hermes-ui] Unknown command: ${cmd}" >&2
    exit 2
    ;;
esac
```

The symlink-resolution loop matters. Without it, running the wrapper through `~/.local/bin/hermes-ui -> /path/to/repo/scripts/hermes-ui` makes `${BASH_SOURCE[0]}` look like `~/.local/bin/hermes-ui`, causing `REPO_ROOT` to resolve incorrectly as `~/.local`.

## Exposing the command

Prefer a symlink into an existing PATH directory without modifying shell profiles:

```bash
mkdir -p "$HOME/.local/bin"
ln -sf "/absolute/path/to/hermes-webui/scripts/hermes-ui" "$HOME/.local/bin/hermes-ui"
command -v hermes-ui
```

If `~/.local/bin` is not in PATH, tell the user to add it manually. Shell profile files are commonly protected from agent writes.

## ctl.sh update command pattern

If `ctl.sh` lacks `update`, implement it in `ctl.sh` rather than duplicating update logic in the wrapper:

- Verify the repo is a git checkout.
- If the daemon is running, read saved host/port and query `/health`.
- Refuse to update when `/health` reports `active_streams > 0`.
- Refuse on a dirty working tree unless an explicit `--force` is provided.
- Default to `git fetch --prune` plus `git pull --ff-only`.
- For `--force`, reset to the upstream branch only after verifying an upstream exists.
- If the daemon was running before update, restart it unless `--no-restart` was passed.
- If the daemon was stopped, update only; do not auto-start.

## ctl.sh .env pitfall

When `ctl.sh` sources a repo `.env`, filter Bash readonly variables before sourcing:

```bash
source <(grep -vE '^[[:space:]]*(export[[:space:]]+)?(UID|GID|EUID|EGID|PPID)=' "${env_file}")
```

Also skip those keys when preserving caller environment overrides. This avoids crashes when `.env` contains Docker-oriented lines like `UID=501` or `GID=20`.

## Manual update when the checkout is dirty or divergent

If `ctl.sh update` refuses because the working tree has local changes, do not tell the user to paste file contents or claim files are inaccessible when a workspace is attached. Use file/terminal tools directly. For a user-owned local checkout where local customizations should be preserved, prefer this safe sequence instead of `--force`:

```bash
# Inspect first; note active streams before deciding whether to restart.
./ctl.sh status
git status --short --branch
git log --oneline --decorate --graph --left-right --cherry-pick HEAD...@{u} | head -120

# Preserve the exact pre-update state and local edits.
backup_branch="backup/webui-pre-update-$(date +%Y%m%d-%H%M%S)"
git branch "$backup_branch"
git stash push -u -m "pre-webui-update-$(date +%Y%m%d-%H%M%S)"

# If the branch is divergent, `git pull --ff-only` will fail; rebase the local commit(s)
# onto upstream, then restore the stashed edits.
git pull --rebase
git stash pop
```

Afterwards verify syntax and whitespace, then check status:

```bash
bash -n ctl.sh
[ ! -f scripts/hermes-ui ] || bash -n scripts/hermes-ui
node --check static/ui.js
node --check static/messages.js
node --check static/sessions.js
node --check static/terminal.js
node --check static/i18n.js
git diff --check
./ctl.sh status
```

If `./ctl.sh status` reports `active_streams > 0`, do not restart automatically; report that the checkout was updated and leave the running daemon untouched unless the user explicitly asks to interrupt/restart.

## Verification

Run cheap checks before reporting success:

```bash
bash -n ctl.sh
bash -n scripts/hermes-ui
command -v hermes-ui
hermes-ui help
hermes-ui status
hermes-ui update --help
```

If Python/pytest is unavailable, do not encode that as a durable limitation; report only that full tests were not run in the current environment.
