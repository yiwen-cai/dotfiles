---
name: bupt-thesis-writer
description: Write, convert, edit, and validate Beijing University of Posts and Telecommunications undergraduate bachelor thesis documents using the local BUPTBachelorThesis LaTeX template. Use when working on BUPT bachelor thesis final papers, LaTeX chapters, abstracts, cover metadata, BibTeX references, appendix content, formatting compliance, or converting Markdown thesis drafts into the BUPT LaTeX repo structure.
---

# BUPT Thesis Writer

## Core Workflow

1. Locate the thesis project or template. Prefer, in order:
   - A path explicitly provided by the user.
   - The current working directory if it contains `main.tex` and `BUPTBachelorThesis.sty`.
   - `$BUPT_THESIS_ROOT` if set.
   - `~/code/BUPTBachelorThesis` if it exists.
   If none can be found, ask the user for the thesis root before editing.
2. Read the active thesis files before editing:
   - `main.tex` for title macros, document order, included chapters, bibliography.
   - `chapters/abstract.tex` for Chinese and English abstracts.
   - `chapters/chapter*.tex` for body chapters.
   - `appendix/appendix*.tex` for appendix material.
   - `ref.bib` for BibTeX references.
3. Preserve the template contract. Do not edit `BUPTBachelorThesis.sty`, `BUPTBachelor.bst`, `.latexmkrc`, assets, or generated files unless the user explicitly asks for style/template changes.
4. Make thesis content changes in chapter/subfile `.tex` files and add new chapters through both a new `chapters/chapterN.tex` file and a matching `\subfile{chapters/chapterN}` entry in `main.tex`.
5. After substantial edits, validate with:
   - `python3 <skill>/scripts/check_bupt_thesis.py <thesis-root>`
   - `latexmk main.tex` from the thesis root when compilation is needed and TeX Live is available.

## When To Load References

- Load `references/template-guide.md` when changing project structure, adding chapters, compiling, managing figures/tables/code/listings, or debugging template behavior.
- Load `references/writing-guide.md` when drafting or revising thesis prose, abstracts, chapter structure, domestic/foreign research status, references, or BUPT formatting rules.

## LaTeX Editing Rules

- Keep every chapter file as a `subfiles` document:
  ```latex
  \documentclass[../main.tex]{subfiles}
  \begin{document}
  ...
  \end{document}
  ```
- Use `\chapter{}`, `\section{}`, `\subsection{}` and let the template number headings.
- Use `\cite{key}` for references, not hard-coded numeric citations.
- Put images under `assets/` or a clear project image folder; use `\includegraphics`.
- Use `figure`, `table`, `longtblr`, `algorithm`, and `lstlisting` environments already supported by the template.
- Keep Chinese technical writing formal, direct, and thesis-oriented. Avoid conversational wording.

## BUPT-Specific Constraints

- Main thesis order is: cover, statement, Chinese abstract and keywords, English abstract and keywords, table of contents, body, references, acknowledgments, appendix.
- `docs/statement.pdf` is required by default because `main.tex` includes it. If using Word-rendered cover instead of the LaTeX cover, `docs/cover.pdf` is also required.
- The main compiler is XeLaTeX through `latexmk main.tex`; output job name is `BUPTBachelorThesis`.
- Reference ordering follows first citation order. Use the template BibTeX flow and keep `ref.bib` clean.
- Reference type markers should use `[J]`, `[C]`, `[M]`, `[P]` semantics through appropriate BibTeX entry types and fields.
- Author display rules: list all authors when there are three or fewer; when more than three, list the first three followed by `等`. English names should be surname first, given-name initials after.
- For English references, avoid unnecessary `language` fields in `ref.bib`; this template may switch `In` to Chinese `见` when `language` is present.
- Treat `Proposal/` as a separate opening-report project, not as part of the final thesis. Its body is a large `longtblr` table and may require manual `\setcounter` control.

## Response Pattern

When editing a thesis:
1. State the files being changed.
2. Make scoped edits only.
3. Report validation commands and results.
4. Mention any missing required template assets, unresolved citations, or compile blockers.
