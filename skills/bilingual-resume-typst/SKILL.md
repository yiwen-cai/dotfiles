---
name: bilingual-resume-typst
description: Manage, review, and sync bilingual (Chinese/English) resumes and personal statements built with Typst's basic-resume
  template. Use when the user asks to review, update, translate, or generate PDFs fro
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Bilingual Resume with Typst

## Trigger

The user asks to review, edit, sync, or generate PDFs of resumes, CVs, or personal statements written in Typst (`.typ` files). The user's resume project lives at `~/Documents/study/CV/basic-resume/`.

## Key Files

| File | Purpose |
|------|---------|
| `chinese.typ` | Chinese resume — **source of truth** |
| `main.typ` | English resume — translation of Chinese |
| `personal_statement.typ` | English personal statement |
| `personal_statement_cn.typ` | Chinese personal statement |

## Compilation

```bash
cd ~/Documents/study/CV/basic-resume
typst compile chinese.typ chinese.pdf
typst compile main.typ main.pdf
typst compile personal_statement.typ personal_statement.pdf
typst compile personal_statement_cn.typ personal_statement_cn.pdf
```

macOS available Chinese fonts (check with `typst fonts | grep -iE 'song|hei|kai|sc'`):
- **Songti SC** (宋体) — preferred for formal Chinese documents
- Heiti SC (黑体) — sans-serif
- Kaiti SC (楷体) — calligraphic
- STSong, LiSong Pro — alternate serif

Do NOT use "SimSun" — not available on macOS.

## Bilingual Sync Rules

1. Chinese version (`chinese.typ`) is the source of truth. All factual changes happen there first.
2. English version (`main.typ`) is a full translation — data must match exactly (GPA, rank, project names, dates, awards).
3. When syncing: diff Chinese vs English, flag all discrepancies, rewrite English to match Chinese.
4. Keep email consistent across both versions unless user specifies otherwise.

## Resume Review Convention

When the user asks to review their resume:
- **Only list problems.** Do NOT suggest fixes or give advice unless explicitly asked.
- After each review round, compare with previous version and report only *remaining* issues.
- The user iterates quickly — keep feedback terse, don't repeat fixed items.

## Typst Template Notes

- Template: `@preview/basic-resume:0.2.3`
- Functions: `#edu()`, `#work()`, `#project()`, `#generic-two-by-two()`, `#generic-one-by-two()`
- Dates: `dates-helper(start-date: "Mon YYYY", end-date: "Mon YYYY")` or raw `dates: "Mon YYYY"`
- Links: `link("url")[text]`