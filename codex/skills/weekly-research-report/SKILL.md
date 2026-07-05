---
name: weekly-research-report
description: Use when helping the user draft, save, and prepare weekly research reports for their advisor as Markdown files
  and email-ready content.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Weekly Research Report

## Overview

This skill defines the user's recurring workflow for writing weekly advisor reports. The report must be saved as a Markdown file under `/Users/yiwencai/Documents/study/weekpaper` and should be suitable for sending by email to the advisor.

The report should use precise academic and research language. It must avoid vague qualitative wording when quantitative metrics are available. Performance, training, inference, and experiment results should be described with concrete values such as speedup ratio, loss value, accuracy, throughput, latency, GPU memory usage, token/s, wall-clock time, or ablation deltas.

## When to Use

Use this skill when the user asks to:

- Write this week's report, weekly report, 周报, or advisor update.
- Summarize weekly research progress into a Markdown file.
- Prepare an email-ready report titled `xxx周报`.
- Continue a weekly email thread by sending the new weekly report as a reply to last week's report.
- Convert experiment notes, logs, or research progress into a polished advisor-facing weekly report.

Do not use this skill for generic daily notes, casual summaries, or non-research status updates unless the user explicitly wants the advisor weekly report format.

## Storage Location

All weekly reports must be saved as Markdown files in:

```text
/Users/yiwencai/Documents/study/weekpaper
```

Before writing a report:

1. Ensure the directory exists.
2. Inspect existing files to infer the naming convention if any exists.
3. If no convention exists, use a clear filename such as:

```text
YYYY-MM-DD-weekly-report.md
```

Use the report date as the Saturday or current date unless the user specifies a reporting period.

## Required Report Sections

Every report must include these three sections exactly:

```markdown
# xxx周报

## 本周进展

## 遇到问题

## 下周计划
```

The title `xxx周报` should be replaced with the appropriate subject. If the user does not specify `xxx`, infer it from the main project or research direction. If still unclear, use `科研进展周报`.

## Content Requirements

### 本周进展

Include concrete completed work and measurable progress. Prefer this structure:

- Research reading and theoretical analysis.
- Method design or implementation progress.
- Experiment setup and configuration.
- Quantitative experiment results.
- Code, dataset, benchmark, or documentation progress.

Use precise statements such as:

```text
完成了基于 vLLM 的批量推理实验配置，batch size 从 8 扩展到 32，吞吐量由 210 tokens/s 提升到 680 tokens/s，加速比为 3.24 倍。
```

Avoid vague statements such as:

```text
效果更好，速度更快，loss 比较低。
```

Replace them with quantified descriptions:

```text
验证集 loss 从 2.31 降至 1.87，相对下降 19.05%；端到端推理延迟从 142 ms 降至 96 ms，降低 32.39%。
```

### 遇到问题

Describe blockers using technical and causal language:

- What failed or remains unresolved.
- Where it occurs: data, model, training, inference, evaluation, deployment, environment, or theory.
- Evidence: logs, metrics, error rate, reproduction condition, affected configuration.
- Current hypothesis and next diagnostic step.

Example:

```text
在 8 卡 H100 环境下进行 ZeRO-3 训练时，global batch size=512 的配置在第 1,240 step 后出现 loss spike，training loss 从 1.92 突增至 3.48。初步判断与学习率 warmup 结束后的梯度范数波动有关，下周计划记录 grad_norm 与激活值分布以定位原因。
```

### 下周计划

Plans must be actionable and verifiable. Include:

- Specific tasks.
- Expected output or metric.
- Experiment matrix if relevant.
- Completion criteria.

Example:

```text
完成 LoRA rank ∈ {8, 16, 32} 的消融实验，比较验证集 loss、BLEU/ROUGE 或任务准确率，并输出包含显存占用、训练时长和推理吞吐量的对比表。
```

## Quantitative Reporting Rules

When performance or experiment effects are discussed, always use quantitative metrics when available:

- Speed: speedup ratio, latency, throughput, wall-clock time.
- Training: train loss, validation loss, perplexity, convergence step, gradient norm.
- Evaluation: accuracy, F1, BLEU, ROUGE, pass@k, win rate, reward score.
- Resource usage: GPU memory, GPU utilization, CPU memory, disk usage, network bandwidth.
- Scaling: number of GPUs, batch size, sequence length, context length, tokens processed.
- Cost: API cost, GPU hours, samples per dollar if relevant.

If values are missing, do not invent them. Write a placeholder such as:

```text
（待补充：验证集 loss、吞吐量、显存占用）
```

or ask the user for the missing metric if the report cannot be completed reliably.

## Attachments and Supporting Materials

If there are concrete technical plans, experiment results, figures, tables, logs, or scripts, include an `附件` section at the end of the Markdown file:

```markdown
## 附件

- `path/to/experiment-table.csv`：实验结果汇总表。
- `path/to/ablation.md`：消融实验配置与结论。
- `path/to/figure.png`：训练 loss 曲线。
```

