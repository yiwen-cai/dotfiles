#!/usr/bin/env bash
# dotfiles 一键安装脚本
# 用法: ./install.sh
# 功能: 把仓库内的配置软链接到 ~/.claude、~/.codex 和 Cursor 对应位置
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_HOME="$HOME/.claude"
CODEX_HOME="$HOME/.codex"
CURSOR_HOME="$HOME/.cursor"
CURSOR_USER="$HOME/Library/Application Support/Cursor/User"

ln_safe() {
  # ln_safe <源文件> <目标>
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -e "$dst" ] || [ -L "$dst" ]; then
    echo "  [skip] 已存在: $dst"
  else
    ln -s "$src" "$dst"
    echo "  [link] $dst -> $src"
  fi
}

copy_if_missing() {
  # copy_if_missing <源文件> <目标>  (用于含密钥的文件，不做软链接)
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -e "$dst" ]; then
    echo "  [skip] 已存在: $dst"
  else
    cp "$src" "$dst"
    echo "  [copy] $dst (来自 $src)"
  fi
}

echo "==> 安装 Claude Code 配置"
mkdir -p "$CLAUDE_HOME"
# 普通配置：软链接
ln_safe "$REPO_DIR/claude/CLAUDE.md"        "$CLAUDE_HOME/CLAUDE.md"
ln_safe "$REPO_DIR/claude/hermes-rules.md"  "$CLAUDE_HOME/hermes-rules.md"
# skills 目录：软链接整个目录
if [ -d "$REPO_DIR/claude/skills" ]; then
  if [ -e "$CLAUDE_HOME/skills" ] && [ ! -L "$CLAUDE_HOME/skills" ]; then
    echo "  [warn] $CLAUDE_HOME/skills 已存在且非软链接，跳过（请手动合并）"
  else
    ln_safe "$REPO_DIR/claude/skills" "$CLAUDE_HOME/skills"
  fi
fi

echo "==> 安装 Codex 配置"
mkdir -p "$CODEX_HOME"
ln_safe "$REPO_DIR/codex/AGENTS.md"          "$CODEX_HOME/AGENTS.md"
ln_safe "$REPO_DIR/codex/config.toml"        "$CODEX_HOME/config.toml"
ln_safe "$REPO_DIR/codex/rules/default.rules" "$CODEX_HOME/rules/default.rules"
if [ -d "$REPO_DIR/codex/skills" ]; then
  if [ -e "$CODEX_HOME/skills" ] && [ ! -L "$CODEX_HOME/skills" ]; then
    echo "  [warn] $CODEX_HOME/skills 已存在且非软链接，跳过（请手动合并）"
  else
    ln_safe "$REPO_DIR/codex/skills" "$CODEX_HOME/skills"
  fi
fi

echo "==> 安装 Cursor 配置"
mkdir -p "$CURSOR_HOME" "$CURSOR_USER"
# Editor settings (macOS Application Support)
ln_safe "$REPO_DIR/cursor/settings.json"    "$CURSOR_USER/settings.json"
ln_safe "$REPO_DIR/cursor/keybindings.json" "$CURSOR_USER/keybindings.json"
if [ -d "$REPO_DIR/cursor/snippets" ]; then
  if [ -e "$CURSOR_USER/snippets" ] && [ ! -L "$CURSOR_USER/snippets" ]; then
    echo "  [warn] $CURSOR_USER/snippets 已存在且非软链接，跳过（请手动合并）"
  else
    ln_safe "$REPO_DIR/cursor/snippets" "$CURSOR_USER/snippets"
  fi
fi
# Agent / CLI configs under ~/.cursor
ln_safe "$REPO_DIR/cursor/hooks.json"       "$CURSOR_HOME/hooks.json"
ln_safe "$REPO_DIR/cursor/cli-config.json"  "$CURSOR_HOME/cli-config.json"

echo
echo "==> 需要手动填写的密钥文件（已提供 .example 模板）"
echo "    cd $REPO_DIR"
echo "    cp claude/settings.json.example ~/.claude/settings.json    # 然后编辑填入 ANTHROPIC_AUTH_TOKEN"
echo "    cp claude/config.json.example    ~/.claude/config.json     # 然后编辑填入 primaryApiKey"
echo "    cp codex/auth.json.example       ~/.codex/auth.json        # 然后编辑填入 OPENAI_API_KEY"
echo "    cp codex/.env.example            ~/.codex/.env             # 然后编辑填入代理"
echo "    cp cursor/mcp.json.example       ~/.cursor/mcp.json        # 然后编辑填入 TAVILY_API_KEY 等"
echo
echo "==> 可选：安装 Cursor 扩展"
echo "    # 需要 cursor CLI 在 PATH 中"
echo "    xargs -n1 cursor --install-extension < $REPO_DIR/cursor/extensions.txt"
echo
echo "✅ 安装完成"
