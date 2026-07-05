# AIHOT 每日早报采集与生成流程

## 项目路径

```
/Users/yiwencai/Documents/code/ai-daily-briefing
```

## 核心脚本

| 脚本 | 作用 |
|:--|:--|
| `scripts/daily_briefing.py` | 主采集脚本，生成早报文本 |
| `scripts/collect_ai_news.py` | 多源 AI 新闻采集 |
| `scripts/hermes_agent_news.py` | Hermes Agent 相关新闻 |
| `scripts/render_html.py` | 渲染 HTML 输出 |

## 输出目录

```
output/
├── hermes-agent-news-YYYY-MM-DD.html   # Hermes 动态
└── ...
```

## 手动运行方式

```bash
cd /Users/yiwencai/Documents/code/ai-daily-briefing
python3 scripts/daily_briefing.py
```

## Cron 配置

```
Name:      AIHOT 每日早报（含 Hermes 动态）
Schedule:  30 9 * * *          # 每天 09:30
Script:    aihot_morning_briefing.py
Workdir:   /Users/yiwencai/Documents/code/ai-daily-briefing
Deliver:   微信
```

## 已知问题

- **微信发送失败**：rate limit 限制（30s cooldown），早报内容已生成但可能未送达
- **GitHub API 偶发 SSL 错误**：`curl: (35) SSL_ERROR_SYSCALL`，通常重试可恢复
