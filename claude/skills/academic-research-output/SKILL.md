---
name: academic-research-output
description: Produce academic research outputs — presentations and papers with proper structure, visual design, and LaTeX
  formatting.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Academic Research Output

Produce academic research outputs including presentations and papers. Covers slide decks, research papers, and publication-ready documents.

## When to Use

- User wants to create a research presentation
- User wants to write a research paper
- Need to format academic content properly
- Preparing for conferences (NeurIPS, ICML, ICLR, etc.)

## Three Output Formats

| Format | Purpose | Tooling |
|--------|---------|---------|
| **Presentations** | Share research findings | Slides, visual design |
| **Papers** | Publish research | LaTeX, citations, figures |
| **HTML Reports** | Quick-read paper summaries | Single-file HTML with cards, tables, formulas |

### HTML Reports from Wiki Entities

When the user asks for an HTML report of a paper and a wiki entity exists (e.g. `wiki/entities/<paper-name>.md`), use that entity as the primary source rather than re-extracting from the PDF. The entity already contains structured fields: one-line summary, motivation, method, results, key insights, open questions, and related work.

**Workflow:**
1. Read the entity file (e.g. `wiki/entities/triaxialkv.md`)
2. Map entity sections to the HTML template structure below
3. Generate a single self-contained HTML file with all CSS inline
4. Save to `wiki/study_archive/` or user-specified path

**HTML Template Structure:**
- Header with gradient background: paper title, arXiv ID, date, tags
- Abstract card: one-line summary + tag cloud
- Motivation card: challenge → manifestation table
- Method card: formulas in centered italic blocks, step-by-step flow
- System/Implementation card: component → detail table
- Results card: big-number grid (compression ratio, throughput, accuracy) + comparison table
- Key Insights card: numbered list with bold lead-ins
- Open Questions card: checkbox list (disabled, unchecked)
- Related Work card: direction → representative work → relationship table
- Footer: paper citation + generation source

**Design specs:**
- Max-width 900px, centered, responsive
- CSS variables for colors: `--primary: #2563eb`, `--bg: #f8fafc`, `--card-bg: #ffffff`
- Cards with `box-shadow: 0 1px 3px rgba(0,0,0,0.08)` and `border: 1px solid #e2e8f0`
- Formula blocks: `background: #f1f5f9`, `font-family: 'Times New Roman', serif`, centered
- Result cards: green gradient background (`#f0fdf4` to `#dcfce7`), large bold numbers
- Highlight row in comparison tables: `background: #eff6ff` for the paper being reported

See `templates/paper-html-report.html` for a starter template. Copy it, replace `{{VARIABLE}}` placeholders with entity data, and write the result via `write_file`.

## Research Presentations

### Defense-Readiness Supplement Pass

## Research Presentations

### Topic-Specific Revision Workflow

When the user asks to supplement or revise a specific technical section of an existing presentation, update that section directly rather than adding only general background or Q&A material.

1. Locate the relevant section in the outline and slide-spec files.
2. Add the new topic into the main narrative, slide sequence, and reading list where it belongs.
3. If the topic straddles categories, state the boundary clearly. Example: sparse attention may reduce compute/bandwidth without reducing stored KV cache; only native/compressed sparse attention that changes training/architecture should be framed as architecture-level cache reduction.
4. Add supporting papers/notes only after the section itself has been updated.
5. Verify the updated files contain the new topic terms in the target section, not just in backup/Q&A pages.

#### KV Cache Sparse / Linear Attention Supplement

For long-context LLM presentations, sparse attention should be split by mechanism instead of treated as a single method family. Use `references/kv-cache-sparse-linear-attention.md` when the user asks about sparse attention, GDN/Gated DeltaNet, linear attention, linear complexity, or whether sparse attention actually reduces KV Cache pressure. Key distinction: top-k/page sparse methods reduce access/compute, GDN-style methods replace explicit per-token KV with fixed recurrent state, and systems such as Spin/LServe are needed to translate sparse access into GPU HBM relief.

### Generating a PPT Agent Brief (Self-Contained)

When the user asks for a file to pass to another agent (or the user will pass to an agent themselves) to generate a complete PPT, produce ONE self-contained markdown file that the downstream agent can use without reading anything else.

**⛔ CRITICAL: The brief file MUST NOT reference any external files.** No "see also part1_ppt.md", no "details in kv_cache_outline.md", no "read the following files first". The file must contain everything the downstream agent needs: slide-by-slide content, speaker notes, design specs, color schemes, paper references, backup slides, defense talking points, and output path — all inline.

The file alone must be sufficient for the downstream agent to produce the full `.pptx`.

