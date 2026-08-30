---
name: resume-review
description: Review, compare, and sync Typst-based resumes (CVs). Covers Chinese/English version consistency, typst-specific
  formatting issues, and iterative review workflows.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

Review Typst resume files (`.typ` using `basic-resume` template) for issues.

## Triggers

- User asks to review their resume/CV/简历
- User asks to sync Chinese and English resume versions
- Working in a directory containing `.typ` files with `basic-resume` template

## User Preference

When reviewing resumes, **list only problems — do NOT include suggestions or fixes** unless the user explicitly asks for them. The user will iterate and fix on their own. Format: short bullet list, grouped by severity.

## Workflow

### Initial Review
1. `search_files` the CV directory for `.typ` and `.pdf` files
2. `read_file` all `.typ` source files
3. Check for issues across these categories (see `references/common-issues.md`)
4. Present problems only, no suggestions

### Iterative Review (user says "再看看" / "再检查")
1. Re-read the file to confirm changes
2. Report only remaining issues (acknowledge fixed items briefly)

### Sync English from Chinese
When user says "按照中文版本同步英文版本":
1. Chinese version is the **source of truth** — all data (GPA, rank, projects, awards, skills) must match
2. Translate Chinese content to English, preserving all technical terms
3. Use `write_file` to rewrite the entire English file
4. Report a summary table of what changed

### Typst-Specific Checks
- `#work()` vs `#project()` usage — `#work` implies company/organization, `#project` for standalone work
- `dates-helper(start-date: ..., end-date: ...)` for date ranges; `dates: "..."` for single dates
- `#super[st]` / `#super[nd]` for ordinal suffixes — rendered as superscript
- `link("url")[text]` for hyperlinked project names

## Section Mapping (Chinese ↔ English)

| Chinese | English |
|---------|---------|
| 教育经历 | Education |
| 项目经验 | Projects |
| 奖项 | Awards |
| 技能 | Skills |
| 编程语言 | Programming Languages |
| 研究方向 | Research Directions |