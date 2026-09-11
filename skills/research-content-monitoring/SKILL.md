---
name: research-content-monitoring
description: "收集论文、科研动态和 AI 简报，沿用用户既有源表与简报管线；定时仅在明确请求时设置。"
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# research-content-monitoring

## 收集流程
按主题与日期筛选原始论文、官方发布和可靠索引，跨来源去重。区分发表/更新日期与事件日期；摘要附原始链接，第三方聚合不能替代关键事实核验。
生成单次简报不建立后台任务。用户要求定时或监控时调用当前宿主调度工具，状态不变时保持安静，只通知有意义的变化。

## 已有管线与条件资料
- 本机 `~/Documents/code/ai-daily-briefing`，先检查实际脚本与最近结果；接入说明见 [aihot-daily-briefing.md](references/aihot-daily-briefing.md)。该文的旧 cron/投递状态属于历史，现场核实。
- 选择源时读 `references/ai-briefing-sources.md` 或 `references/third-party-ai-aggregators.md`。
- 仅出现投递/调度故障时读 `references/cron-delivery-troubleshooting.md`。
用户要求深入某篇论文时按论文笔记格式继续，不在摘要里编造细节。验证链接、日期、重复项及自己的推断标记。
