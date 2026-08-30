---
name: software-quality-workflows
description: 'Software quality umbrella: TDD, systematic debugging, pre-commit verification, multi-reviewer simplification,
  and exploratory QA/dogfooding.'
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Software Quality Workflows

Use this class-level umbrella for making software changes safely: write tests first, debug from evidence, verify changes before commit, simplify recent diffs with targeted reviewers, and dogfood web applications with structured evidence.

## Workflow selector

| Situation | Use this section |
|---|---|
| New feature, bug fix, behavior change | TDD loop |
| Test/build/runtime failure or unexpected behavior | Systematic debugging |
| Before commit/push/merge | Pre-commit verification |
| User explicitly asks to simplify/review recent changes | Parallel simplify review |
| User asks to test a web app in-browser | Exploratory QA / dogfooding |

## Test-driven development

Core law: no production code without a failing test first.

RED-GREEN-REFACTOR:

1. RED: write one minimal behavior test with a descriptive name.
2. Run the exact test and verify it fails for the expected reason, not a typo.
3. GREEN: write the smallest code that makes it pass.
4. Run the exact test, then targeted/full tests for regressions.
5. REFACTOR only while tests stay green.

```bash
pytest tests/test_feature.py::test_specific_behavior -v
pytest tests/ -q
```

Red flags: code before test, tests passing immediately, manual-only testing, or keeping implementation as "reference" while claiming TDD.

## Systematic debugging

Core law: no fixes without root-cause investigation first.

Four phases:

1. Root cause investigation: read full errors, reproduce, inspect recent changes, trace data flow, instrument component boundaries.
2. Pattern analysis: find working examples and compare exact differences.
3. Hypothesis testing: state one hypothesis and test it minimally.
4. Implementation: add regression test, fix root cause, verify.

Useful commands:

```bash
pytest tests/test_module.py::test_name -v --tb=long
git log --oneline -10
git diff
```

If three fixes fail, stop and question the architecture instead of attempting fix #4.

### TypeScript/Vite missing export from `.js` residue

When Vite/Rolldown reports a missing export from a `.js` path but the matching `.ts` source exports it, check for ignored generated `.js` files under source directories before editing code. See `references/ignored-js-residue-vite.md` for the diagnosis and safe cleanup pattern.

### Shell/Git conflict debugging reference

The former `systematic-debugging` skill had detailed shell merge-conflict handling. It has been preserved in `references/zsh-plugin-debugging.md`. Key pattern: inspect with `file`, byte tools, `bash -n`, conflict-marker grep, and `git show :2:` / `:3:` before resolving.

## Frontend scroll/auto-follow debugging

For scroll-position bugs in chat/message-list Vue components — jumping to top, not staying at latest message, auto-follow breaking during streaming. See `references/frontend-scroll-debugging.md` for the full technique.

Six common traps:
1. `:key` on VirtualMessageList causing full component recreation — all scroll state lost.
2. `userDetachedFromBottom` threshold (`delta < -1`) too sensitive — tiny DOM jitter during streaming detaches the user.
3. `restoreViewportPosition` vs `handleResize` competition — ResizeObserver overrides the manual scroll restore.
4. Multiple watchers calling `scrollToBottom` during initialization — rAF loops fight each other.
5. `handleWheel` detaches on any upward scroll event, even 2px.
6. Missing `overflow: hidden` on message rows — markdown nesting pushes content beyond viewport.

## Pre-commit verification

Use after implementing changes, before commit/push/ship. Core principle: no agent should verify its own work; use fresh context when possible.

Steps:

1. Capture diff: `git diff --cached`; if empty, `git diff` or `git diff HEAD~1 HEAD`.
2. Scan added lines for secrets, shell injection, eval/exec, unsafe pickle, SQL interpolation.
3. Run project tests/lints, comparing against baseline if the repo already has failures.
4. Self-review checklist: secrets, validation, parameterized queries, path handling, error handling, debug prints, tests.
5. Ask an independent reviewer subagent to return a JSON verdict when available.
6. Auto-fix only the reported issues, bounded to two cycles.
7. Commit only after verification passes.

Static scan starters:

```bash
git diff --cached | grep '^+' | grep -iE '(api_key|secret|password|token|passwd)\s*=\s*['\''"][^'\''"]{6,}['\''"]'
git diff --cached | grep '^+' | grep -E 'os\.system\(|subprocess.*shell=True'
git diff --cached | grep '^+' | grep -E '\beval\(|\bexec\('
git diff --cached | grep '^+' | grep -E 'pickle\.loads?\('
git diff --cached | grep '^+' | grep -E 'execute\(f"|\.format\(.*SELECT|\.format\(.*INSERT'
```

## Parallel simplify review

Use only when the user explicitly asks to simplify/clean up/review recent changes. It is token-expensive and should not run after every edit.

1. Identify the diff: `git diff`, `git diff HEAD`, `git diff --staged`, `git diff HEAD~1`, or scoped file diff.
2. Launch up to three reviewers in parallel:
   - Reuse: duplicated functionality, missed helpers/constants/patterns.
   - Quality: redundant state, parameter sprawl, copy-paste variation, leaky abstractions, stringly typing.
   - Efficiency: redundant work, N+1s, missed concurrency, hot-path bloat, TOCTOU, leaks.
3. Require concrete evidence (`file:line`) and confidence levels.
4. Aggregate/dedupe findings, discard weak positives, resolve conflicts by correctness > user focus > readability/reuse > micro-performance.
5. Apply minimal scoped fixes unless the user asked for dry run.
6. Verify targeted tests/lints and summarize applied/skipped findings.

## Spike / feasibility prototyping

Use when the user wants to feel out an idea before committing to a production build: "spike this", "quick prototype", "is this possible?", "compare A vs B", or "try this before we build it".

Core loop: decompose → research → build → verdict.

1. Decompose the idea into 2-5 independent feasibility questions, ordered by risk. Use Given/When/Then framing and comparison suffixes (`002a`, `002b`) when testing alternative approaches.
2. Research just enough to pick credible tools/libraries. Skip research for pure logic with no external dependencies.
3. Build disposable artifacts under `spikes/NNN-descriptive-name/` (or `.planning/spikes/` if the project uses GSD conventions). Prefer observable output: CLI, small HTML page, tiny endpoint, or focused test.
4. Test edge cases and surprising findings, not just the happy path.
5. End each spike README with:
   - `## Verdict: VALIDATED | PARTIAL | INVALIDATED`
   - what worked, what did not, surprises, and recommendation for the real build.

Keep spike code throwaway. If it needs days of cleanup to become production code, the spike was scoped too broadly.

## Exploratory QA / dogfooding

Use for systematic browser QA of a web app.

Five phases:

1. Plan: create output dir, map scope and key flows.
2. Explore: navigate, snapshot DOM, check console, visually inspect, interact with controls/forms/keyboards.
3. Collect evidence: screenshot, URL, steps, expected/actual, console errors.
4. Categorize: dedupe, classify severity/category, sort.
5. Report: executive summary, issue sections, screenshot references, summary table, testing notes.

Always check console after navigation and significant interactions. Test valid and invalid inputs, empty states, long text, special characters, scrolling, and navigation flows.

Support files migrated from dogfood:

- `references/issue-taxonomy.md`
- `templates/dogfood-report-template.md`

## Completion checklist

- Reproduced or tested the relevant behavior with real commands/tools.
- Claims are grounded in test output, diff output, browser evidence, or API readback.
- No broad refactors hidden inside quality passes.
- User-visible side effects are confirmed or explicitly reported as skipped.