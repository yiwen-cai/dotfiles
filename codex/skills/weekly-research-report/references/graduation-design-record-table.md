# Graduation Design Record-Table Session Notes

This reference records the workflow for filling blank weeks in the graduation design advisor record table.

## Trigger

User asks to fill in / complete / write remaining weeks of:
- `北京邮电大学教师指导本科毕业设计_论文_记录表.docx`
- Any variant of "毕业设计记录表", "指导记录表", "空白周数"

## Workflow

1. **Locate the record table**
   ```text
   /Users/yiwencai/Documents/study/毕业设计/北京邮电大学教师指导本科毕业设计_论文_记录表.docx
   ```
   Use `textutil -convert txt FILE.docx -stdout` to extract text content.

2. **Identify blank periods**
   - Read existing filled weeks to understand the timeline and writing style.
   - Note the date pattern (每2周一个记录, typically spanning the full semester).
   - Identify which week ranges are empty.

3. **Gather research content for blank periods**
   - Read the thesis PDF to extract experiments, milestones, and results for the corresponding time periods.
   - Use `pdftotext THESIS.pdf -` for full text extraction.
   - Check local project files for additional context:
     - `/Users/yiwencai/Documents/study/毕业设计/中期检查/` — mid-term defense materials
     - `/Users/yiwencai/Documents/study/毕业设计/开题报告/` — proposal materials
     - Any code notes, experiment logs, or technical reports in the project directory.

4. **Cross-reference timeline**
   - Map thesis chapters/experiments to the record-table week ranges.
   - Ensure chronological consistency with already-filled entries.
   - The writing style should match: academic advisor tone, specific technical details, concrete guidance.

5. **Generate content only — do NOT modify .docx**
   - Output plain text formatted for direct copy-paste.
   - Each entry should be a self-contained paragraph covering the 2-week period.
   - Include the date line at the end of each entry.

## Content style rules

- **Perspective**: Written as if the advisor is recording guidance given (指导教师视角).
- **Tone**: Formal academic Chinese, precise technical language.
- **Structure per entry**:
  - Open with the week's focus topic.
  - Describe specific technical discussions (algorithms, design decisions, experiments).
  - Include quantitative results when available (speedup, accuracy, metrics).
  - Mention next steps or decisions made.
  - End with the date line (指导教师签字 + 日期).
- **Later weeks (论文撰写阶段)**: Focus on draft writing, revisions, format checks, defense preparation.
- **Do NOT invent metrics**: Use values from the thesis; if uncertain, describe qualitatively or use approximate language.

## Example entry structure

```
第15-16周记录：
本周重点指导[具体技术方向]。学生汇报了[具体进展]。指导教师指出[具体问题/建议]。双方讨论了[具体技术决策]。此外，指导教师要求[下一步工作]。

指导教师签字

日期    2026年3月30日
```

## Key files for this workflow

| File | Purpose |
|------|---------|
| `北京邮电大学教师指导本科毕业设计_论文_记录表.docx` | The record table itself |
| `一种基于 GPU 上张量核心的图神经网络训练系统的设计与实现.pdf` | Thesis for content extraction |
| `毕业设计论文.docx` | Alternative thesis source |
| `中期检查/` | Mid-term materials for timeline context |
| `开题报告/` | Proposal for early-week context |

## Pitfalls

- **Do NOT modify the .docx directly**: The user explicitly requested text-only output for manual copy-paste.
- **Match the existing style**: Read at least 2-3 filled weeks to internalize the tone and level of detail.
- **Chronological consistency**: Ensure the generated content logically follows from the last filled week and leads into the next.
- **Avoid vague statements**: "做了一些实验" → replace with "完成了Voltrix后端在Reddit-rabbit-fg数据集上的对比实验，稳态加速比达3.307x".
- **Date accuracy**: Ensure dates align with the 2-week interval pattern established in existing entries.
