---
name: paper-note-generator
description: Given a paper title/link/arXiv ID or local PDF path, generate a paper note HTML in the established format with
  source info, summary, core technology, experiment analysis, and limitations.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Paper Note Generator

## When to Use

When the user asks to create a paper note / 论文笔记 / 文献笔记 for a research paper. Accepts:

- **arXiv URL** or **arXiv ID**: `https://arxiv.org/abs/XXXX.XXXXX` or `XXXX.XXXXX`
- **Paper title**: will search for it on arXiv/semantic scholar
- **Local PDF path**: absolute path to a PDF file on disk
- **Direct PDF URL**: any URL ending in `.pdf`

Outputs an HTML note following the established format at `paper_notes/<slug>/index.html`, optionally updating the index page.

## Prerequisites

```bash
# Required system tools (check with: which pdftotext pdftoppm pdfinfo)
brew install poppler   # if missing: provides pdftotext, pdftoppm, pdfinfo
```

## Workflow

### Phase 1 — Get the PDF

Determine the PDF source by priority:

1. **Local path**: if user provides an absolute path to a `.pdf`, use it directly.
2. **arXiv URL**: download via `https://arxiv.org/pdf/<arxiv_id>.pdf`.
3. **arXiv ID**: construct URL and download.
4. **Paper title**: search web for `"<paper title>" arXiv` to find the arXiv page, then construct PDF URL.
5. **arXiv abstract page**: extract the abstract page URL, scrape it for the PDF link (usually `/pdf/XXXX.XXXXX`), then download.

**Naming convention**: `<num>_<short_name>_<arxiv_id>.pdf` where `<num>` is a zero-padded sequence number (check existing paper files to determine the next number).

```bash
# Download from arXiv
curl -SL "https://arxiv.org/pdf/2405.04434" -o "07_deepseek_v2_mla_2405.04434.pdf"
```

**If download fails or PDF is protected**: try the arXiv HTML abstract page and use `web_extract`, or ask the user for a direct PDF link.

### Phase 1.5 — Supplement with Web Research

Before diving into PDF extraction, search for supplementary materials that enrich the note. This is especially important for recent papers with code releases:

```python
# Search for code repo, blog posts, project page
web_search("\"<paper short name>\" code GitHub")
web_search("\"<paper short name>\" blog lmsys")
web_search("<paper short name> <framework> integration")
```

**What to collect (3–5 minutes max):**
- Official GitHub repo (code, checkpoints, Hugging Face model card)
- Project / demo page
- Third-party blog posts (lmsys, Hugging Face, technical deep dives from Modal, Fireworks, etc.)
- Production integration guides (SGLang / vLLM / Transformers)

**How to use supplementary sources:**
- **Code repos** often have better deployment instructions and practical block-size recommendations than the paper itself.
- **Third-party blogs** validate the paper's claims with independent benchmarks (e.g., lmsys + Modal verified DFlash on Qwen3.5-397B).
- **Hugging Face model cards** document dtype notes, memory requirements, and usage examples.
- **Always cite both paper and supplementary sources** — a note that only repeats the paper is less useful than one that tells the reader where to find the code and how to actually run it.

**When to skip:** Very old paper with no code release; or when the user explicitly asks for "just the paper".

Record URLs and key findings; they will be integrated into the note's appropriate sections (e.g., production deployment code in 实验分析 or separate discussion).

> **Concrete example:** See `references/supplementary-research-example.md` for how this phase was applied to the DFlash paper — search queries used, sourcing breakdown, and findings that only came from supplementary sources.

### Phase 2 — Extract Text and Metadata

**Preferred path (when PDF is accessible and poppler is available):** Run the helper script:

```bash
python3 SKILL_DIR/scripts/generate_paper_note.py \
  --pdf "/path/to/paper.pdf" \
  --output "/path/to/paper_notes" \
  --slug "07_deepseek_v2_mla_2405.04434"
```

