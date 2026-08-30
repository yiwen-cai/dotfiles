# Hermes Web UI mutation surfaces

Use this when auditing or explaining whether `EKKOLearnAI/hermes-web-ui` can modify a Hermes workspace/home/profile.

## Key distinction

In this repository, "workspace" can mean two different things:

- Hermes home/profile directory: `~/.hermes/` or `~/.hermes/profiles/<name>/`.
- Session workspace metadata: a project path stored on a chat/session row.

The Web UI does modify the Hermes home/profile directory. It does not appear to automatically edit a session-bound project directory, but its terminal feature gives an authenticated user a shell with the same filesystem permissions as the Web UI process.

## Repository paths audited

- `packages/server/src/services/hermes/hermes-profile.ts`
  - Resolves active profile paths from `HERMES_HOME || ~/.hermes` and `active_profile`.
  - Exposes `getActiveProfileDir()`, `getActiveConfigPath()`, `getActiveEnvPath()`, `getActiveAuthPath()`.
- `packages/server/src/controllers/hermes/config.ts`
  - Reads/writes active profile `config.yaml`.
  - Backs up to `config.yaml.bak` before writing.
  - Saves platform credentials into `.env` via `saveEnvValue()`.
- `packages/server/src/services/config-helpers.ts`
  - `writeConfigYaml()` overwrites active profile `config.yaml`.
  - `saveEnvValue()` overwrites active profile `.env` and chmods `0600`.
- `packages/server/src/controllers/hermes/providers.ts`
  - Creates/updates/removes custom and built-in providers in `config.yaml`, `.env`, and sometimes `auth.json`.
  - Restarts the gateway after provider changes.
- `packages/server/src/controllers/hermes/codex-auth.ts`
  - Writes active profile `auth.json` for OpenAI Codex auth.
- `packages/server/src/controllers/hermes/nous-auth.ts`
  - Writes active profile `auth.json` for Nous auth.
- `packages/server/src/controllers/hermes/weixin.ts`
  - Writes Weixin credentials into active profile `.env`.
- `packages/server/src/controllers/hermes/memory.ts`
  - Writes active profile `memories/MEMORY.md`, `memories/USER.md`, and `SOUL.md`.
- `packages/server/src/controllers/hermes/profiles.ts`
  - Wraps `hermes profile create/delete/rename/use/import/export`.
  - On cloned profile creation, `smartCloneCleanup()` edits the new profile's `.env` and `config.yaml` to strip exclusive platform credentials.
  - On profile switch, may create a missing profile `.env` and may run `hermes setup reset` if `config.yaml` is missing.
- `packages/server/src/controllers/hermes/sessions.ts`
  - Wraps `hermes sessions delete/rename` when not using local session store.
  - In local session store mode, `setWorkspace()` writes only a `workspace` metadata column in the Web UI DB and creates a session row if missing.
- `packages/server/src/routes/hermes/files.ts`
  - File manager rooted at active profile directory via `resolveHermesPath()`.
  - Supports read/list/stat/write/delete/rename/mkdir/copy/upload.
- `packages/server/src/services/hermes/file-provider.ts`
  - `resolveHermesPath()` maps relative paths under `getActiveProfileDir()`.
  - Sensitive write/delete/rename protection only blocks basenames `.env` and `auth.json`.
  - `config.yaml`, `SOUL.md`, `memories/*`, `skills/*`, etc. are not protected by that sensitive-file set.
- `packages/server/src/routes/hermes/terminal.ts`
  - Spawns a shell with `cwd: process.env.HOME || undefined`.
  - An authenticated Web UI terminal user can manually modify any file accessible to the Web UI process.
- `docker-compose.yml`
  - Mounts `${HERMES_DATA_DIR:-./hermes_data}` to `/home/agent/.hermes` and sets `HERMES_HOME=/home/agent/.hermes`.

## Practical answer template

Short answer: yes, if by Hermes workspace you mean Hermes home/profile data. The Web UI can modify `config.yaml`, `.env`, `auth.json`, memory/user/soul files, profiles, sessions, and arbitrary files under the active profile directory through its file manager, except direct file-manager writes/deletes/renames to `.env` and `auth.json` are blocked by basename. It can still update those files through dedicated settings/auth/provider routes.

If the user means a project workspace path attached to a session, the code stores that as session metadata. No automatic project-file mutation path was found, but the integrated terminal can modify any filesystem path the Web UI process can access.

## Pitfalls

- Do not answer from memory for repo questions. Clone or inspect the current repo state and cite exact files/functions.
- Search broadly for `writeFile`, `copyFile`, `mkdir`, `rename`, `rm`, `execFile`, `pty.spawn`, `.hermes`, `config.yaml`, `.env`, `auth.json`, `workspace`.
- Clarify the two meanings of "workspace" without blocking on a question: answer both by default.
- For security analysis, include the Web Terminal as a mutation surface even if no automated code path edits a project directory.
