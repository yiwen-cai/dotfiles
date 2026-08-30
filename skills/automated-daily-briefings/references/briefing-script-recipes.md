# Briefing Script Maintenance Recipes

Concrete modifications for the two daily briefing scripts used in this project.

## aihot_morning_briefing.py

Located at `~/.hermes/scripts/aihot_morning_briefing.py`.

### Remove summary truncation

- `shorten()` function: change default limit from 90 to 99999, remove the `…` suffix logic
- `MERGE_SUMMARY_LIMIT` constant: change from 150 to 99999
- Line calling `shorten(item.get("summary"), 70)`: `70` limit becomes irrelevant after the function changes

### Verification
```bash
python3 ~/.hermes/scripts/aihot_morning_briefing.py | grep -c '…'
# Expect 0 — no truncated ellipsis anywhere in output
```

## hermes_agent_news.py

Located at `~/Documents/code/ai-daily-briefing/scripts/hermes_agent_news.py`.

### Remove HTML attachment generation

Three changes in `main()`:
1. Delete `html_path = OUTPUT_DIR / f"hermes-agent-news-{date_name}.html"`
2. Delete `render_html(data, html_path)` call
3. Delete `print(f"MEDIA:{html_path.resolve()}")` line (and the blank `print("")` before it)

Replace `html_path` argument in `send_email()` call with `OUTPUT_DIR`.

Delete the entire `render_html()` function (~80 lines, from `def render_html` to its last line).

### Show all items (not just top 6)

In `build_text_summary()`, change:
- Remove `lines.append("重点条目：")` header
- Change `for index, item in enumerate(items[:6], start=1):` to `for index, item in enumerate(items, start=1):`
- Add summary display: after `title` and `source`, add:
  ```python
  summary = item.get("summary") or ""
  lines.append(f"   {summary}")
  ```

### Remove HTML references in text output

1. Delete `lines.append(f"注：{len(errors)} 个采集请求出现异常，详情见 HTML 附件。")` — replace with inline error listing
2. Delete `lines.append("详细内容请查看 HTML 附件。")`

### Remove `clean_text` truncation

- `clean_text(value, limit=700)`: change default to `99999`
- `clean_text(title, 300)`: change to `clean_text(title)`
- `clean_text(summary, 1000)`: change to `clean_text(summary)`

### Verify

```bash
cd ~/Documents/code/ai-daily-briefing
python3 scripts/hermes_agent_news.py | head -20
# Confirm no MEDIA: line, no HTML reference, all items listed with summaries
```
