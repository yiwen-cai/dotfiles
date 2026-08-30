# Supplementary Research Example: DFlash Paper

This is a concrete example of how Phase 1.5 (Supplementary Web Research) was applied to the DFlash paper (arXiv:2602.06036). Use this as a reference pattern for future paper research tasks.

## Task Given

"Research this paper and generate a research report and paper notes."

## Search Queries Used

```python
# 1. Get the paper content
web_extract(["https://arxiv.org/abs/2602.06036"])
# → Got title, authors, venue (ICML 2026), GitHub link, HF link

# 2. Get detailed content - try HTML abstract page
web_extract(["https://arxiv.org/html/2602.06036v2"])
# → Got full structured summary with key quotes, benchmark numbers, methodology

# 3. Search for supplementary materials
web_search("DFlash block diffusion speculative decoding ICML 2026 benchmark results EAGLE")
# → Found ICML poster page, YouTube video, lmsys blog, Z Lab project page

# 4. Extract supplementary sources
web_extract(["https://z-lab.ai/projects/dflash"])
# → Got deployment code (SGLang + Transformers), ablation study data, Hugging Face model links

web_extract(["https://www.lmsys.org/blog/2026-06-15-next-generation-speculative-decoding-dflash-v2/"])
# → Got production serving benchmarks, Spec V2 integration details, Qwen3.5-397B results
```

## What Each Source Contributed

| Source | Contribution |
|--------|-------------|
| arXiv abstract page | Title, authors, venue, links to code/models |
| arXiv HTML page | Full paper summary, key quotes, motivation, methodology |
| Z Lab project page | Deployment code (SGLang + Transformers), ablation table, model list on HF |
| lmsys blog | Production benchmarks on Qwen3.5-397B, Spec V2 overlap scheduling (+33% improvement), independent third-party validation by Modal |
| YouTube (optional) | Additional explanation, kept as reference only |

## Key Findings That Only Came From Supplementary Sources

1. **SGLang deployment command** — not in paper, only in Z Lab project page and lmsys blog
2. **Qwen3.5-397B-A17B support** — paper focuses on Qwen3-4B/8B; the 397B model support was announced later via lmsys
3. **Spec V2 overlap scheduling** — a separate performance optimization (+33%) from SGLang engine, not part of DFlash itself
4. **Block size recommendation** — paper says 16, but production deployment for 397B model uses block size 8
5. **Token throughput numbers** (11.4k → 15.3k tok/s) — only in lmsys blog

## Output Structure

For this task, the output was two files:
- **Research report** (Markdown): comprehensive analysis for technical readers
- **Paper notes** (HTML): structured notes per user preference (按大纲分段, 技术按原理→优势→局限)

## Reflection

The paper-only version of the report would have been significantly weaker:
- No deployment code → reader can't try it
- No production validation → claims feel unsubstantiated
- No 397B model results → misses the most impressive benchmark
- No Spec V2 context → misses the broader serving ecosystem picture

The 3-5 minutes spent on supplementary search was the highest-ROI step of the entire task.
