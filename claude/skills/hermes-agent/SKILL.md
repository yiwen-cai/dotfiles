---
name: hermes-agent
description: "Configure, extend, or contribute to Hermes Agent."
version: 2.2.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively** — setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill (ID can be a hub identifier OR a direct https://…/SKILL.md URL; pass --name to override when frontmatter has no name)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks. Open WebUI connects via the API Server adapter.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### Cron Jobs

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

**Attaching files in cron deliveries:** To send a local file (e.g. HTML, PDF) as an attachment via a cron job, the script or agent response must include `MEDIA:/absolute/path/to/file` on its own line. The gateway parses this and sends the file through the platform adapter (e.g. Weixin). Example script output:
```
Your daily briefing text here.

MEDIA:/Users/you/project/output/2026-05-11.html
```

**Pitfall — agent-mode cron may not emit MEDIA:** When `no_agent=False` (default), the LLM must be explicitly instructed in the prompt to include the `MEDIA:` line. Even then, the model may forget or place it incorrectly. For reliable file delivery, prefer `no_agent=True` with a script that deterministically prints the `MEDIA:` line.

**Pitfall — Weixin rate limiting:** The Weixin gateway adapter (`ilinkai.weixin.qq.com`) enforces strict rate limits. If you trigger a cron job multiple times in quick succession, subsequent deliveries will fail with `iLink sendmessage rate limited: ret=-2`. Wait several minutes between manual triggers. The standalone fallback also retries with backoff, but may still fail under heavy load.

**Pitfall — last_status=ok does not mean delivery succeeded:** Check `last_delivery_error` separately. A job can show `last_status: ok` (the agent/script ran without crashing) while `last_delivery_error` contains a gateway error like `Cannot connect to host ilinkai.weixin.qq.com:443` or `rate limited`.

**Recommended pattern for file-delivering cron jobs:**
1. Set `no_agent=True` on the job.
2. Provide a `script` path relative to `workdir`.
3. The script prints the message body, then `MEDIA:/absolute/path`.
4. The script handles its own data collection, rendering, and error reporting.
5. Keep the script idempotent — it should work whether run by cron or manually.

**Cron job with no_agent=True example:**
```python
#!/usr/bin/env python3
# scripts/daily_briefing.py — runs inside workdir
import sys, subprocess, datetime as dt
from pathlib import Path

# 1. Collect data
subprocess.run([sys.executable, "scripts/collect.py"], check=True)

# 2. Render HTML
subprocess.run([sys.executable, "scripts/render.py"], check=True)

# 3. Output for Hermes delivery
html_path = Path("output") / f"{dt.date.today().isoformat()}.html"
print("Your briefing text here.")
print("")
print(f"MEDIA:{html_path.resolve()}")
```

Then create the job:
```bash
hermes cron create "0 9 * * *" \
  --name "Daily Briefing" \
  --script scripts/daily_briefing.py \
  --workdir /path/to/project \
  --no-agent \
  --deliver origin
```

See `references/aihot-morning-briefing-cron.md` for a real-world AIHOT morning briefing variant that sends to Weixin and uses a deterministic `MEDIA:` output line.

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session. New commands land fairly
often; if something below looks stale, run `/help` in-session for the
authoritative list or see the [live slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands).
The registry of record is `hermes_cli/commands.py` — every consumer
(autocomplete, Telegram menu, Slack mapping, `/help`) derives from it.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/snapshot [sub]      Create or restore state snapshots of Hermes config/state (CLI)
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/steer <prompt>      Inject a message after the next tool call without interrupting
/agents (/tasks)     Show active agents and running tasks
/resume [name]       Resume a named session
/goal [text|sub]     Set a standing goal Hermes works on across turns until achieved
                     (subcommands: status, pause, resume, clear)
/redraw              Force a full UI repaint (CLI)
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/busy [sub]          Control what Enter does while Hermes is working (CLI)
                     (subcommands: queue, steer, interrupt, status)
/indicator [style]   Pick the TUI busy-indicator style (CLI)
                     (styles: kaomoji, emoji, unicode, ascii)
/footer [on|off]     Toggle gateway runtime-metadata footer on final replies
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/reload-skills       Re-scan ~/.hermes/skills/ for added/removed skills
/reload              Reload .env variables into the running session (CLI)
/reload-mcp          Reload MCP servers
/cron                Manage cron jobs (CLI)
/curator [sub]       Background skill maintenance (status, run, pin, archive, …)
/kanban [sub]        Multi-profile collaboration board (tasks, links, comments)
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/topic [sub]         Enable or inspect Telegram DM topic sessions (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/copy [N]            Copy the last assistant response to clipboard (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/gquota              Show Google Gemini Code Assist quota usage (CLI)
/status              Session info (gateway)
/profile             Active profile info
/debug               Upload debug report (system info + logs) and get shareable links
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

Memory maintenance for this user: see `references/layered-memory-maintenance.md` for the layered policy — memory stores global/local indexes and stable facts, while concrete workflows belong in skills.

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Adding Custom OpenAI-Compatible Providers

For any service that exposes an OpenAI-compatible API endpoint (vLLM, Ollama, LM Studio, Together AI, Fireworks, Groq, or private deployments), use the `providers` dict in config.yaml (v12+ format).

**Recommended format — `providers` dict:**

```yaml
providers:
  my-provider:                     # unique name, shown in /model picker
    base_url: https://api.example.com/v1
    api_key: "sk-your-key"         # or use key_env for env-var reference:
    # key_env: MY_PROVIDER_API_KEY #  ← alternative: read from env var
    models:
      - model-name-1
      - model-name-2
      - model-name-3
    # Optional fields:
    # context_length: 128000       # override context window
    # api_mode: chat_completions   # defaults to chat_completions
    # rate_limit_delay: 1.0        # seconds between requests
```

**Legacy format — `custom_providers` list (older Hermes versions):**

```yaml
custom_providers:
  - name: my-provider
    base_url: https://api.example.com/v1
    api_key: "sk-your-key"
    models:
      - model-name-1
```

**Full normalized field reference** (both formats accept these):

| Field | Aliases | Description |
|-------|---------|-------------|
| `name` | — | Provider name (shown in `/model` picker). Required for legacy list format; for dict format the dict key is the name. |
| `base_url` | `url`, `api` | OpenAI-compatible endpoint URL (required, must have scheme+host) |
| `api_key` | — | Inline API key string |
| `key_env` | `api_key_env`, `apiKeyEnv` | Env var name holding the API key (prefer this over inline `api_key` for security) |
| `models` | — | List of model IDs available from this endpoint (e.g. `["gpt-5.5", "claude-4"]`) |
| `context_length` | `contextLength` | Max context window in tokens |
| `api_mode` | `transport` | API mode: `chat_completions` (default), `responses`, `codex_responses`, etc. |
| `rate_limit_delay` | `rateLimitDelay` | Delay between requests in seconds |

**Switching to a custom provider:**

- **Interactive:** `hermes model` → pick your provider from the list → pick a model
- **In-session:** `/model` → pick provider → pick model
- **One-shot:** `hermes --provider my-provider --model model-name`
- **Default swap:** `hermes config set model.provider my-provider && hermes config set model.default model-name`

**Verification after changing the default model:**

Prefer verifying the exact config file instead of piping `hermes config` through PyYAML; user environments may not have the `yaml` Python package installed.

```bash
hermes config path
hermes config set model.provider nowcoding
hermes config set model.default nowcoding/gpt-5.5

# Verify with tools that do not require PyYAML:
grep -n "^model:" -A5 "$(hermes config path)"
# Expected for nowcoding/gpt-5.5:
#   default: nowcoding/gpt-5.5
#   provider: nowcoding
```

When reporting the result to the user, keep it brief and explicitly mention that a running CLI session may need `/model`, `/reset`, or a new Hermes process before the new default is used.

**Pitfall: .env write protection**

API keys stored as `key_env` references are safer than inline `api_key`, but the `.env` file is protected from agent tool writes (guardrails block both `patch` and terminal commands like `echo >>`). If the agent suggests adding a key to `.env`, the user must run the command themselves:

```bash
echo 'MY_PROVIDER_API_KEY=sk-your-key' >> ~/.hermes/.env
```

As a fallback, the agent CAN write the API key directly into `config.yaml`'s `providers` section using `api_key`, since `config.yaml` is writable via `patch`.

### Testing a custom endpoint:

```bash
# Check if endpoint is reachable
curl -s -o /dev/null -w "%{http_code}" https://your-endpoint/v1

# List available models
curl -s https://your-endpoint/v1/models -H "Authorization: Bearer $API_KEY" | python3 -m json.tool

# Quick chat completion test
curl -s https://your-endpoint/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"model-name","messages":[{"role":"user","content":"hello"}]}'
```

### Probing model availability before delegation:

When the user has specified a model assignment policy (e.g., "use nowcoding/gpt-5.5 as main agent, kimi-k2.6 as subagent"), verify both models are reachable **before** starting delegation:

```bash
# 1. Check provider endpoint health
curl -s -o /dev/null -w "%{http_code}" https://nowcoding.ai/v1/models -H "Authorization: Bearer $KEY"
curl -s -o /dev/null -w "%{http_code}" https://api.kimi.com/coding/v1/models -H "Authorization: Bearer $KEY"

# 2. Verify the specific model exists in the provider's model list
curl -s https://nowcoding.ai/v1/models -H "Authorization: Bearer $KEY" | grep "gpt-5.5"
curl -s https://api.kimi.com/coding/v1/models -H "Authorization: Bearer $KEY" | grep "kimi-k2.6"

# 3. Test a minimal chat completion to confirm auth + model work
curl -s https://nowcoding.ai/v1/chat/completions \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.5","messages":[{"role":"user","content":"Say OK"}],"max_tokens":5}'

curl -s https://api.kimi.com/coding/v1/chat/completions \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"kimi-k2.6","messages":[{"role":"user","content":"Say OK"}],"max_tokens":5}'
```

**Key insight from real session:** A single API key may work for one provider but fail for another. The nowcoding key (`REMOVED_SECRET`) worked for `nowcoding.ai` but returned `invalid_authentication_error` for `api.kimi.com/coding`. Each provider requires its own valid key — verify independently.

## Real-world example: See `references/nowcoding-provider.md` for a complete working config (nowcoding.ai with gpt-5.5 models).

## Hermes Web UI CLI wrapper: See `references/hermes-web-ui-cli-wrapper.md` for creating a global `hermes-ui` command backed by project-local `ctl.sh`, including symlink-safe wrapper path resolution, `ctl.sh update` semantics, `.env` readonly-variable filtering, and verification commands.

## Hermes Web UI local control and scroll behavior: See `references/hermes-web-ui-local-control-and-scroll.md` for the local `hermes-ui` wrapper pattern, `ctl.sh` lifecycle/update pitfalls, and the user's preferred no-auto-scroll transcript behavior with explicit top/bottom buttons.

## Desktop/TUI timeout diagnosis: See `references/desktop-tui-timeout-diagnosis.md` for diagnosing `request timed out: prompt.submit` errors, including the 30-second desktop default timeout, TUI environment variable override, API provider slowness detection, and the three fixes (rebuild desktop with 120s timeout, set `HERMES_TUI_RPC_TIMEOUT_MS`, or address provider issues).

## Hermes Web UI proxy diagnosis: See `references/hermes-web-ui-proxy-diagnosis.md` for checking whether a local proxy port (e.g. 7897) prevents timeouts, distinguishing successful `curl -x` probes from WebUI process env injection, and safely restarting only when no active streams are running.

## Hermes Web UI scroll button placement: See `references/hermes-web-ui-scroll-buttons.md` for the preferred Start/End button layout, including the sticky-overlap pitfall when both buttons are early children of `.messages`, and the absolute-positioned top/bottom overlay pattern.

## Hermes Web UI 8787 shell fallback: See `references/hermes-web-ui-8787-shell-fallback.md` for diagnosing the `Hermes is restarting… The WebUI shell could not load cleanly` fallback on port 8787, including stale daemon paths, health-vs-shell mismatch, and `ctl.sh` shell compatibility pitfalls.

## Hermes Web UI mutation audit: See `references/hermes-web-ui-mutation-surfaces.md` for the audited write surfaces in `EKKOLearnAI/hermes-web-ui` (config/env/auth/memory/profile/session/file-manager/terminal) and how to explain "workspace" ambiguity.

## Hermes Web UI options: See `references/hermes-web-ui-options.md` for current Web UI choices: official `hermes dashboard`, Open WebUI via Hermes API Server, community `EKKOLearnAI/hermes-web-ui`, and other OpenAI-compatible frontends.

## macOS terminal choice for Hermes CLI: See `references/macos-terminal-choice.md` for the current recommendation: iTerm2 as the default, Ghostty as the modern high-performance alternative, WezTerm for power users, and Warp only when the user explicitly wants Warp/Oz agentic terminal features.

## Migrating kitty terminal config to iTerm2: See `references/kitty-to-iterm2-migration.md` for the concrete workflow used to convert kitty fonts, Catppuccin colors, Option-as-Alt, scrollback, mouse reporting, and selected keybindings into an iTerm2 Dynamic Profile JSON under `~/Library/Application Support/iTerm2/DynamicProfiles/`.

## Open WebUI local pip setup: See `references/open-webui-local-pip-hermes.md` for no-Docker Open WebUI setup with Hermes API Server, including live-port probing, `DATA_DIR=$HOME/.open-webui`, 8642-vs-8643 config pitfalls, and first-run Alembic migration waits.

## Curating large agent bundles: See `references/curating-large-agent-bundles.md` for the allowlist approach used when an external repository ships hundreds of agents/skills and the user only wants production-relevant ones.

## Provider authentication pitfalls: See `references/provider-auth-pitfalls.md` for common auth issues when working with multiple providers — including the "one key for multiple providers" trap, config key vs env key confusion, and pre-delegation verification checklists.

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `search` | Web search only (subset of `web`) |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `video` | Video analysis and generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `todo` | In-session task planning and tracking |
| `kanban` | Multi-agent work-queue tools (gated to workers) |
| `debugging` | Extra introspection/debug tools (off by default) |
| `safe` | Minimal, low-risk toolset for locked-down sessions |
| `spotify` | Spotify playback and playlist control |
| `homeassistant` | Smart home control (off by default) |
| `discord` | Discord integration tools |
| `discord_admin` | Discord admin/moderation tools |
| `feishu_doc` | Feishu (Lark) document tools |
| `feishu_drive` | Feishu (Lark) drive tools |
| `yuanbao` | Yuanbao integration tools |
| `rl` | Reinforcement learning tools (off by default) |
| `moa` | Mixture of Agents (off by default) |

Full enumeration lives in `toolsets.py` as the `TOOLSETS` dict; `_HERMES_CORE_TOOLS` is the default bundle most platforms inherit from.

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Installing External Skills & Plugins From GitHub

Skills and plugins from external GitHub repos can be installed manually. This covers repos that ship a Hermes adapter (a `.hermes/` directory with both a skill and a project plugin).

### Skill Installation (2 methods)

**Method A — Skill hub install (simplest, when the skill is on the hub):**
```bash
hermes skills install <hub-id>
```

**Method B — Direct SKILL.md URL (repos with a Hermes adapter):**
```bash
hermes skills install https://raw.githubusercontent.com/OWNER/REPO/main/.hermes/skills/SKILL_NAME/SKILL.md --name SKILL_NAME
```

**Method C — External directory (repos with a full skill directory):**
```yaml
# ~/.hermes/config.yaml
skills:
  external_dirs:
    - /absolute/path/to/repo/.hermes/skills
```
The skill's SKILL.md lives at `repo/.hermes/skills/<name>/SKILL.md`. Hermes discovers it on next session. The repo must be at a stable persistent path (not `/tmp/`).

### Project Plugin Installation

If the repo includes a `.hermes/plugins/` directory with Python tool/hook files, copy it to the Hermes plugins directory:

```bash
cp -r REPO_PATH/.hermes/plugins/PLUGIN_NAME ~/.hermes/plugins/
```

This provides Hermes with custom tools, hooks, and lifecycle automation defined by the plugin.

### Enabling Project Plugins

Project plugins require an environment variable:

```bash
export HERMES_ENABLE_PROJECT_PLUGINS=1
```

Add this to `~/.zshrc` (or `~/.bashrc`) for persistence.

### Pitfall: Shell Profile Protection

**`.zshrc` / `.bashrc` / `.bash_profile` are protected from agent tool writes.** Guardrails block both `write_file`/`patch` and terminal-based modifications (echo, sed, etc.) on these files. The agent cannot add env vars like `HERMES_ENABLE_PROJECT_PLUGINS` automatically.

**Workaround:** The user must add the env var manually:

```bash
echo 'export HERMES_ENABLE_PROJECT_PLUGINS=1' >> ~/.zshrc && source ~/.zshrc
```

Tell the user clearly: "Shell profile is protected — please run this command yourself."

### Config File Modification

`~/.hermes/config.yaml` IS writable by the agent via `patch`. This is safe to edit programmatically for adding `skills.external_dirs`, changing providers, or other config values.

### Verification

After installation, verify the skill loads:
```bash
hermes skills list
```
And that the plugin is registered by checking for its custom tools in the tool listing (requires a fresh session after enabling project plugins).

### Pitfall: Community URL skills may be quarantined by security scan

When installing a direct community `SKILL.md` URL, Hermes may first quarantine the file and run a security scan. Some skills can be blocked with a `DANGEROUS` verdict for supply-chain-looking text (for example documentation mentioning `curl -fsSL ... | bash`) even when the actual skill is only a read-only API workflow. Do not blindly force-install. First fetch or inspect the `SKILL.md`, skim command fences for destructive commands (`rm`, `sudo`, `chmod`, eval/base64 pipelines, credential exfiltration), and confirm the workflow scope. If acceptable, install non-interactively with an explicit stable category:

```bash
hermes skills install https://example.com/path/SKILL.md \
  --name skill-name \
  --category research \
  --force \
  --yes
```

Verify both registry listing and actual loadability:
```bash
hermes skills list | grep -i skill-name
# In-agent/tool verification: skill_view(name="skill-name")
```

For skills that call public APIs, also run one minimal endpoint probe with the required headers from the skill before declaring the install complete.

---

## Security & Privacy Toggles

Common "why is Hermes doing X to my output / tool calls / commands?" toggles — and the exact commands to change them. Most of these need a fresh session (`/reset` in chat, or start a new `hermes` invocation) because they're read once at startup.

### Secret redaction in tool output

Secret redaction is **off by default** — tool output (terminal stdout, `read_file`, web content, subagent summaries, etc.) passes through unmodified. If the user wants Hermes to auto-mask strings that look like API keys, tokens, and secrets before they enter the conversation context and logs:

```bash
hermes config set security.redact_secrets true       # enable globally
```

**Restart required.** `security.redact_secrets` is snapshotted at import time — toggling it mid-session (e.g. via `export HERMES_REDACT_SECRETS=true` from a tool call) will NOT take effect for the running process. Tell the user to run `hermes config set security.redact_secrets true` in a terminal, then start a new session. This is deliberate — it prevents an LLM from flipping the toggle on itself mid-task.

Disable again with:
```bash
hermes config set security.redact_secrets false
```

### PII redaction in gateway messages

Separate from secret redaction. When enabled, the gateway hashes user IDs and strips phone numbers from the session context before it reaches the model:

```bash
hermes config set privacy.redact_pii true    # enable
hermes config set privacy.redact_pii false   # disable (default)
```

### Command approval prompts

By default (`approvals.mode: manual`), Hermes prompts the user before running shell commands flagged as destructive (`rm -rf`, `git reset --hard`, etc.). The modes are:

- `manual` — always prompt (default)
- `smart` — use an auxiliary LLM to auto-approve low-risk commands, prompt on high-risk
- `off` — skip all approval prompts (equivalent to `--yolo`)

```bash
hermes config set approvals.mode smart       # recommended middle ground
hermes config set approvals.mode off         # bypass everything (not recommended)
```

Per-invocation bypass without changing config:
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

Note: YOLO / `approvals.mode: off` does NOT turn off secret redaction. They are independent.

### Shell hooks allowlist

Some shell-hook integrations require explicit allowlisting before they fire. Managed via `~/.hermes/shell-hooks-allowlist.json` — prompted interactively the first time a hook wants to run.

### Disabling the web/browser/image-gen tools

To keep the model away from network or media tools entirely, open `hermes tools` and toggle per-platform. Takes effect on next session (`/reset`). See the Tools & Skills section above.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---

## Durable & Background Systems

Four systems run alongside the main conversation loop. Quick reference
here; full developer notes live in `AGENTS.md`, user-facing docs under
`website/docs/user-guide/features/`.

### Delegation (`delegate_task`)

Synchronous subagent spawn — the parent waits for the child's summary
before continuing its own loop. Isolated context + terminal session.

- **Single:** `delegate_task(goal, context, toolsets)`.
- **Batch:** `delegate_task(tasks=[{goal, ...}, ...])` runs children in
  parallel, capped by `delegation.max_concurrent_children` (default 3).
- **Roles:** `leaf` (default; cannot re-delegate) vs `orchestrator`
  (can spawn its own workers, bounded by `delegation.max_spawn_depth`).
- **Not durable.** If the parent is interrupted, the child is
  cancelled. For work that must outlive the turn, use `cronjob` or
  `terminal(background=True, notify_on_complete=True)`.

Config: `delegation.*` in `config.yaml`.

### Cron (scheduled jobs)

Durable scheduler — `cron/jobs.py` + `cron/scheduler.py`. Drive it via
the `cronjob` tool, the `hermes cron` CLI (`list`, `add`, `edit`,
`pause`, `resume`, `run`, `remove`), or the `/cron` slash command.

- **Schedules:** duration (`"30m"`, `"2h"`), "every" phrase
  (`"every monday 9am"`), 5-field cron (`"0 9 * * *"`), or ISO timestamp.
- **Per-job knobs:** `skills`, `model`/`provider` override, `script`
  (pre-run data collection; `no_agent=True` makes the script the whole
  job), `context_from` (chain job A's output into job B), `workdir`
  (run in a specific dir with its `AGENTS.md` / `CLAUDE.md` loaded),
  multi-platform delivery.
- **Invariants:** 3-minute hard interrupt per run, `.tick.lock` file
  prevents duplicate ticks across processes, cron sessions pass
  `skip_memory=True` by default, and cron deliveries are framed with a
  header/footer instead of being mirrored into the target gateway
  session (keeps role alternation intact).

User docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

### Curator (skill lifecycle)

Background maintenance for agent-created skills. Tracks usage, marks
idle skills stale, archives stale ones, keeps a pre-run tar.gz backup
so nothing is lost.

- **CLI:** `hermes curator <verb>` — `status`, `run`, `pause`, `resume`,
  `pin`, `unpin`, `archive`, `restore`, `prune`, `backup`, `rollback`.
- **Slash:** `/curator <subcommand>` mirrors the CLI.
- **Scope:** only touches skills with `created_by: "agent"` provenance.
  Bundled + hub-installed skills are off-limits. **Never deletes** —
  max destructive action is archive. Pinned skills are exempt from
  every auto-transition and every LLM review pass.
- **Telemetry:** sidecar at `~/.hermes/skills/.usage.json` holds
  per-skill `use_count`, `view_count`, `patch_count`,
  `last_activity_at`, `state`, `pinned`.

Config: `curator.*` (`enabled`, `interval_hours`, `min_idle_hours`,
`stale_after_days`, `archive_after_days`, `backup.*`).
User docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/curator

### Kanban (multi-agent work queue)

Durable SQLite board for multi-profile / multi-worker collaboration.
Users drive it via `hermes kanban <verb>`; dispatcher-spawned workers
see a focused `kanban_*` toolset gated by `HERMES_KANBAN_TASK` so the
schema footprint is zero outside worker processes.

- **CLI verbs (common):** `init`, `create`, `list` (alias `ls`),
  `show`, `assign`, `link`, `unlink`, `comment`, `complete`, `block`,
  `unblock`, `archive`, `tail`. Less common: `watch`, `stats`, `runs`,
  `log`, `dispatch`, `daemon`, `gc`.
- **Worker toolset:** `kanban_show`, `kanban_complete`, `kanban_block`,
  `kanban_heartbeat`, `kanban_comment`, `kanban_create`, `kanban_link`.
- **Dispatcher** runs inside the gateway by default
  (`kanban.dispatch_in_gateway: true`) — reclaims stale claims,
  promotes ready tasks, atomically claims, spawns assigned profiles.
  Auto-blocks a task after ~5 consecutive spawn failures.
- **Isolation:** board is the hard boundary (workers get
  `HERMES_KANBAN_BOARD` pinned in env); tenant is a soft namespace
  within a board for workspace-path + memory-key isolation.

User docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Hermes Desktop installer fails during Electron download

If Desktop install/bootstrap shows npm `deprecated` warnings but ultimately fails in the `desktop` phase with `RequestError: socket hang up` from Electron's `node install.js`, the warnings are usually not the root cause. The real failure is Electron binary download from GitHub releases timing out or being reset, e.g. `electron-v37.6.0-darwin-arm64.zip`. Verify with:

```bash
curl -I --max-time 20 https://github.com/electron/electron/releases/download/v37.6.0/electron-v37.6.0-darwin-arm64.zip
```

If this times out, enable a proxy/TUN that covers terminal HTTPS traffic or set an Electron mirror before rerunning install:

```bash
export ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
cd ~/.hermes/hermes-agent
ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/ ~/.hermes/node/bin/npm install
```

For npm package registry issues, also set `~/.hermes/node/bin/npm config set registry https://registry.npmmirror.com`. After dependencies install, rebuild/package Desktop from `apps/desktop` if needed.

### Desktop/TUI "request timed out: prompt.submit"

The desktop's default JSON-RPC timeout is 30 seconds (vs. 120 seconds in the shared library), which can time out during slow LLM responses or tool execution. See `references/desktop-tui-timeout-diagnosis.md` for:
- How to distinguish desktop vs. TUI timeout sources
- The three fixes (increase desktop timeout, set TUI env var, or fix provider issues)
- Related GitHub fixes (#38578, session busy retry, clarify timeout persistence)

### Web UI shows "disconnected" but gateway is running

This usually means the Web UI's **GatewayManager** cannot pass its health check against the API server. The manager reads `platforms.api_server.extra.port` from `config.yaml` to know where to probe — if that value diverges from the actual gateway listen port, the UI marks the gateway as down even though the process is alive.

**Diagnostic checklist:**
1. Confirm the gateway process is listening: `lsof -nP -iTCP:8642 -sTCP:LISTEN`
2. Check `config.yaml` for **two** port sources that can drift:
   - `platforms.api_server.extra.port` — used by Web UI GatewayManager for health checks
   - `API_SERVER_PORT` (top-level or `.env`) — used by the gateway itself at startup
3. Verify health on the configured port: `curl -s http://127.0.0.1:<port>/health`
4. If the Web UI upstream log shows `Gateway health check timed out after 15000ms` while the gateway is alive on a different port, the `extra.port` value is stale.

**Fix:**
```bash
# Read the actual port the gateway is listening on (e.g. 8642)
# Then write it into the config key the Web UI reads
hermes config set platforms.api_server.extra.port 8642
hermes gateway restart
```

**Prevention:** Hermes Web UI's `GatewayManager` can auto-reassign ports on startup and write `extra.port` to a new value if it detects a conflict. If a previous run left `extra.port=8646` but the gateway still starts on `8642` (because `API_SERVER_PORT=8642` takes precedence), the mismatch persists until manually aligned. After any port-reassignment event, verify `platforms.api_server.extra.port` matches `API_SERVER_PORT`.

See `references/hermes-web-ui-disconnected-diagnosis.md` for the full step-by-step transcript and commands used in a real session.

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

For live verification, probe the actual auxiliary task path rather than only checking `/models`: run a small `agent.auxiliary_client.call_llm()` script from the Hermes source checkout. See `references/auxiliary-model-probing.md` for a reusable probe and a nowcoding/Kimi `model_not_found` example.

Pitfall: `provider: auto` plus an explicit auxiliary `model` can route that model through the resolved/main provider. If the main provider does not serve that model, auxiliary calls may fail with provider-specific `model_not_found` errors instead of falling back. Match auxiliary models to the provider's served model list, or set an explicit auxiliary provider with independently verified credentials.

---

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

Auto-discovery: any `tools/*.py` file with a top-level `registry.register()` call is imported automatically — no manual list needed.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs — never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Key Rules

- **Never break prompt caching** — don't change context, tools, or system prompt mid-conversation
- **Message role alternation** — never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met
