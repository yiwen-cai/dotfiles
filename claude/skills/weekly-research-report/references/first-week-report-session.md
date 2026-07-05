# First Weekly Report Session Notes

This reference records reusable details from the first advisor-weekly-report workflow.

## Confirmed user workflow

- The report title can be user-specified, e.g. `第一周周报`.
- Do not write the Markdown file immediately after receiving a broad request. First gather the user's rough weekly work, inspect provided evidence, discuss the proposed structure, ask targeted questions, and only write after confirmation.
- If the user says there were no concrete problems, write `没有出现阻塞性问题` and optionally describe follow-up risk points, rather than inventing blockers.
- If the user says `下周再说` but the report format requires `下周计划`, offer a conservative plan option and get confirmation.

## Evidence sources used

Graduation thesis PDFs were found under:

```text
/Users/yiwencai/Documents/study/毕业设计
```

The primary thesis topic was:

```text
一种基于 GPU 上张量核心的图神经网络训练系统的设计与实现
```

The session used these thesis metrics after extracting the PDF/report:

- Voltrix achieved 1.571x to 3.307x steady-state training epoch speedup on Reddit-rabbit-fg and FraudYelp-RSR-rabbit.
- Fused3S achieved about 1.21x and 1.71x end-to-end median time speedups over DGL DotGAT on ogbn-arxiv and FraudYelp-RSR-rabbit.
- Independent Q/K/V projection improved accuracy on ogbn-arxiv by about 4.61 percentage points.
- Plagiarism check: total text duplication ratio 0.5%, total word count 48711.

CS336 materials should be taken from the LLM wiki, not only from `/Users/yiwencai/Documents/code/cs336/README.md`. Relevant files observed:

```text
/Users/yiwencai/wiki/concepts/cs336-language-modeling.md
/Users/yiwencai/wiki/queries/cs336-learning-plan.md
/Users/yiwencai/wiki/queries/cs336-day1-completion.md
/Users/yiwencai/wiki/queries/cs336-day2-plan.md
```

## Wording choices confirmed

- Use `内审结果反馈` instead of `导师反馈` when describing the next thesis revision trigger for this report.
- No attachments should be added unless the user explicitly requests them.

## Output example path

```text
/Users/yiwencai/Documents/study/weekpaper/第一周周报.md
```
