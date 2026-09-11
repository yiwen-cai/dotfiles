---
name: youtube-content
description: "提取 YouTube 视频字幕及时间戳，整理课程摘要或指定格式的笔记。"
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# youtube-content

## 字幕提取
脚本为 `scripts/fetch_transcript.py`。先用 `--help` 确认参数；使用有 youtube-transcript-api 的环境，或 `uv run --with youtube-transcript-api python <script> <URL>`，避免修改无关项目环境。
支持 URL 或 video ID，`--text-only`、`--timestamps`、`--language zh,en` 按任务选择。核实内容非空与实际语言。
字幕关闭、视频私有或限流时报告具体失败；不要声称已经看过视频画面。缺少指定语言可以尝试现有字幕并说明语言。

## 整理
按主题和时间戳组织课程内容，区分视频原文与解释补充。可选格式见 [output-formats.md](references/output-formats.md)。只整理内容，不自动向社交平台发送。
核对时间戳与原文对应，长字幕分段后检查跨段遗漏和重复。
