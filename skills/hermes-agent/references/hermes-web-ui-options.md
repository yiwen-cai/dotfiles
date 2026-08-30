# Hermes Web UI options

Use this when the user asks what Web UI / browser UI options are currently usable with Hermes Agent.

## Current options

### 1. Official Hermes Web Dashboard

- Maturity: official, local-first management UI; best for configuration/control, not necessarily the richest chat product.
- Use cases: manage config, API keys, sessions, toolsets, skills; optional browser Chat/TUI.
- Install/start:

```bash
pip install 'hermes-agent[web,pty]'
hermes dashboard
```

- Default URL: `http://127.0.0.1:9119`
- Useful flags: `--port`, `--host`, `--no-open`, `--tui`.
- Security note: binding beyond localhost can expose sensitive config/API-key surfaces.
- Source: `https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard`

### 2. Open WebUI + Hermes API Server

- Maturity: recommended general-purpose chat Web UI path. Open WebUI is mature, and Hermes has official integration docs.
- Use cases: ChatGPT-like web chat, multi-user UI, session management, account system.
- Hermes exposes an OpenAI-compatible API server; Open WebUI connects as an OpenAI endpoint.
- Default Hermes API URL: `http://127.0.0.1:8642/v1`
- Hermes setup:

```bash
hermes config set API_SERVER_ENABLED true
hermes config set API_SERVER_KEY your-secret-key
hermes gateway
```

- Open WebUI Docker example:

```bash
docker run -d -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8642/v1 \
  -e OPENAI_API_KEY=your-secret-key \
  -e ENABLE_OLLAMA_API=false \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

- Open: `http://localhost:3000`
- Important: Hermes API Server is an agent runtime, not just a model proxy. Tool calls execute on the API Server host.
- Sources:
  - `https://hermes-agent.nousresearch.com/docs/user-guide/messaging/open-webui`
  - `https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server`
  - `https://github.com/open-webui/open-webui`

### 3. EKKOLearnAI/hermes-web-ui

- Maturity: community project, feature-rich and Hermes-specific, but not official.
- Reported session snapshot: GitHub around 3964 stars, MIT license, active as of 2026-05-08; npm latest observed version `0.5.14`.
- Features: AI chat, multi-session UI, SSE streaming, tool-call display, file upload/download, platform config for Telegram/Discord/Slack/WhatsApp/Matrix/Feishu/Weixin/WeCom, usage analytics, cron, model management, profiles/gateway management, file browser, skills/memory management, Web Terminal, group chat.
- npm start:

```bash
npm install -g hermes-web-ui
hermes-web-ui start
```

- Default npm URL: `http://localhost:8648`
- Docker Compose example from project:

```bash
WEBUI_IMAGE=ekkoye8888/hermes-web-ui:latest docker compose up -d hermes-agent hermes-webui
```

- Default compose URL observed in docs: `http://localhost:6060`
- Architecture summary: Browser -> BFF/Koa (`:8648`) -> Hermes Gateway (`:8642`) -> Hermes CLI/config files.
- Sources:
  - `https://github.com/EKKOLearnAI/hermes-web-ui`
  - `https://www.npmjs.com/package/hermes-web-ui`

### 4. Other OpenAI-compatible Web frontends

Any UI that can point at an OpenAI-compatible base URL can often connect to Hermes API Server.

Examples: LobeChat, LibreChat, AnythingLLM, NextChat, ChatBox, Jan, HF Chat-UI, big-AGI.

Typical settings:

```text
Base URL: http://localhost:8642/v1
API Key: Hermes API_SERVER_KEY
Model: hermes-agent or a profile/model name accepted by the server
```

## Recommendation template

- Official/local management: use `hermes dashboard`.
- Mature ChatGPT-like web chat: use Open WebUI + Hermes API Server.
- Hermes-specific all-in-one control panel: try `EKKOLearnAI/hermes-web-ui`, with community-project risk.
- Existing LobeChat/LibreChat/NextChat/etc.: connect directly through the OpenAI-compatible API Server.

## Pitfalls

- Do not expose dashboard/API server publicly without authentication and network controls.
- Remind users that API Server tools run on the server machine.
- For Docker on Linux, `host.docker.internal` may require `--add-host=host.docker.internal:host-gateway`.
- For current stats/version, re-check GitHub/npm instead of repeating the session snapshot.
