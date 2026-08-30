#!/usr/bin/env bash
# dotfiles 一键安装脚本
# 用法: ./install.sh
# 功能: 把仓库内的配置软链接到 Claude、Codex、Cursor 和 Helix 对应位置；
#       skills 由单一事实源（repo/skills + repo/skills-local）rsync 部署到各工具目录
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

echo "==> 部署 skills（单一事实源: repo/skills + repo/skills-local）"
# shellcheck source=scripts/skills-targets.sh
source "$REPO_DIR/scripts/skills-targets.sh"

deploy_skills() {
  # deploy_skills <目标名> <目标目录> <部署主树:yes/no> <本地技能白名单(逗号分隔)>
  local label="$1" dst="$2" main_tree="$3" locals="$4" stage srcs=()
  stage="$(build_skill_stage "$locals")"
  [ "$main_tree" = "yes" ] && srcs+=("$REPO_DIR/skills/")
  srcs+=("$stage/")
  mkdir -p "$dst"
  # 旧版整目录软链接 → 改为独立管理的真实目录
  if [ -L "$dst" ]; then
    echo "  [info] $label: 移除旧的整目录软链接，改为 rsync 管理"
    rm "$dst"
    mkdir -p "$dst"
  fi
  # --exclude='.system': 保护 Codex 内置技能目录（不得删除）
  local dry
  dry="$(rsync -ainO --delete --exclude='.system' \
         "${srcs[@]}" "$dst/" 2>&1 \
         | grep -vE '^sending|^sent |^total |^$' || true)"
  if [ -n "$dry" ]; then
    echo "  [sync] $label ($(echo "$dry" | wc -l) 项变更)"
    echo "$dry" | sed 's/^/         /' | head -12 || true
    rsync -aO --delete --exclude='.system' "${srcs[@]}" "$dst/"
    echo "  [done] $label -> $dst"
  else
    echo "  [ok] $label 已是最新 ($dst)"
  fi
  rm -rf "$stage"
}

for _t in "${SKILL_TARGETS[@]}"; do
  _label="${_t%%|*}"; _rest="${_t#*|}"
  _dst="${_rest%%|*}"; _rest="${_rest#*|}"
  _main="${_rest%%|*}"; _locals="${_rest#*|}"
  deploy_skills "$_label" "$_dst" "$_main" "$_locals"
done

echo "==> 安装 Codex 配置"
mkdir -p "$CODEX_HOME"
ln_safe "$REPO_DIR/codex/AGENTS.md"          "$CODEX_HOME/AGENTS.md"
ln_safe "$REPO_DIR/codex/config.toml"        "$CODEX_HOME/config.toml"
ln_safe "$REPO_DIR/codex/rules/default.rules" "$CODEX_HOME/rules/default.rules"

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
