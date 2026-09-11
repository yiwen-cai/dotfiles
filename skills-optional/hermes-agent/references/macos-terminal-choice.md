# macOS terminal emulator choice for Hermes Agent CLI

Session-derived research note for future Hermes setup/configuration answers.

## Bottom line

For macOS users who want the most reliable terminal for running Hermes Agent CLI, recommend:

1. iTerm2 — default recommendation
2. Ghostty — modern high-performance alternative
3. WezTerm — advanced/power-user option
4. Warp — only when the user explicitly wants Warp/Oz agentic terminal features
5. Kitty — strong but power-user-oriented, not default for macOS Hermes
6. Alacritty — fast/minimal but too sparse for many Hermes workflows
7. Apple Terminal — stable fallback and troubleshooting baseline, not best experience

## Why iTerm2 is the default

Hermes is an interactive CLI agent. The most important properties are predictable PTY/ANSI behavior, long-running session stability, scrollback/search/copy reliability, tmux/SSH support, Unicode/CJK/emoji rendering, and shortcuts that do not interfere with multiline input.

iTerm2 is the safest default on macOS because it has the best balance of maturity, user base, troubleshooting material, split panes/tabs, long scrollback, search, paste history, shell integration, tmux integration, SSH workflows, Unicode, 24-bit color, and configurable key bindings. Its AI Chat feature is optional and does not normally sit in front of Hermes' natural-language input.

Recommended install:

```bash
brew install --cask iterm2
```

Recommended setup:

- Use iTerm2 as the main Hermes terminal.
- Use tmux for long-running sessions and remote work.
- Keep one pane for Hermes, one for tests/logs, one for git/shell work.
- Enable or increase scrollback.
- Enable shell integration if the user wants command navigation/history features.
- Keep paste warnings unless the user deliberately wants less friction.

## Ghostty

Ghostty is the best modern alternative: fast, native-feeling on macOS, clean, low-interference, and good for users who want Hermes to be the only agent layer. It supports modern rendering, tabs/splits, shell integration, ligatures, grapheme/emoji handling, Kitty graphics protocol, and simple `key = value` configuration.

Caveat: it is newer than iTerm2, so for maximum conservatism still recommend iTerm2 first. For SSH/remote environments, TERM/terminfo may occasionally need attention.

Install:

```bash
brew install --cask ghostty
```

## WezTerm

WezTerm is excellent for advanced users: cross-platform, deeply scriptable, strong Unicode/font fallback, tabs/splits, scrollback, search, SSH, mux, and Lua configuration.

Caveat: Lua configuration and the mux/SSH concepts are too much for many users who only want to run Hermes reliably.

Install:

```bash
brew install --cask wezterm
```

## Warp

Warp is not the default recommendation for Hermes, despite being a strong AI-native terminal. It is itself an agentic development environment with Terminal mode, Agent Mode/Oz, natural-language detection, and enhanced support for selected third-party CLI agents.

Use Warp for Hermes only if the user explicitly wants Warp/Oz features. Otherwise it adds an extra agent layer above Hermes and can create ambiguity about whether natural-language input is meant for Warp or Hermes.

If using Warp with Hermes:

- Run Hermes in Terminal mode, not inside a Warp Agent conversation.
- Consider Classic Input.
- Disable or be cautious with natural-language autodetection.
- Do not assume Hermes receives Warp's third-party CLI agent enhancements; Warp's supported agent list has included tools like Claude Code, Codex, OpenCode, etc., but Hermes was not found in the official list during this research.
- Avoid having Warp Agent and Hermes Agent work on the same task context simultaneously.

Install:

```bash
brew install --cask warp
```

## Kitty

Kitty is powerful and fast, with modern terminal protocols, but it is more Linux/power-user oriented. macOS native integration, terminfo/tmux/remote details, and Unicode width/Nerd Font edge cases can create extra troubleshooting burden. Good for users already familiar with Kitty; not the default Hermes recommendation.

Install:

```bash
brew install --cask kitty
```

## Alacritty

Alacritty is fast and minimal. It is fine if the user delegates tabs/splits/session management to tmux, but it lacks many convenience features useful for Hermes workflows: built-in tabs/splits, richer shell integration, extensive search/copy/history workflows, and modern terminal app ergonomics.

Install:

```bash
brew install --cask alacritty
```

## Apple Terminal

Apple Terminal is stable and built in, useful as a fallback or to determine whether an issue is terminal-specific. It is conservative and not the best experience for heavy Hermes usage.

## Suggested answer pattern

When asked "which terminal should I use for Hermes on macOS?":

- Short answer: iTerm2.
- Add: Ghostty if the user wants a modern/fast clean terminal; WezTerm if they are a power user; Warp only if they deliberately want Warp/Oz agent features.
- Explain Warp carefully: third-party CLI agents run in Terminal mode; do not describe Hermes as running in Warp Agent Mode unless the user explicitly wraps it that way.