This produces:
- `paper.txt` — full extracted text, used only as source material and evidence for the agent
- `assets/method_pXX.png` — method/architecture pages
- `assets/experiment_pXX.png` — experimental results pages
- A JSON manifest entry printed to stdout with all metadata

Important: `paper.txt` is **not** final note content. The final HTML must be rewritten in Chinese by the agent; do not paste English extracted text into the note body.

**Alternative path (arXiv HTML paper available, or poppler unavailable):** Use `web_extract` on the arXiv HTML abstract page (`https://arxiv.org/html/<id>v2`) — this provides structured markdown text without PDF tooling. You will miss rendered figures; supplement those with results from Phase 1.5 web research or directly link to the PDF for figure references. Mark missing figures as "PDF 图表" in the note.

### Phase 3 — Read and Understand the Paper

1. Read the extracted text from `paper.txt` (focus on abstract, introduction, method sections, experiments, conclusion).
2. Use the rendered page images (`MEDIA:assets/method_pXX.png`) to understand figures, architecture diagrams, and experiment charts.
3. For **charts and data**: only use what is visible in the PDF images or explicitly stated in the text. If data is missing, label it explicitly as "论文中未找到该数据".

### Phase 4 — Generate HTML Note

Follow the exact HTML template from existing notes. Structure:

| Section | Content |
|---------|---------|
| **Header** | Tags: `论文笔记` + slug. Title. Auto-notice disclaimer. |
| **论文出处 (Source)** | Table: arXiv link, local PDF path, authors, venue/version, page count. |
| **论文概括 (Summary)** | Bullet points summarizing the paper's contribution, key ideas, and main results. Must include concrete numbers/benchmarks from the paper. |
| **从论文 PDF 提取的图表页 (Figures)** | List of method pages and experiment pages extracted from the PDF. |
| **核心技术原理讲解 (Core Technology)** | Explanation of the core technique: how it works, key innovations, formulas/algorithms, architecture diagrams. Write in well-structured Chinese paragraphs (not just bullet points). Include rendered method page images. |
| **实验分析 (Experiment Analysis)** | Analysis of experimental setup, benchmarks, baselines, main results, ablation studies. Include concrete numbers. Include rendered experiment page images. |
| **局限性和展望 (Limitations & Future Work)** | What the paper acknowledges as limitations, failure cases, and directions for future work. |

**Critical rules:**
- **所有笔记内容必须使用中文讲解**：除论文标题、作者姓名、机构名、模型名、数据集名、方法名、会议名、URL、公式和代码标识符外，HTML 正文不得出现大段英文原文。
- 不要把 `paper.txt` 中的英文句子直接作为 `<li>`、段落或摘要输出；必须先理解后用中文重新组织。
- 所有 `<pre class='evidence'>` 或证据摘录块也必须改写为中文说明，格式建议为：`[页 X] 中文转述：……；可核对信息：Figure/Table/公式编号……`。只有极短的专有名词、指标名或原文表头可以保留英文。
- 如果需要保留原文证据，最多只保留一两个关键短语，并必须配中文解释；不要粘贴整段英文 PDF 原文。
- 图表说明、caption、表格解释、实验结论、局限性都必须是中文讲解。
- Charts, tables, and numerical data must come ONLY from the PDF. If missing, explicitly write "论文中未明确标注" / "论文中未找到该数据".
- Slug naming: same as PDF stem (e.g., `07_deepseek_v2_mla_2405.04434`).
- Page images go in `assets/` subdirectory.
- Write the HTML to `<output_dir>/<slug>/index.html`.

### Chinese-only Note Writing Requirements

生成 HTML 前，必须先把论文信息整理成中文结构化草稿，再写入 HTML：

