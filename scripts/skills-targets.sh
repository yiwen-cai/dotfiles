# ============================================================
# skills 部署目标定义（install.sh 与 scripts/check-skills.sh 共用）
# 单一事实源：repo/skills/（全量技能）+ repo/skills-local/（本机专属，按白名单部署）
#
# 格式: "<目标名>|<目标目录>|<部署主树:yes/no>|<本地技能白名单(逗号分隔，可为空)>"
# 每个目标目录由 install.sh 全权管理（rsync --delete 收敛到仓库状态）
# ============================================================
SKILLS_DIR="$REPO_DIR/skills"
SKILLS_LOCAL_DIR="$REPO_DIR/skills-local"

SKILL_TARGETS=(
  "claude|$HOME/.claude/skills|yes|bupt-thesis-writer,cuda-skill,cutlass-skill,sglang-skill,triton-skill"
  "codex|$HOME/.codex/skills|yes|bupt-thesis-writer"
  "zcode|$HOME/.zcode/skills|yes|"
  "agents|$HOME/.agents/skills|no|cuda-skill,cutlass-skill,sglang-skill,triton-skill"
)

# 构建部署视图：白名单内的本地技能以符号链接形式放进 staging 目录，
# 使 rsync 多源合并时每个本地技能都落在目标目录的顶层（与 skills/ 的子目录布局一致）。
# 用法: stage="$(build_skill_stage "a,b,c")"; ...; rm -rf "$stage"
build_skill_stage() {
  local locals="$1" stage l
  stage="$(mktemp -d)"
  if [ -n "$locals" ]; then
    local _arr
    IFS=',' read -ra _arr <<< "$locals"
    for l in "${_arr[@]}"; do
      if [ -d "$SKILLS_LOCAL_DIR/$l" ]; then
        ln -s "$SKILLS_LOCAL_DIR/$l" "$stage/$l"
        # 幂等：让 stage 符号链接 mtime 跟随仓库目录，避免每次部署都报变更
        touch -h -r "$SKILLS_LOCAL_DIR/$l" "$stage/$l" 2>/dev/null || true
      else
        echo "  [warn] skills-local/$l 不存在，跳过" >&2
      fi
    done
  fi
  echo "$stage"
}
