#!/usr/bin/env bash
# ============================================================
# 校验 skills 单一事实源结构与部署一致性
#
# 用法:
#   scripts/check-skills.sh            # 校验仓库结构（防再次分叉）
#   scripts/check-skills.sh --deployed # 额外校验各部署目录与仓库一致
#
# 检查项:
#   1. claude/skills 与 codex/skills 必须是软链接（不得出现真实双树）
#   2. 每个技能目录都有 SKILL.md，且 frontmatter name 与目录名一致
#   3. skills/ 与 skills-local/ 之间无重名
#   4. 无跨技能路径引用（~/.claude/skills/<X>/SKILL.md 这类导致双树分叉的写法）
#   5. 无 .codex/notes（执行笔记统一约定为 .claude/notes）
#   6. 其他 ~/.claude、~/.codex 字面路径给出 WARN 供人工复核
#   7. --deployed: 每个部署目录与仓库期望内容一致
# 退出码: 0 = 无 FAIL（WARN 不阻断）
# ============================================================
set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS="$REPO_DIR/skills"
LOCAL="$REPO_DIR/skills-local"
fail=0
warn=0

note()  { echo "FAIL: $1"; fail=$((fail + 1)); }
warnf() { echo "WARN: $1"; warn=$((warn + 1)); }

# ---------- 1. 仓库内不得再有真实双树 ----------
for t in claude codex; do
  link="$REPO_DIR/$t/skills"
  if [ -L "$link" ]; then
    [ "$(readlink "$link")" = "../skills" ] \
      || warnf "$t/skills 软链接目标应为 ../skills（当前: $(readlink "$link")）"
  else
    note "$t/skills 不是软链接（出现真实目录说明又分叉了）"
  fi
done

# ---------- 2. 技能目录完整性 ----------
check_tree() {
  local root="$1" kind="$2"
  [ -d "$root" ] || { note "$kind 目录不存在: $root"; return; }
  local dir
  for dir in "$root"/*/; do
    [ -d "$dir" ] || continue
    local name fname desc
    name="$(basename "$dir")"
    case "$name" in
      .system|.*.bak*) note "$kind 含垃圾目录: $name"; continue ;;
    esac
    if [ ! -f "$dir/SKILL.md" ]; then
      note "$kind/$name 缺少 SKILL.md"; continue
    fi
    fname="$(awk -F': *' '/^name:/{print $2; exit}' "$dir/SKILL.md" | tr -d '"' | xargs)"
    [ -n "$fname" ] || { note "$kind/$name SKILL.md 缺少 name"; continue; }
    [ "$fname" = "$name" ] || warnf "$kind/$name 目录名($name)与 frontmatter name($fname) 不一致（harness 容忍，注意引用时用 frontmatter 名）"
    desc="$(awk -F': *' '/^description:/{print $2; exit}' "$dir/SKILL.md")"
    [ -n "$desc" ] || warnf "$kind/$name 缺少 description"
  done
}
check_tree "$SKILLS" "skills"
check_tree "$LOCAL" "skills-local"

# ---------- 3. skills/ 与 skills-local/ 重名检查 ----------
for d in "$LOCAL"/*/; do
  [ -d "$d" ] || continue
  n="$(basename "$d")"
  [ -d "$SKILLS/$n" ] && note "技能重名: skills/$n 与 skills-local/$n"
done

# ---------- 4. 交叉引用与工具路径检查（防再次分叉） ----------
check_refs() {
  local root="$1" kind="$2"
  [ -d "$root" ] || return
  local dir
  for dir in "$root"/*/; do
    [ -d "$dir" ] || continue
    local self
    self="$(basename "$dir")"
    local file
    for file in "$dir"/SKILL.md "$dir"/references/*.md; do
      [ -f "$file" ] || continue
      # 4a. 跨技能路径引用（~/.claude/skills/<X>、~/.codex/skills/<X>、.claude/skills/<X> 等）
      #     自引用与已部署到所有目标的本地技能（bupt-thesis-writer）除外
      local m
      while read -r m; do
        [ -n "$m" ] || continue
        if [ "$m" != "$self" ] && [ "$m" != "bupt-thesis-writer" ]; then
          note "$kind/$self: 跨技能路径引用 ...skills/$m（应改为按技能名引用）"
        fi
      done < <(grep -oE '(~/|\.)(claude|codex)/skills/[^/]+' "$file" \
               | sed -E 's|.*/skills/||; s|[^a-zA-Z0-9_-].*$||' | sort -u)
      # 4b. .codex/notes 不允许（统一约定为 .claude/notes）
      if grep -q '\.codex/notes' "$file"; then
        note "$kind/$self: 出现 .codex/notes（统一约定为 .claude/notes）"
      fi
      # 4c. 其余 ~/.claude、~/.codex 字面路径 → WARN 人工复核
      local line
      while IFS= read -r line; do
        [ -n "$line" ] || continue
        case "$line" in
          *".claude/notes"*) ;;                                        # 统一执行笔记约定
          *"~/.claude/skills/$self"* | *"~/.codex/skills/$self"*) ;;    # 自身目录引用
          *"bupt-thesis-writer"*) ;;                                    # 已部署到所有目标的本地技能
          *) warnf "$kind/$self: ${line%%:*}: $(echo "$line" | cut -d: -f2- | xargs)" ;;
        esac
      done < <(grep -nE '~/(\.claude|\.codex)/' "$file")
    done
  done
}
check_refs "$SKILLS" "skills"
check_refs "$LOCAL" "skills-local"

# ---------- 5. （可选）部署一致性 ----------
if [ "${1:-}" = "--deployed" ]; then
  # shellcheck source=skills-targets.sh
  # shellcheck disable=SC1091
  source "$REPO_DIR/scripts/skills-targets.sh"
  for entry in "${SKILL_TARGETS[@]}"; do
    label="${entry%%|*}"; rest="${entry#*|}"
    dst="${rest%%|*}"; rest="${rest#*|}"
    main_tree="${rest%%|*}"; locals="${rest#*|}"
    if [ ! -d "$dst" ]; then
      note "部署目标不存在（尚未运行 install.sh）: $label ($dst)"
      continue
    fi
    stage="$(build_skill_stage "$locals")"
    srcs=()
    [ "$main_tree" = "yes" ] && srcs+=("$SKILLS_DIR/")
    srcs+=("$stage/")
    dry="$(rsync -ainO --delete --exclude='.system' \
           "${srcs[@]}" "$dst/" 2>&1 \
           | grep -vE '^sending|^sent |^total |^$' || true)"
    rm -rf "$stage"
    if [ -n "$dry" ]; then
      echo "DIFF: $label ($dst)"
      echo "$dry" | head -8
      fail=$((fail + 1))
    else
      echo "ok: $label 与仓库一致"
    fi
  done
fi

echo
echo "== 结果: $fail 个 FAIL, $warn 个 WARN =="
[ "$fail" -eq 0 ] && exit 0 || exit 1
