# BUPT Bachelor Thesis Writing Guide

## Overall Thesis Shape

Use a conventional engineering thesis structure unless the user gives a school-specific outline:

1. 绪论
   - 研究背景与意义
   - 国内外研究现状
   - 研究问题
   - 本文工作
   - 论文结构
2. 相关技术
3. 系统需求或总体设计
4. 关键技术/算法/算子设计
5. 系统实现
6. 实验设计与结果分析
7. 总结与展望

For implementation-heavy computer science projects, keep the thesis focus on:
- Problem background.
- Technical challenge.
- System architecture.
- Key module design.
- Correctness and performance evaluation.
- Reproducibility and limitations.

## Abstracts

Chinese abstract:
- One paragraph or several coherent paragraphs.
- Cover background, problem, method/system, main work, experiment result, conclusion.
- Avoid citations, figures, tables, and unexplained abbreviations.
- Keywords use concise terms separated by `\quad` in the template.

English abstract:
- Translate meaning rather than word order.
- Keep terminology consistent with the Chinese abstract.
- Use `full-batch`, `SpMM`, `SDDMM`, `CUDA`, model/backend names consistently.

## Chapter Writing Rules

- Start each chapter with a short orientation paragraph.
- Use section titles that describe content, not vague labels.
- Avoid unsupported claims such as “显著提升” unless followed by quantified results.
- When discussing performance, state the metric and scope: steady epoch, cached E2E, cold-start, preprocessing, memory, accuracy.
- When comparing systems, state whether data input, preprocessing, backend, and hardware are the same.
- For CUDA/kernel work, distinguish algorithm semantics from implementation optimization.
- For fallback or correctness gates, explain when the optimized backend is valid and when it falls back.

## Domestic And Foreign Research Status

Organize by technical lineage instead of listing papers one by one:
1. GNN model development.
2. GNN frameworks and benchmark datasets.
3. Large-scale training and sampling.
4. GPU sparse operators and graph preprocessing.
5. Gaps addressed by the thesis.

Each paragraph should end with a synthesis sentence that connects prior work to this thesis.

## References

Hard requirements commonly used for this thesis:
- List references in the order they first appear in the text.
- Use at least 20 references.
- Use at least 30% references from the most recent three years when required by the school/task.
- Use `[J]` for journals, `[C]` for conference papers, `[M]` for books/manuals, `[P]` for patents.
- If author count is fewer than or equal to three, list all authors.
- If author count is greater than three, list the first three authors followed by `等`.
- Separate authors with commas.
- Use surname-first formatting for both Chinese and foreign names.

In LaTeX, prefer BibTeX entries over hand-written bibliography text. Keep citation keys stable and cite with `\cite{key}`.

For English BibTeX entries in this template, remove `language` unless Chinese `见` output is desired.

## Markdown-To-LaTeX Conversion Notes

- `#` maps to `\chapter{}` only for chapter files; do not create a chapter inside `abstract.tex`.
- `##` maps to `\section{}`.
- `###` maps to `\subsection{}`.
- Inline code can use `\texttt{}` for short identifiers.
- Long code blocks should use `lstlisting`.
- Markdown tables should become `table`/`tabular` or `longtblr`.
- Markdown links in prose should be converted to citations, footnotes, or plain URLs depending on context.
- Keep math in LaTeX form.