1. **论文概括**：用中文解释研究问题、核心贡献、方法思路和主要实验结论；不要直接翻译 abstract，而是面向中文读者重写。
2. **核心技术原理讲解**：按照“背景问题 → 方法机制 → 关键公式/结构 → 为什么有效 → 和已有方法的区别”组织；允许保留方法名如 PagedAttention、GQA、MLA，但解释必须是中文。
3. **实验分析**：用中文说明实验设置、baseline、数据集、指标、主结果和消融实验；所有数字必须可在 PDF 文本或图表页中核对。
4. **局限性和展望**：中文总结论文明确承认的限制、从实验可推断但需谨慎表述的适用边界，以及合理后续方向；推断内容必须标注为“基于论文结果的分析”。
5. **证据摘录**：不要输出英文原文段落。用中文写“依据页码 + 中文转述 + 关键数值/图表编号”，例如：
   ```html
   <pre class='evidence'>[页 12] 中文转述：论文在 Figure 18 中比较了不同 block size 下的端到端延迟，结果显示 block size 过小会增加 kernel 开销，过大则会降低内存利用率。关键可核对项：Figure 18(a)(b)。</pre>
   ```

### Phase 5 — Update Index (if applicable)

If a `paper_notes/index.html` already exists, read it and regenerate it to include the new paper. The index page table has columns: **论文 Title** (linked), **作者**, **会议/版本**, **arXiv**.

```python
# Read existing index, add new row, write back
# The index HTML is a single-line/compact format with inline CSS
```

For topic supplements to an existing literature review, also update the relevant outline/reading-list files with the new slugs and explain how each paper supports the revised section. Keep the distinction between papers, system/blog documentation, and implementation repositories explicit; do not present implementation docs as formal papers.

### Phase 6 — Report

Report to the user:
- Where the note was saved (absolute path)
- A MEDIA: link to the generated HTML for preview
- Key metadata: title, authors, venue, page count
- Any issues encountered (missing data, rendering failures, etc.)

## Deep Enhancement Pass for Existing Notes

When the user says the current notes are not detailed enough, treat it as a **depth enhancement** pass, not another simple Chinese conversion. Focus on `核心技术原理讲解` and `实验分析` while preserving the existing HTML shell and assets. Use `references/deep-enhancement-checklist.md` as the checklist for what "detailed enough" means: design motivation, formulas/cache/complexity expressions, traditional-method contrast, concrete baseline numbers, relative improvements, and ablations.

## Technical Research Report Generation

When the user asks for a **technical research report** (技术调研报告) on a model, framework, or technology — especially when there is no standalone technical paper — use the workflow in `references/tech-model-research-template.md`. This covers models that only have official blog posts, Hugging Face model cards, and third-party analyses (e.g., Kimi K2.6, K2.7 Code).

Key differences from paper notes:
- **Scope**: Broader than a single paper — covers architecture, training, benchmarks, deployment, and competitive analysis across multiple sources
- **Format**: Self-contained HTML report with charts, tables, and professional styling; optionally converted to PDF
- **Depth**: When the user says "文字太少，感觉深度不够" (content is too shallow), expand all sections with detailed analysis, concrete numbers, and critical evaluation rather than surface-level summaries
- **Charts**: Generate matplotlib charts for benchmark comparisons, radar charts, architecture diagrams, and training pipelines. If the sandbox environment lacks matplotlib, generate placeholder descriptions and note the limitation
- **Sources**: Explicitly distinguish between official data (blog, model card), third-party analysis (Kili Technology, Artificial Analysis), and speculation. Mark unverified claims clearly

### From News Discovery to Deep Dive

When the user discovers an interesting paper from a **daily briefing, tech news aggregator, or casual mention** and asks for a deeper investigation, follow this enhanced workflow:

1. **Rapid paper identification**: Extract arXiv ID, title, or authors from the user's reference. If only a vague description is given, search `"<description>" site:arxiv.org` or use Hugging Face Papers API to identify the exact paper.

2. **Full-text extraction**: Use the Jina AI PDF extraction service for quick full-text access without downloading:
   ```bash
   curl -sL "https://r.jina.ai/http://arxiv.org/pdf/<arxiv_id>" > paper_full_text.txt
   ```
   This service returns the complete paper text in markdown format, including all sections, figures, tables, and formulas. It is the fastest way to get a paper's full content for analysis.

