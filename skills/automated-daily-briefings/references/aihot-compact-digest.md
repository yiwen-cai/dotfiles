# AIHOT Daily Briefing Pattern

Use this for scheduled AIHOT/AI news cron briefings delivered through messaging platforms.

## Two Modes

This file documents two modes: **Compact Mode** (merge + truncate, for short messages) and **Full Mode** (no truncation, full summaries). Choose based on user preference — the cron script should match whichever mode the user prefers.

## Goal (Common)

- Fetch a larger candidate pool, e.g. last 24h with `take=50`.
- Emit at most 10 numbered digest items.
- Merge thematically similar items into one numbered item when possible.
- Keep the output plain Markdown for gateway delivery; no attachment is required unless the job already sends one.

## Implementation Pattern (Common)

For a deterministic `no_agent=True` cron script:

1. Add constants near the category/order config:
   - `MAX_DIGEST_ITEMS = 10`
   - `SIMILARITY_THRESHOLD = 0.28` as a practical starting point
   - `MERGE_SUMMARY_LIMIT` — varies by mode (see below)
   - a small English `STOPWORDS` set so generic words such as `ai`, `new`, `release`, `update` do not dominate matching.
2. Tokenize each item from `title`, `title_en`, `summary`, and `source` using a regex such as `[a-z0-9][a-z0-9-]{2,}`.
3. Score similarity with Jaccard overlap plus a small same-category bonus, e.g. `+0.08`.
4. Greedily cluster in API order: compare a new item against existing cluster members, then append to the best cluster if the score crosses the threshold.
5. Sort clusters by `(cluster_size, newest_published_at)` descending and keep the first 10.
6. Render each cluster as one numbered item:
   - Single-item cluster: original title and summary.
   - Multi-item cluster: title like `<first title> 等 N 条相关动态`, plus `已合并 N 条相近动态。`
   - Join up to three distinct source names.
   - Use the newest `publishedAt` for displayed time.
   - Use the first available URL as the primary link.
7. In the message header, state both the collected count and compressed count, e.g. `过去 24 小时采集 35 条 AI 动态，压缩为 10 条精选；其中 1 条已并入相近主题。`

---

## Mode A: Compact (Truncated + Merged)

Use when the user wants short digest items with `…` suffix for long content.

**Key constants:**

```python
### COLLECTION / RENDERING
MAX_DIGEST_ITEMS = 10
SIMILARITY_THRESHOLD = 0.28
MERGE_SUMMARY_LIMIT = 150
```

**`shorten()` function:**

```python
def shorten(text: str | None, limit: int = 90) -> str:
    value = " ".join((text or "").split())
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "…"
```

Individual item summaries in merging are capped at `70` chars; merged result is capped at `MERGE_SUMMARY_LIMIT`.

**Use when:**
- The user explicitly says the briefing is too long
- The platform has message length limits (e.g. Telegram, SMS)
- The user has not stated a preference

## Mode B: Full (No Truncation)

Use when the user wants full summaries without `…` truncation. Text stays concise because the API summaries themselves are already short — just not sliced mid-sentence.

**Key constants:**

```python
### COLLECTION / RENDERING
MAX_DIGEST_ITEMS = 10
SIMILARITY_THRESHOLD = 0.28
MERGE_SUMMARY_LIMIT = 99999  # effectively unlimited
```

**`shorten()` function (no truncation):**

```python
def shorten(text: str | None, limit: int = 99999) -> str:
    return " ".join((text or "").split())
```

**Use when:**
- The user says "不要省略" / "不要用省略号" / "完整内容" / "no truncation"
- The user corrected a prior truncated delivery

### Cron script conversion from Compact to Full

When converting a Compact-mode cron script to Full mode:

1. Change `shorten()` to strip whitespace only — remove the `…` suffix logic.
2. Increase `MERGE_SUMMARY_LIMIT` to `99999`.
3. Remove any separate small-limit calls like `shorten(item.get("summary"), 70)` — just pass full text.
4. Verify by running the script and checking no `…` appears in the output.

---

## Verification

After editing a Python cron script:

```bash
python3 /absolute/path/to/script.py | tee /tmp/aihot_briefing_preview.txt
```

In Full mode, additionally verify no `…` characters appear in the output:

```bash
grep -c '…' /tmp/aihot_briefing_preview.txt || echo "No truncation found (good)"
```

In Compact mode, verify numbered item count:

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('/tmp/aihot_briefing_preview.txt').read_text(encoding='utf-8')
count = sum(1 for line in text.splitlines() if line.split('. ', 1)[0].isdigit() and '. **' in line)
print(f'NUMBERED_ITEMS={count}')
raise SystemExit(0 if count <= 10 else 1)
PY
```

If the user specifically asked for merging, also inspect for `已合并` in the preview when the current candidate pool naturally contains related items. Do not fail the job solely because a particular day has no mergeable topics.

## Pitfalls

- Do not count raw collected items as final digest items; count numbered lines after rendering.
- Do not rely only on exact title deduplication. AIHOT often contains multiple posts about the same product/model/event from different X accounts or blogs.
- Do not make the threshold too low; unrelated AI product posts will collapse together. Start around `0.28` and adjust after previewing the real day's data.
- **Do not assume Compact mode is the user's preference.** Ask or infer from past corrections. If the user previously complained about truncated summaries, switch to Full mode.
- When user says "简练文字全部概述", they want concise but complete summaries — not truncated. Full mode achieves this: the API summaries are already concise; removing the `…` just prevents mid-sentence cuts.
- After modifying the cron script, verify by running it manually. A "preview looks good" check beats a "wait until tomorrow's cron" loop.
