#!/usr/bin/env bash
# dotfiles 一键安装脚本
# 用法: ./install.sh
# 功能: 把仓库内的配置软链接到 ~/.claude 和 ~/.codex 对应位置
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_HOME="$HOME/.claude"
CODEX_HOME="$HOME/.codex"

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

echo
echo "==> 需要手动填写的密钥文件（已提供 .example 模板）"
echo "    cd $REPO_DIR"
echo "    cp claude/settings.json.example ~/.claude/settings.json    # 然后编辑填入 ANTHROPIC_AUTH_TOKEN"
echo "    cp claude/config.json.example    ~/.claude/config.json     # 然后编辑填入 primaryApiKey"
echo "    cp codex/auth.json.example       ~/.codex/auth.json        # 然后编辑填入 OPENAI_API_KEY"
echo "    cp codex/.env.example            ~/.codex/.env             # 然后编辑填入代理"
echo
echo "✅ 安装完成"
