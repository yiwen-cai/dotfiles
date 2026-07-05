# PDF-to-HTML Paper Notes Workflow

Use this reference when the user asks to create a browsable note library from a folder of academic PDFs, especially for LLM systems surveys.

## Output contract

Create a class-level folder such as `paper_notes/` under the active workspace:

- `paper_notes/index.html`: browsable index of all papers.
- `paper_notes/manifest.json`: machine-readable metadata for every generated note.
- `paper_notes/<paper_slug>/index.html`: one HTML note per paper.
- `paper_notes/<paper_slug>/assets/`: rendered PDF pages used as figures and experiment charts.

Each HTML note should contain:

1. Paper source: local PDF path and arXiv link when extractable.
2. Authors.
3. Venue/version. If the PDF does not clearly state a conference/venue, write `未在 PDF 中明确标注` rather than guessing.
4. Paper overview.
5. Core technical principle.
6. Experiment analysis.
7. Limitations and future directions.
8. Method/system figure pages rendered from the PDF.
9. Experiment table/plot pages rendered from the PDF.
10. Evidence excerpts copied from the extracted PDF text.

## Grounding rules

- Do not invent experiment numbers, conference names, model names, datasets, speedups, or compression ratios.
- If a value is not present in the extracted PDF text or rendered PDF page, omit it or mark it as not clearly stated.
- Prefer embedding rendered PDF pages for charts/tables over manually recreating charts from memory.
- Keep extracted evidence excerpts visible in each note so claims are auditable.
- If a PDF is corrupt, try re-downloading from the arXiv ID in the filename or text, then rerun PDF validation.

## Recommended implementation

A robust script should:

1. List all `*.pdf` files under `paper/`.
2. Extract full text via `pdftotext -layout`.
3. Get page counts via `pdfinfo`.
4. Extract metadata from first page and text patterns:
   - Title from first substantive title-like line.
   - Authors from following non-affiliation line.
   - arXiv ID from `arXiv:` text or filename.
   - Venue from explicit `Published as`, `Proceedings`, or known conference patterns.
5. Select likely method pages using keywords such as `method`, `approach`, `algorithm`, `architecture`, `framework`, `system`, `quantization`, `compression`, `eviction`.
6. Select likely experiment pages using keywords such as `experiment`, `evaluation`, `benchmark`, `results`, `ablation`, `throughput`, `latency`, `perplexity`, `accuracy`, `LongBench`, `RULER`, `Needle`, `Table`, `Figure`.
7. Render selected pages with `pdftoppm -png` and embed them as images.
8. Generate `index.html` and per-paper HTML with consistent styling.
9. Verify counts and assets:
   - PDF count equals note count.
   - `manifest.json` count equals note count.
   - Every `src='assets/...'` reference exists.

## User-specific presentation preference

For this user, paper notes should be in Chinese and organized as:

- 论文出处
- 作者
- 会议/版本
- 论文概括
- 核心技术原理讲解
- 实验分析
- 局限性和展望

The user explicitly values 图文并茂 notes. Core technical principle sections should include method/system figures when possible. Experiment analysis should include paper-extracted tables or plots, preferably as rendered PDF pages.

## Python formatting

When writing a Python generator for this user, run `ruff format` after editing. Avoid Chinese characters and Chinese punctuation in code outside comments if possible; put Chinese UI strings in data structures deliberately if the generated HTML must be Chinese.
