#!/usr/bin/env bash
# dotfiles 一键安装脚本
# 用法: ./install.sh
# 功能: 把仓库内的配置软链接到 Claude、Codex、Cursor 和 Helix 对应位置；
#       skills 按 skills-manifest.json 部署，仅更新已登记名称
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_HOME="$HOME/.claude"
CODEX_HOME="$HOME/.codex"
CURSOR_HOME="$HOME/.cursor"
CURSOR_USER="$HOME/Library/Application Support/Cursor/User"
HELIX_HOME="$HOME/.config/helix"
LOCAL_BIN="$HOME/.local/bin"
LOCAL_SECRETS="$HOME/.config/dotfiles/secrets.zsh"

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
  if [ -e "$dst" ] || [ -L "$dst" ]; then
    echo "  [skip] 已存在: $dst"
  else
    (umask 077; cp "$src" "$dst")
    echo "  [copy] $dst (来自 $src)"
  fi
}

echo "==> 安装 Claude Code 配置"
mkdir -p "$CLAUDE_HOME"
# 普通配置：软链接
ln_safe "$REPO_DIR/claude/CLAUDE.md"        "$CLAUDE_HOME/CLAUDE.md"
ln_safe "$REPO_DIR/claude/hermes-rules.md"  "$CLAUDE_HOME/hermes-rules.md"

echo "==> 部署受管理的 skills（清单: skills-manifest.json）"
# Only enabled Codex/agents profiles; preserve unknown packages and disabled hosts.
source "$REPO_DIR/scripts/skills-targets.sh"
deploy_managed_skills

echo "==> 安装 Codex 配置"
mkdir -p "$CODEX_HOME"
ln_safe "$REPO_DIR/codex/AGENTS.md"          "$CODEX_HOME/AGENTS.md"
ln_safe "$REPO_DIR/codex/config.toml"        "$CODEX_HOME/config.toml"
ln_safe "$REPO_DIR/codex/rules/default.rules" "$CODEX_HOME/rules/default.rules"

echo "==> 安装 pi agent 配置"
PI_HOME="$HOME/.pi/agent"
mkdir -p "$PI_HOME/extensions"
# 主配置：软链接（pi 会回写 lastChangelogVersion，属正常；见 pi/README.md）
ln_safe "$REPO_DIR/pi/settings.json"  "$PI_HOME/settings.json"
ln_safe "$REPO_DIR/pi/starline.json"  "$PI_HOME/starline.json"
# 含密钥的文件：只复制模板，绝不覆盖本机真实文件
copy_if_missing "$REPO_DIR/pi/auth.json.example" "$PI_HOME/auth.json"
copy_if_missing "$REPO_DIR/pi/extensions/nowcoding.ts"        "$PI_HOME/extensions/nowcoding.ts"
copy_if_missing "$REPO_DIR/pi/extensions/nowcoding-claude.ts" "$PI_HOME/extensions/nowcoding-claude.ts"
echo "  [hint] 新机器需手动填写 ~/.pi/agent/auth.json 与 extensions 中的 apiKey（见 pi/README.md）"

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

echo "==> 安装 Helix 配置"
ln_safe "$REPO_DIR/helix/config.toml" "$HELIX_HOME/config.toml"
ln_safe "$REPO_DIR/helix/languages.toml" "$HELIX_HOME/languages.toml"
ln_safe "$REPO_DIR/helix/runtime/queries/cuda" \
  "$HELIX_HOME/runtime/queries/cuda"
ln_safe "$REPO_DIR/helix/bin/clangd-helix" "$LOCAL_BIN/clangd-helix"
case ":$PATH:" in
  *":$LOCAL_BIN:"*) ;;
  *) echo "  [warn] 请将 $LOCAL_BIN 加入 PATH，Helix 才能找到 clangd-helix" ;;
esac

echo "==> 准备本机密钥配置"
copy_if_missing "$REPO_DIR/secrets.zsh.example" "$LOCAL_SECRETS"
if [ -f "$LOCAL_SECRETS" ] && [ ! -L "$LOCAL_SECRETS" ]; then
  chmod 600 "$LOCAL_SECRETS"
else
  echo "  [warn] $LOCAL_SECRETS 不是普通文件，未修改其权限"
fi

echo
echo "==> 需要手动填写的密钥文件（已提供 .example 模板）"
echo "    cd $REPO_DIR"
echo "    cp claude/settings.json.example ~/.claude/settings.json    # 然后编辑填入 ANTHROPIC_AUTH_TOKEN"
echo "    cp claude/config.json.example    ~/.claude/config.json     # 然后编辑填入 primaryApiKey"
echo "    cp codex/auth.json.example       ~/.codex/auth.json        # 然后编辑填入 OPENAI_API_KEY"
echo "    cp codex/.env.example            ~/.codex/.env             # 然后编辑填入代理"
echo "    cp cursor/mcp.json.example       ~/.cursor/mcp.json        # 然后编辑填入 TAVILY_API_KEY 等"
echo "    $LOCAL_SECRETS                    # 填本机环境变量，不要提交"
echo
echo "==> 可选：安装 Cursor 扩展"
echo "    # 需要 cursor CLI 在 PATH 中"
echo "    xargs -n1 cursor --install-extension < $REPO_DIR/cursor/extensions.txt"
echo
echo "✅ 安装完成"
