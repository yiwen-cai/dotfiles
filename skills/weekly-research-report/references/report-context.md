

For weekly reports, write `实验室 H100 服务器` instead of `lab 服务器` when referring to the user's remote GPU machine. Avoid exposing internal host aliases such as `lab` in advisor-facing report prose unless the user explicitly asks for implementation details.

## User-Specific Context Sources

For this user, recurring source locations are:

- Weekly report output directory: `/Users/yiwencai/Documents/study/weekpaper`.
- Study materials root: `/Users/yiwencai/Documents/study`.
- Graduation thesis materials: `/Users/yiwencai/Documents/study/毕业设计`.
- LLM wiki: `$WIKI_PATH` if set, otherwise `/Users/yiwencai/wiki`.
- CS336 wiki pages commonly used for weekly reports:
  - `/Users/yiwencai/wiki/concepts/cs336-language-modeling.md`
  - `/Users/yiwencai/wiki/queries/cs336-learning-plan.md`
  - `/Users/yiwencai/wiki/queries/cs336-day1-completion.md`
  - `/Users/yiwencai/wiki/queries/cs336-day2-plan.md`

When the user mentions `wiki`, `llmwiki`, or CS336 learning records, orient with the `llm-wiki` skill first and read `SCHEMA.md`, `index.md`, and relevant CS336 pages before drafting.

## Thesis Context on Remote Server

The user's graduation thesis LaTeX source and build artifacts are maintained on the lab server, not locally:

- **Remote path**: `$HOME/code/BUPTBachelorThesis/`
- **Key files for status checks**:
  - `progress.md` — chronological modification log with per-session summaries
  - `todo.md` — checklist of pending and completed modifications
  - `suggestions.md` — advisor/internal review feedback text
  - `task_plan.md` — phased modification plan with completion status
  - `temp/BUPTBachelorThesis.pdf` — latest compiled PDF
- **Build command**: `latexmk main.tex` (run from the repo root)
- **Validation command**: `python3 <thesis-project-skill>/scripts/check_bupt_thesis.py $HOME/code/BUPTBachelorThesis`（该技能同时部署于各工具的 skills 目录）

When thesis status is unclear, read these files before asking the user.