Only add this section when there are real supporting materials or the user provides files. Do not fabricate attachments.

## Email Requirements

Email subject:

```text
xxx周报
```

Threading requirement:

- Each week, send the report by replying to last week's weekly report email thread when possible.
- If using an email CLI or API, first search for the latest sent or received email whose subject contains `周报`.
- Reply to that thread instead of creating a new thread.
- If no previous weekly report thread can be found, create a new email with subject `xxx周报`.

Email body can be the Markdown report body, or a concise greeting plus the report content. Preserve the three required sections.

## Interaction Protocol

Before writing any weekly report, follow this sequence strictly:

1. The user must first provide the approximate content of this week's work. Do not draft or create the Markdown file before receiving this initial input.
2. Discuss the concrete report content with the user. Organize the raw input into `本周进展`, `遇到问题`, and `下周计划`, and explain any proposed framing or emphasis.
3. Ask targeted follow-up questions for unclear or missing information, especially:
   - exact project or report title for `xxx周报`;
   - quantitative metrics such as loss, speedup ratio, accuracy, throughput, latency, GPU memory, training steps, or dataset size;
   - unresolved technical issues and diagnostic evidence;
   - next-week completion criteria;
   - whether attachments such as experiment tables, figures, logs, or technical plans should be included.
4. If the user says "check the remote server" or "look at the code on lab" instead of describing work verbally, connect to the remote environment and gather metrics directly (see "Gathering Context from Remote Code" above).
5. Only after the content is sufficiently clarified and the user agrees with the planned structure, write the Markdown report file.
6. If the user explicitly asks for a quick draft before all metrics are known, use `待补充` placeholders for missing values, but still complete the discussion step first.

Do not silently infer major technical claims, metrics, or next-step plans without confirming them with the user.

## Terminology Preferences

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

- **Remote path**: `/public/home/caiyiwen/code/BUPTBachelorThesis/`
- **Key files for status checks**:
  - `progress.md` — chronological modification log with per-session summaries
  - `todo.md` — checklist of pending and completed modifications
  - `suggestions.md` — advisor/internal review feedback text
  - `task_plan.md` — phased modification plan with completion status
  - `temp/BUPTBachelorThesis.pdf` — latest compiled PDF
- **Build command**: `latexmk main.tex` (run from the repo root)
- **Validation command**: `python3 /public/home/caiyiwen/.codex/skills/bupt-thesis-writer/scripts/check_bupt_thesis.py /public/home/caiyiwen/code/BUPTBachelorThesis`

When thesis status is unclear, read these files before asking the user.

## Graduation Design Record-Table Assistance

When the user asks to fill in blank weeks of the graduation design (毕业设计) advisor record table (教师指导本科毕业设计_论文_记录表), do NOT modify the .docx file directly. Instead:

1. Read the existing filled weeks from the record table to understand the timeline, writing style, and research progression.
2. Read the thesis PDF or .docx to extract the actual research content, experiments, and milestones for the blank periods.
3. Cross-reference any local project files (中期检查, code notes, experiment logs) for additional context.
4. Generate text content only, formatted to match the existing record-table style (academic advisor tone, bi-weekly summaries, specific technical details).
5. Present the content as plain text that the user can copy and paste into the .docx themselves.

Key style rules for record-table entries:
- Each entry covers a 2-week period (第N-M周记录).
- Write from the advisor's perspective (指导教师签字 + date).
- Include concrete technical guidance: specific algorithms discussed, design decisions made, experiments conducted.
- Reference quantitative results when available (speedup ratios, accuracy improvements, structural metrics like expansion ratio).
- Mention paper-writing milestones (draft completion, revision feedback, format checks) in later weeks.
- Connect each period logically to the next, showing progressive research development.
- Do NOT invent metrics; use values from the thesis or mark as approximate if uncertain.

The record table is typically located at:
```text
/Users/yiwencai/Documents/study/毕业设计/北京邮电大学教师指导本科毕业设计_论文_记录表.docx
```

The thesis PDF is typically at:
```text
/Users/yiwencai/Documents/study/毕业设计/一种基于 GPU 上张量核心的图神经网络训练系统的设计与实现.pdf
```

## Gathering Context from Remote Code

When the user's weekly work includes coding on a remote server (e.g., CS336 assignments on `a800`), gather quantitative metrics directly from the remote environment rather than relying solely on the user's memory or wiki logs:

1. **Connect to the remote server** (e.g., `ssh a800`) and navigate to the project directory.
2. **Run the test suite** to get exact pass/fail counts: `pytest tests/ -v`.
3. **Check code metrics**: `wc -l` on implementation files, `git diff --stat` for modified files.
4. **Inspect git history** if available: `git log --oneline` for commit activity.
5. **Verify test details**: for xfailed tests, check whether they are expected failures (test framework markers) or actual regressions.
6. **Read source code directly** when the user says "implementation is done" — inspect the actual file to confirm completeness and catch unimplemented stubs or `NotImplementedError` remnants.