Structure of a self-contained brief:
1. **Task goal** — topic, audience, duration, page count, output format
2. **Global design specs** — colors, fonts, diagram requirements, formula rendering
3. **Complete slide index** — a numbered table of all slides with Part attribution
4. **Slide-by-slide content** — every slide with: title, layout description, body text/bullets, diagram specification, takeaway, speaker notes, and references
5. **Backup slides** — same format as main slides
6. **Full paper reference list** — all citations the agent may need to put in footers
7. **Defense talking points** — center sentences for Q&A
8. **Output requirements** — exact file path and self-check checklist

This is NOT about describing slides at a high level. Each slide must have enough detail that the downstream agent knows exactly what text, diagram, and layout to produce.

### Pitfall: Referencing External Files in Agent Briefs

**❌ DO NOT** write agent briefs like:
- "请读取以下文件: part1_ppt.md, part2_ppt.md..."
- "详见 kv_cache_complete_ppt_description.md"
- "See part4_ppt.md for detailed slide specs"

The downstream agent may not have access to those files, or the user may not want to pass multiple files. Consolidate everything.

When the user says "一个文件就完成所有描述", they mean it — one file, fully self-contained, zero external references.

### Syncing Presentation Artifacts After PPT Edits

When the user says they edited an existing PPT and asks to update downstream artifacts, read the actual `.pptx` first and regenerate from the deck as it exists now. Do not rely on the earlier agent brief, older markdown script, or stale slide count. Save a slide-text extraction artifact, create timestamped backups of overwritten markdown files, write current artifacts aligned to the actual slide count, and verify continuous slide numbering.

Apply this to both:
- **Speaker scripts** — produce a slide-by-slide script keyed to actual `Slide N` order. See `references/ppt-script-sync.md` for the reusable workflow and `python-pptx` extraction pattern.
- **Self-contained PPT agent briefs** — if an older brief no longer matches the edited deck, rebuild the complete slide index and slide-by-slide content from the extraction plus the current script. Remove stale sections such as old `Slide 36-38` entries or outdated page-count headings, and explicitly note visible deck inconsistencies such as a footer still showing `/38` when the actual deck has 35 slides.

Verification checklist: actual `.pptx` slide count matches regenerated artifacts; slide numbers are continuous; structure tables have the same count; old page-count strings and removed slide headers are absent; important technical boundary notes from the current deck remain present.

### Structure
1. **Title slide** — Title, authors, affiliation
2. **Motivation** — Why this problem matters
3. **Related work** — Key prior work and gaps
4. **Method** — Your approach, with diagrams
5. **Experiments** — Setup, results, ablations
6. **Results** — Key findings with visualizations
7. **Conclusion** — Summary and future work

### Design Principles
- **One idea per slide** — don't crowd
- **Visual hierarchy** — titles, bullets, figures
- **Consistent styling** — fonts, colors, layout
- **Readable fonts** — 24pt minimum for body text
- **High-contrast** — ensure readability in large rooms

### Tools
- Beamer (LaTeX)
- PowerPoint / Keynote
- Google Slides
- reveal.js (web-based)

## Research Papers

### Structure
1. **Abstract** — 150-250 words summarizing contribution
2. **Introduction** — Problem, motivation, contributions
3. **Related Work** — Prior art and differences
4. **Method** — Technical approach
5. **Experiments** — Setup, datasets, metrics
6. **Results** — Main findings, ablations, analysis
7. **Discussion** — Interpretation, limitations
8. **Conclusion** — Summary and future work

### LaTeX Template
```latex
\documentclass{article}
\usepackage{neurips_2024}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}

\title{Your Paper Title}
\author{Author Name\\ Institution}

\begin{document}
\maketitle

\begin{abstract}
Your abstract here.
\end{abstract}

\section{Introduction}
\section{Related Work}
\section{Method}
\section{Experiments}
\section{Results}
\section{Conclusion}

\bibliographystyle{plain}
\bibliography{references}
\end{document}
```

### Citation Management
- Use BibTeX / BibLaTeX
- Maintain a single `.bib` file
- Use consistent citation keys
- Check for missing fields

### Figure Guidelines
- Vector graphics (PDF, SVG) preferred
- 300 DPI minimum for raster images
- Consistent font size across figures
- Clear labels and legends
- Colorblind-friendly palettes

## Conference-Specific Notes

| Conference | Format | Page Limit | Key Dates |
|------------|--------|------------|-----------|
| NeurIPS | LaTeX | 9 pages | May/September |
| ICML | LaTeX | 8 pages | January |
| ICLR | LaTeX | 8 pages | October |
| ACL | LaTeX | 8 pages | July |

## Common Pitfalls

1. **Weak motivation** — clearly state why the problem matters
2. **Insufficient baselines** — compare against strong baselines
3. **Missing ablations** — show what matters in your method
4. **Overclaiming** — be honest about limitations
5. **Poor writing** — get feedback, use Grammarly
6. **Late submission** — start early, buffer time

## Related Skills

- `arxiv` — For finding related work
- `research-content-monitoring` — For staying current
- `llm-fine-tuning` — For experimental methods
- `cs336-stanford-course` — For fundamentals