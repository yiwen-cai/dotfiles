# BUPTBachelorThesis Template Guide

## Repository Layout

Common local template repo:
`~/code/BUPTBachelorThesis`

If the user has the template elsewhere, use the path they provide. When no path is provided,
prefer the current working directory if it contains `main.tex` and `BUPTBachelorThesis.sty`,
then `$BUPT_THESIS_ROOT`, then `~/code/BUPTBachelorThesis`.

Key files:
- `main.tex`: thesis entry point.
- `BUPTBachelorThesis.sty`: page, heading, font, caption, algorithm, listing, bibliography, appendix styles.
- `BUPTBachelor.bst`: BibTeX style.
- `.latexmkrc`: XeLaTeX/latexmk build settings.
- `chapters/abstract.tex`: Chinese and English abstracts.
- `chapters/cover.tex`: LaTeX cover alternative.
- `chapters/chapter1.tex`, `chapters/chapter2.tex`, ...: thesis body.
- `chapters/acknowledgment.tex`: acknowledgments.
- `appendix/appendix1.tex`, ...: appendices.
- `ref.bib`: bibliography.
- `assets/`: school badge/name images and thesis figures.
- `docs/`: required PDFs such as `statement.pdf`; optionally `cover.pdf`.

## Build

Local build:

```bash
latexmk main.tex
```

The template `.latexmkrc` uses:
- `xelatex -file-line-error --shell-escape -src-specials -synctex=1 -interaction=nonstopmode`
- `temp` as output directory
- `BUPTBachelorThesis` as job name
- BibTeX enabled

Overleaf build:
- Upload main thesis files excluding `Proposal/`.
- Use XeLaTeX.

## Main Document Contract

`main.tex` defines:

```latex
\def\thesistitle{...}
\def\thesisenglishtitle{...}
```

Document order:
1. Cover: default `\subfile{chapters/cover}`; Word-rendered `docs/cover.pdf` is available but commented.
2. Statement: `\includepdf[pages=-]{docs/statement.pdf}`.
3. Abstract: `\subfile{chapters/abstract}`.
4. Table of contents.
5. Body chapters: `\subfile{chapters/chapterN}`.
6. References:
   ```latex
   \bibliographystyle{BUPTBachelor}
   \songti\zihao{5}{\bibliography{ref}}
   ```
7. Acknowledgments.
8. Appendix.

When adding a body chapter, create `chapters/chapterN.tex` and add a corresponding `\subfile{chapters/chapterN}` in `main.tex`.

## Formatting Defaults

From `BUPTBachelorThesis.sty`:
- Document class in template: `book`, A4, one-sided, 12pt.
- Chinese font: SimSun; English font: Times New Roman.
- Body text: Songti, 小四, 1.5 line spacing.
- Margins: 2.5 cm on all sides.
- Main header: `北京邮电大学本科毕业设计（论文）`.
- Chapter title: centered, 黑体, 三号.
- Section title: 黑体, 四号.
- Subsection and subsubsection: 黑体, 小四 with indent.
- TOC includes down to subsubsection.
- Figures: `图 章-序号`; tables: `表 章-序号`; equations: `章-序号`.
- Captions use 楷体 五号.
- Citations use natbib numeric superscript style.

## Figures, Tables, Algorithms, Code

Supported packages include:
- `graphicx`, `subcaption` for figures and subfigures.
- `array`, `booktabs`, `multirow`, `tabularx`, `longtable`, `tabularray` for tables.
- `algorithm`, `algorithmicx`, `algpseudocode` for algorithms.
- `listings` for code.

For cross-page tables, prefer `longtblr`:

```latex
\begin{longtblr}[
  caption = {表题},
  label = {tab:label}
]{
  colspec = {|p{4cm}|X[2,l]|X[1,l]|},
  rowhead = 1,
}
\hline
...
\end{longtblr}
```

For appendix headings:

```latex
\appendixsection{附录1\quad 缩略语表}{appendix:abbr}
```

Reference appendix content with:

```latex
\hyperlink{appendix:abbr}{附录1\quad 缩略语表}
```

## Files To Avoid Editing

Do not edit these unless the user asks for template/style changes:
- `BUPTBachelorThesis.sty`
- `BUPTBachelor.bst`
- `.latexmkrc`
- `assets/bupt-*`
- generated files under `temp/`

## Opening Report

`Proposal/` is an independent LaTeX project for the opening report:
- Entry point: `Proposal/main.tex`.
- Class: `Proposal/BUPTBachelorProposal.cls`.
- Bibliography: `Proposal/ref.bib`.
- Build:
  ```bash
  cd Proposal
  latexmk main.tex
  ```
- The body is written inside a large `longtblr` table. Cross-page content may need manual table splitting.
- Section and subsection counters inside the table may need explicit `\setcounter` control.
- Do not mix opening-report files with final-thesis chapters.
