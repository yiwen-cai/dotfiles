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

