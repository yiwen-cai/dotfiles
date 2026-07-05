# Merging Hermes Agent Release Notes into AIHOT Briefing

Implementation reference for pulling Hermes Agent release data from GitHub API
and presenting it as a ~200-char Chinese summary entry inside the AIHOT daily
briefing, replacing a separate Hermes-specific cron job.

## Architecture

```
aihot_morning_briefing.py  (no_agent=True cron script)
├── fetch_json()             ← AIHOT API (unchanged)
├── fetch_hermes_brief()    ← GitHub Releases API (NEW)
├── sectioned_items()       ← AIHOT items only
└── build_briefing()        ← AIHOT + unconditionally appends Hermes entry
```

## The fetch_hermes_brief Function

```python
HERMES_RELEASES_URL = "https://api.github.com/repos/NousResearch/hermes-agent/releases"

def fetch_hermes_brief(now: dt.datetime) -> dict | None:
    """Fetch latest Hermes Agent releases and return a ~200-char summary item."""
    try:
        result = subprocess.run(
            ["curl", "-fsSL", "-H", "User-Agent: aihot-hermes/0.1",
             f"{HERMES_RELEASES_URL}?per_page=2"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        releases = json.loads(result.stdout)
        if not releases or not isinstance(releases, list):
            return None

        latest = releases[0]
        tag = latest.get("tag_name", "")
        name = latest.get("name", "")
        url = latest.get("html_url", "https://github.com/NousResearch/hermes-agent/releases")
        published = latest.get("published_at", "")
        body = latest.get("body", "") or ""

        # Extract tagline from > **The Surface Release.** ...
        tagline = ""
        match = re.search(r">\s*\*\*(.+?)\*\*\.?\s*(\S[^\\n]{0,120})", body)
        if match:
            tagline = match.group(1).strip()

        # Extract top 2 highlight titles from - **...**
        highlights = []
        for line in body.splitlines():
            m = re.match(r"^\s*-\s+\*\*(.+?)\*\*", line)
            if m:
                title = m.group(1).strip()
                if len(title) > 50:
                    title = title[:48] + "..."
                highlights.append(title)
                if len(highlights) >= 2:
                    break

        summary_parts = []
        if tagline:
            summary_parts.append(tagline)
        if highlights:
            summary_parts.append("亮点：" + "；".join(highlights))

        summary = ("，".join(summary_parts) if summary_parts
                   else "Hermes Agent 有新版本发布。")
        if len(summary) > 200:
            summary = summary[:197] + "..."

        prev_tag = releases[1].get("tag_name", "") if len(releases) > 1 else ""
        title = (f"Hermes Agent 更新：{name}（较 {prev_tag}）" if prev_tag
                 else f"Hermes Agent 更新：{name}")

        return {
            "title": title,
            "summary": summary,
            "source": "GitHub：NousResearch/hermes-agent",
            "url": url,
            "publishedAt": published,
            "category": "hermes",
        }
    except Exception:
        return None
```

## Guaranteeing Inclusion in build_briefing

Keep the Hermes item separate from AIHOT items before clustering. Append it
unconditionally after the main section:

```python
build_briefing():
    aihot_items = [...from API...]
    hermes_item = fetch_hermes_brief(now)

    selected_clusters = select_digest_clusters(aihot_items)
    # ... render AIHOT items ...

    if hermes_item:
        lines.append("## 项目动态")
        pub = human_time(hermes_item.get("publishedAt"), now)
        lines.append(f"11. **{hermes_item['title']}** — {hermes_item['source']}")
        lines.append(f"   {pub}")
        lines.append(f"   {hermes_item['summary']}")
        lines.append(f"   {hermes_item['url']}")
```

## Category Registration

```python
CATEGORY_LABELS = {"hermes": "项目动态", ...}
CATEGORY_ORDER = [..., "hermes", None]
```

## Cron Job Consolidation Steps

1. `cronjob(action='list')` — find the hermetic project cron job (e.g. "Hermes Agent 每日动态") and the main briefing cron job.
2. `cronjob(action='remove', job_id='<hermes-job-id>')` — delete the separate one.
3. `cronjob(action='update', job_id='<main-job-id>', name='AIHOT 每日早报（含 Hermes 动态）', workdir='/path/to/project')` — update name and working directory.

## Release Body Parsing

The GitHub release notes for Hermes Agent follow a consistent format:

```
# Hermes Agent v0.16.0 (v2026.6.5)

**Release Date:** June 5, 2026
**Since v0.15.2:** 874 commits · 542 merged PRs · 1,962 files changed ...

> **The Surface Release.** Hermes meets you wherever you work. ...

---

## ✨ Highlights

- **Hermes Desktop — a real native app, not a terminal wrapper** — ...
- **Run the desktop app against a remote Hermes** — ...
```

The regex patterns extract:
- `> \*\*(.+?)\*\*` → the tagline (one-line summary of the release theme)
- `- \*\*(.+?)\*\*` → individual highlight titles

## Note on Language

GitHub release bodies are always in English. The tagline and highlight titles
are extracted as-is. For full Chinese translation, switch from `no_agent=True`
to agent-mode translation (see `references/content-localization.md`).
