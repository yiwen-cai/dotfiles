---
name: weekly-research-report
description: "将用户提供或要求核查的科研进展整理成导师周报，保存为既定路径下的 Markdown。"
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# weekly-research-report

## 固定格式
保存至 `~/Documents/study/weekpaper`，先查看已有文件沿用命名。正文使用 `# <主题>周报`，以及 `## 本周进展`、`## 遇到问题`、`## 下周计划` 三节。真实附件存在时才增加附件节。
依据用户给出的工作、已有记录或明确要求检查的远程结果起草；关键信息缺失时针对性询问，快速草稿可标待补充。已有充分授权和资料时直接写文件，无需重复批准固定格式。

## 内容口径
吞吐、显存、loss、延迟、实验规模写实际值与条件，区分计划和完成。导师可见正文用“实验室 H100 服务器”，不暴露内部 host 别名。
具体来源、论文远程路径和历史参考见 [report-context.md](references/report-context.md)。毕业设计指导记录表见 [graduation-design-record-table.md](references/graduation-design-record-table.md)，默认生成可粘贴文本，不直接编辑表格文件。

## 邮件与验收
写周报本身不授权发送邮件。用户要求发送时优先续接上一周邮件链，再核对正文和附件。
检查周期、三节内容、指标证据与附件路径，交付可点击文件。
