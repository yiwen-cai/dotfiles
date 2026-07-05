# Cron File Delivery via Weixin — Session Notes

Session: 2026-05-11, AI daily briefing automation for Weixin.

## Problem

User wanted a cron job that sends an HTML file attachment to Weixin every morning. Initial attempts using `no_agent=False` (agent-mode cron) failed to deliver the file because:
1. The LLM did not consistently include `MEDIA:/absolute/path` in its response.
2. Even when instructed, the model sometimes forgot or used placeholder paths.
3. Weixin gateway (`ilinkai.weixin.qq.com`) rate-limited repeated manual triggers.

## Solution

Switched to `no_agent=True` with a dedicated Python script (`scripts/daily_briefing.py`) that:
1. Runs data collection (`collect_ai_news.py`).
2. Runs HTML rendering (`render_html.py`).
3. Prints a brief summary + `MEDIA:/absolute/path/to/file`.

The script is deterministic and does not depend on LLM behavior for file attachment.

## Key Logs

```
# Rate limiting (multiple triggers in short time)
[Weixin] send failed: iLink sendmessage rate limited: ret=-2

# Connection failure (network issue)
[Weixin] send chunk failed: Cannot connect to host ilinkai.weixin.qq.com:443

# Successful delivery
Job '7b2258d24058': delivered to weixin:... via live adapter
```

## Verification

Check delivery status:
```bash
hermes cron list
# Look at last_status AND last_delivery_error
```

## Pitfalls

- `last_status=ok` does NOT mean the user received the message. Always check `last_delivery_error`.
- Weixin has aggressive rate limiting. Space out manual triggers by several minutes.
- `MEDIA:` path must be absolute. Relative paths fail silently.
- HTML files are sent as documents through Weixin. The recipient taps to open.
