---
name: bilingual-resume-typst
description: "在个人 Typst 简历项目中审阅、同步中英文简历及个人陈述。"
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# bilingual-resume-typst

## 文件与事实源
本项目 `chinese.typ` 是中文事实源，`main.typ` 是英文；个人陈述为 `personal_statement.typ` 与 `personal_statement_cn.typ`。GPA、日期、奖项与经历先核对中文，再同步英文。
审阅时只列问题，除非明确要求修改建议；迭代只报告剩余问题。检查 `references/common-issues.md`。
使用本项目 basic-resume 模板与实际字体；不要在 macOS 假定 SimSun 可用。生成 PDF 用 `typst compile <source> <output>`。
验证双语事实一致、联系方式统一、排版与页数符合原项目；不修改博客中的另一份简历。