Example workflow for CS336 tokenizer progress:
```bash
ssh a800 "export PATH='/storage/caiyiwen/.local/bin:\$PATH' && cd /storage/caiyiwen/code/cs336/assignment/assignment1-basics && uv run pytest tests/test_tokenizer.py -v"
```

**Extended pattern for CS336 Assignment 2 systems work** (benchmark + profiling):
```bash
# 1. Check implementation status and git diff
ssh a800 "cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems && git status --short && git diff --stat"

# 2. Run attention tests specifically
ssh a800 "export PATH='/storage/caiyiwen/.local/bin:\$PATH' && cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems && uv run pytest tests/test_attention.py -v --tb=short"

# 3. Run full test suite and capture summary
ssh a800 "export PATH='/storage/caiyiwen/.local/bin:\$PATH' && cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems && uv run pytest tests/ -v --tb=short 2>&1 | tail -30"

# 4. Run benchmark with formal scale configuration
ssh a800 "export PATH='/storage/caiyiwen/.local/bin:\$PATH' && cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems && uv run python cs336_systems/benchmark.py --batch-size 4 --context-length 512 --num-layers 12 --d-model 768 --num-heads 12 --d-ff 3072 --warmup-steps 5 --measure-steps 10 --mode train"

# 5. Extract Nsight Systems profiling data
ssh a800 "cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems && cat traces/formal/summary_kernel.csv"
ssh a800 "cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems && cat traces/formal/summary_train_nvtx.csv"
```

When benchmark scripts support NVTX annotation (via `torch.cuda.nvtx.range_push/pop`), the profiling data can be extracted at two levels:
- **Kernel level**: `summary_kernel.csv` shows top GPU kernels (e.g., `ampere_sgemm_128x128_nn`, elementwise kernels) with percentage, call count, and average nanoseconds.
- **NVTX range level**: `summary_train_nvtx.csv` shows logical phases (forward, backward, optimizer) with total milliseconds, instances, and average per instance.

Always include the exact test counts (e.g., "24 passed, 1 xfailed") and test execution time in the report. Do not round or estimate metrics gathered from the remote environment. When test status changes week-over-week, quantify the delta (e.g., "from 14 failed to 8 failed, FlashAttention 6 tests now passing").

## Recommended Workflow

1. Gather context:
   - Ask the user for this week's progress, problems, next-week plan, metrics, and attachments if not already provided.
   - If the user points to files, logs, Git commits, experiment outputs, or notes, inspect them with tools before drafting.
2. Create or update the Markdown report under `/Users/yiwencai/Documents/study/weekpaper`.
3. Ensure the report contains `本周进展`, `遇到问题`, and `下周计划`.
4. Check for vague phrases and replace them with precise technical descriptions or metric placeholders.
5. If sending email is requested, search for the previous `周报` email and reply in-thread when possible.
6. Verify the saved file path and summarize what was created.

## Quality Checklist

Before finalizing, verify:

- [ ] The Markdown file is saved under `/Users/yiwencai/Documents/study/weekpaper`.
- [ ] The report has title `xxx周报`.
- [ ] It includes `本周进展`, `遇到问题`, and `下周计划`.
- [ ] Research terminology is clear and precise.
- [ ] Quantitative effects use numbers instead of vague adjectives.
- [ ] Missing metrics are explicitly marked as `待补充` rather than invented.
- [ ] Real attachments are listed only when they exist.
- [ ] If email is sent, it replies to last week's weekly report thread when possible.

## References

- `references/first-week-report-session.md` — Reusable details from the first weekly report workflow, including confirmed source paths, CS336 llmwiki pages, thesis metrics, and wording choices.
- `references/third-week-report-session.md` — Remote code gathering pattern, thesis remote context files, CS336 tokenizer completion metrics, and established naming convention.
- `references/sixth-week-report-session.md` — CS336 Assignment 2 status-gathering commands, KV Cache first-presentation material structure, benchmark sanity-check metrics, and remote SSH `$PATH` escaping pitfall.
- `references/seventh-week-report-session.md` — CS336 FlashAttention test verification, benchmark formal experiment matrix, Nsight Systems profiling data extraction (kernel-level + NVTX range-level CSV analysis), and quantitative test status delta reporting (14 failed → 8 failed).
- `references/graduation-design-record-table.md` — Workflow for filling blank weeks in the graduation design advisor record table: text-only output, style rules, and cross-referencing thesis content.


1. Inventing metrics.
   Never fabricate loss values, speedup ratios, accuracy, or resource usage. Use placeholders or ask for data.

2. Writing vague progress.
   Avoid phrases like `效果不错`, `性能更高`, `速度更快`, `问题比较多`. Replace them with measured values, failure conditions, or diagnostic hypotheses.

3. Forgetting the storage path.
   Reports belong in `/Users/yiwencai/Documents/study/weekpaper`, not the current working directory.

4. Starting a new email thread every week.
   The user wants each weekly report to continue from last week's email thread when possible.

5. Adding fake attachments.
   Only include attachments that exist or are explicitly provided by the user.