3. **Structured deep analysis**: Produce a multi-section analysis covering:
   - **Problem background**: Why this direction matters, industry context
   - **Core mechanism**: Mathematical principles, algorithmic innovations, with formulas
   - **Systemic implications**: How the finding propagates through the training/inference stack
   - **Experimental validation**: Key results across model scales, ablation studies
   - **Industry relevance**: Connections to hardware roadmaps (NVIDIA, AMD, custom ASICs), competing approaches
   - **Future directions**: Open questions, potential follow-up work

4. **Cross-paper contextualization**: When the paper is part of a larger trend (e.g., FP4 quantization), survey related works from the same period to provide competitive landscape analysis. Use the paper's Related Work section as a starting point, then verify with web search for the latest developments.

5. **Output format**: Use a structured markdown or HTML format with clear section headers, tables for comparisons, and inline formulas. The user expects depth — include mathematical derivations, quantitative comparisons, and critical evaluation rather than surface-level summaries.

See `references/news-to-deep-dive-example.md` for a concrete example of this workflow applied to the UFP4 paper (arXiv:2606.20381), including the full structured analysis template and key findings.

## Batch Converting Existing Notes to Chinese

When existing `paper_notes/*/index.html` pages were generated with English PDF snippets, convert the **content pages** in place instead of regenerating everything from scratch:

1. Inventory `paper_notes/*/index.html`, source PDFs under `paper/`, and `manifest.json` if present.
2. Preserve each page's HTML/CSS shell, source table, slug, image paths, and `assets/` references.
3. Rewrite only the note content sections into Chinese: `论文概括`, `核心技术原理讲解`, `实验分析`, `局限性和展望`, and every evidence block.
4. If metadata fields were polluted by extracted English paragraphs, replace them with accurate short metadata or `论文中未明确标注`; do not leave abstract/introduction prose in `作者` or `会议/版本` cells.
5. Do not modify source PDFs, `paper.txt`, or rendered image assets unless the user explicitly asks.
6. Validate the batch with the helper script:
   ```bash
   python3 SKILL_DIR/scripts/validate_chinese_notes.py /path/to/paper_notes
   ```
   The expected result is `problems: 0`; if not, fix the reported slugs and rerun.


- **禁止把英文 PDF 原文当作笔记正文**：摘要、原理、实验、局限、证据摘录都必须是中文讲解；英文仅可用于论文标题、作者、方法名、模型名、数据集名、指标名、公式符号、URL 和必要短语。
- Structure explanations from **basic concepts → technical details → significance**.
- For figures: include all rendered method/experiment page images in their respective sections.
- Verification: after generating, read back the HTML and check that there are no long English paragraphs copied from the PDF. If found, rewrite them into Chinese before reporting completion.
- Verification: check for coherence, correct links, proper image references, and traceability of every numerical result.

## Error Handling

| Problem | Action |
|---------|--------|
| `pdftotext` / `pdftoppm` not found | Install poppler (`brew install poppler` or `apt install poppler-utils`) |
| PDF download fails (arXiv) | Try `https://arxiv.org/pdf/<id>` with `-L` flag; fall back to abstract page |
| Corrupted PDF | Tell user and try to find paper through Semantic Scholar API |
| Paper title not found | Search `"<title>" site:arxiv.org` or ask user for arXiv ID/link |
| Image rendering fails | Skip images for that page, note it in the report |
| Text extraction incomplete | Use `-layout` flag; for scanned PDFs, try `marker-pdf` OCR (see ocr-and-documents skill) |

## File Structure

```
paper_notes/
├── index.html                     # Index page (if applicable)
├── manifest.json                  # Machine-readable metadata
└── <slug>/
    ├── index.html                 # Paper note
    ├── paper.txt                  # Extracted text
    └── assets/
        ├── method_p02.png
        ├── method_p04.png
        ├── experiment_p12.png
        └── experiment_p15.png
```