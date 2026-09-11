---
name: paper-note-generator
description: "根据论文链接、标题或本地 PDF 生成既定格式的中文论文笔记；用于明确的论文笔记或补充深度请求。"
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# paper-note-generator

## 工作约定
输出沿用项目的 `paper_notes/<slug>/index.html`；已有笔记先读原文件，保留 HTML 外壳、图片和来源材料。正文中文，方法名/公式保留准确原文；区分论文报告、个人推断和自己的复现。
先定位原论文并核对作者、年份、方法和实验；外部补充仅在任务需要时获取，不能用二手介绍替代论文。缺失证据标明，不补造实验数字。

## 格式与资源
- 生成前读 [note-format.md](references/note-format.md)，按既定字段准备内容。
- `scripts/generate_paper_note.py`：先用 `--help` 确认输入，再生成；`scripts/validate_chinese_notes.py` 校验中文笔记。
- 深度增强时读 [deep-enhancement-checklist.md](references/deep-enhancement-checklist.md)。技术模型调研、新闻转深读分别见对应 `tech-model-research-template.md`、`news-to-deep-dive-example.md`；仅按任务读取。
生成后检查公式、关键表格、数字与来源对应，渲染查看 HTML；只有存在索引且任务需要时更新索引。
