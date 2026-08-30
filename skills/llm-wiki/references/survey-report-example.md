# Survey Report Example: LLM Wiki 调研报告

> This is a reference file showing the output structure of a successful survey report generated via the llm-wiki skill. Use it as a template for future survey work.

## Report Structure

A good survey report in `queries/` should contain:

1. **调研背景** — Why this topic matters, what problem it solves
2. **方法论核心** — Key concepts, frameworks, or methodologies found
3. **对比分析** — Tables comparing alternatives (tools, approaches, paradigms)
4. **工具生态** — Available tools, their trade-offs, recommended combinations
5. **实施建议** — Step-by-step guidance for adoption
6. **总结** — Key takeaways, who this is for, expected benefits

## File Organization Pattern

```
queries/
└── <topic>-survey-report.md      # The main deliverable
```

Supporting pages created alongside the report:
```
entities/     # People, organizations, tools mentioned
concepts/     # Core methodologies or ideas
comparisons/  # Side-by-side analyses
```

## Frontmatter Template for Survey Reports

```yaml
---
title: <Topic> 调研报告
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: query
tags: [review, <domain>, survey]
sources: [raw/articles/source-1.md, raw/articles/source-2.md]
confidence: high
---
```

## Cross-Linking Requirement

The report must cite wiki pages it draws from:
- "Based on [[page-a]] and [[page-b]]..."
- This connects the report back into the knowledge graph

## User Language Preference (Important)

If the user has specified a preferred language (e.g., "无论用什么语言提问都必须用中文回复"), ALL wiki pages and the survey report MUST be written in that language. This includes:
- Page titles and content
- SCHEMA.md conventions
- index.md and log.md entries
- Tags (if possible within the taxonomy)
