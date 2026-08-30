# Warp Terminal mode vs Agent mode notes

Source checked during session: https://docs.warp.dev/agent-platform/local-agents/interacting-with-agents/terminal-and-agent-modes/ and Warp docs `llms.txt` bundles. Last-updated marker on the page at the time: May 8, 2026.

## Official phrasing

Warp provides two distinct modes:

- A clean terminal for commands.
- A dedicated conversation view for multi-turn conversations with Oz, Warp's agent.

Key terms:

- Terminal session: shell environment where users run commands; default when opening Warp.
- Oz agent conversation: multi-turn interaction with Oz; maintains context and has a dedicated view with richer controls.

## Why two modes

- Clean terminal by default: minimal input for command running; agent controls appear only when needed.
- Dedicated conversation view: full controls for multi-turn agent workflows, including model selection, voice input, image attachments, and conversation history.
- Explicit mode switching: makes terminal work and agent work visually distinct and easier to organize.

## Terminal mode

- Default when opening a new tab or pane unless settings are changed.
- Looks/behaves like a traditional terminal input.
- Agent controls are not always visible.
- Bottom message bar shows contextual hints, e.g. start a new agent, send text to agent, attach failed command output, continue conversation.
- If auto-detection is enabled, Warp labels input as agent or shell before submission.

## Oz agent conversation view / Agent Mode

- Dedicated conversation UI with richer controls: model select, voice input, image attachments, conversation management, current directory/git branch/diff view entry, etc.
- Designed for multi-turn workflows and managing multiple conversations.
- Agent controls appear only inside a conversation, keeping terminal mode clean.
- Identified by alternate background color and an input toolbelt.

## Block origin and visibility

- Terminal blocks: commands run directly in terminal mode; appear in terminal blocklist; can be attached as context to any conversation.
- Agent conversation blocks: commands executed within an agent conversation, by user or agent; only appear in that conversation and do not appear in the terminal blocklist.
- Commands executed within an agent conversation become automatic context for later prompts in that conversation.
- Terminal blocks can be manually attached to bring outside outputs into a conversation.

## Auto-detection

- Terminal mode: if input appears to be natural language, Warp labels it as an agent request and can send it directly to an agent conversation.
- Agent view: if input appears to be a shell command, Warp indicates it will run as command rather than prompt.
- Settings are separate:
  - `Autodetect agent prompts in terminal input`
  - `Autodetect terminal commands in agent input`
- Override methods:
  - macOS `Cmd+I`, Windows/Linux `Ctrl+I` toggles command vs Agent Mode.
  - In agent view, prefix with `!` to force shell command, e.g. `!git status`.

## Entering conversations

- `/agent` or `/new` in terminal mode opens a new agent conversation view.
- `/agent <prompt>` sends the prompt directly to a new conversation.
- macOS `Cmd+Enter`, Windows/Linux `Ctrl+Shift+Enter` enters conversation view.
- With auto-detection in terminal mode, typing a natural-language request and pressing Enter can quicksend to the agent.

## Cloud agent conversations

- Shortcut from terminal mode: macOS `Option+Cmd+Enter`; Windows/Linux `Ctrl+Alt+Enter`.
- Run in isolated cloud environments.
- Useful for parallel agents, remote/offloaded compute, autonomous background work, and checking in from anywhere.
- Differ from local conversations with environment selector, credits indicator, and cloud storage.

## Third-party CLI agents

Warp docs describe Claude Code, Codex, OpenCode, and similar tools as third-party CLI agents. They are run in Warp's terminal mode as CLI programs and enhanced with Warp features like rich input, notifications, code review, vertical tabs, remote control, and tab configs.

Important user-facing wording: if asked whether to use Agent Mode for Claude Code/Codex/OpenCode, say no — run those in Terminal mode. Warp Agent Mode is for Warp's built-in Oz agent.
