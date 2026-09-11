---
name: academic-research-output
description: "按用户既有科研规范撰写综述、汇报、答辩材料和论文输出；保留定量证据与个人模板。"
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# academic-research-output

## 输出约定
先确认输出是汇报、论文还是 HTML 报告，直接使用当前宿主可用的演示/文档/PDF/可视化工具。不要复制旧宿主 API。
使用已有 wiki 实体时核对来源与时效，不重复提取已经可靠整理的材料。明确实验口径、baseline、指标单位、限制和未复现之处。
如果用户要交给另一个 agent 的单文件 PPT brief，必须自包含：关键内容、设计和讲稿直接写入同一文件，不能依赖对方读不到的路径。
PPT 改动后同步讲稿时，以实际新 PPT 的页数与内容为准，不能使用旧大纲。

## 条件参考
- 汇报与讲稿同步：[ppt-script-sync.md](references/ppt-script-sync.md)。
- 答辩补充：[research-presentation-defense-prep.md](references/research-presentation-defense-prep.md)。
- 文献综述：[academic-literature-review-slide-prompts.md](references/academic-literature-review-slide-prompts.md)。
- KV Cache 量化、稀疏/线性注意力分别读 `references/kv-cache-quantization-asymmetric.md`、`references/kv-cache-sparse-linear-attention.md`。
- HTML 模板在 templates/；按输出选用，不强制普通回答变成网页。

## 验证
数字与引用逐项对应来源；排版输出需实际渲染检查。已有产物修改后核对页码、讲稿及图表一致。
