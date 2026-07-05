---
name: warp-agentic-development
description: 'Use and explain Warp, the agentic development environment: Terminal mode, Agent mode, Oz agents, CLI agents,
  cloud agents, and official docs lookup.'
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Warp Agentic Development

Use this skill when the user asks about Warp, Warp Terminal, Warp Agent Mode, Oz agents, Warp cloud agents, third-party CLI agents inside Warp, or comparisons such as Agent tab vs Terminal tab.

## Official docs lookup

1. Start from the official docs, not memory:
   - https://docs.warp.dev/
   - https://docs.warp.dev/llms.txt
2. Prefer the docs' LLM text bundles for fast extraction:
   - `https://docs.warp.dev/_llms-txt/getting-started.txt`
   - `https://docs.warp.dev/_llms-txt/terminal.txt`
   - `https://docs.warp.dev/_llms-txt/agent-platform.txt`
3. Individual docs pages advertise that markdown versions are available by appending `.md` to URLs, but some guessed paths may 404. If a guessed `.md` path fails, use `llms.txt` / `_llms-txt/*.txt` or browse the canonical HTML page.

## Core mental model

Warp is an agentic development environment combining a modern terminal with Oz, Warp's agent orchestration layer.

Keep these concepts separate:

- Terminal mode: a shell session for commands, default for new tabs/panes unless configured otherwise.
- Agent mode / Oz agent conversation view: a dedicated multi-turn conversation view for Warp's built-in Oz agent.
- Third-party CLI agents: tools like Claude Code, Codex, and OpenCode run as terminal commands inside Terminal mode, not inside Warp's built-in Agent Mode.
- Cloud agents: Oz agents running remotely/in the cloud for parallel, autonomous, or offloaded work.

## Explaining Terminal mode vs Agent mode

When asked for the difference, answer around these axes:

- Interaction target: shell vs Oz agent.
- Input interpretation: shell command vs natural-language prompt.
- UI: clean terminal input vs expanded conversation controls.
- Context: terminal blocks manually attachable vs conversation-scoped automatic context.
- Use cases: known commands/CLI agents vs AI-driven coding/debugging/multi-step workflows.
- Shortcuts: macOS `Cmd+Enter` / Windows/Linux `Ctrl+Shift+Enter` to start an agent conversation; `Esc` returns to terminal; `Cmd+I` / `Ctrl+I` toggles shell/agent interpretation.

## Important pitfalls

- Do not describe Claude Code/Codex/OpenCode as running in Warp Agent Mode. They are third-party CLI agents and should be run in Terminal mode.
- Do not imply Agent Mode commands pollute the normal terminal block list. Warp scopes commands executed within an agent conversation to that conversation.
- Warp's UI language changes; prefer current docs terminology (`Terminal mode`, `Agent Mode`, `Oz agent conversation`) over user shorthand like `Agent tab` / `Terminal tab`, while acknowledging the shorthand.
- For current feature details, verify against docs; Warp changes quickly.

## Reference notes

- `references/terminal-agent-modes.md` contains a condensed, sourced note from the May 2026 Warp docs about Terminal mode vs Oz agent conversation view, auto-detection, block scope, cloud conversations, and shortcuts.