---
name: automated-daily-briefings
description: Build scheduled daily briefing pipelines that collect trusted sources, summarize them, render artifacts, and
  deliver through messaging platforms.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Automated Daily Briefings

Use this skill when the user wants a recurring news/research/market/engineering briefing delivered on a schedule, especially when the output includes both a concise message and a rendered artifact such as HTML, Markdown, PDF, or a dashboard snapshot.

## Core Principle

Prefer a small number of stable aggregated sources over many hand-written website integrations. The first version should optimize for reliability and maintainability, not maximal coverage.

## Recommended Architecture

1. **Collect structured inputs**
   - RSS/Atom feeds for publishers and official blogs.
   - Public JSON APIs where available.
   - Domain-specific APIs such as arXiv, GitHub Search, Hacker News Algolia, etc.
   - Local cache for deduplication, score history, and growth metrics.
2. **Normalize to one schema**
   - Every source adapter should emit the same item shape.
   - Include source, title, URL, timestamp, summary, tags, metrics, and a score.
3. **Separate collection from generation**
   - Collection scripts should produce JSON and logs only.
   - The agent or renderer should perform selection, synthesis, HTML generation, and delivery.
4. **Render artifacts deterministically**
   - Use a template for HTML/Markdown/PDF.
   - Save both source JSON and final artifacts by date.
5. **Deliver through the scheduler**
   - Use Hermes cron for scheduled agent runs and gateway delivery.
   - Include `MEDIA:/absolute/path/to/file` for attachments when delivering through messaging platforms that support media.
6. **Verify manually before enabling daily runs**
   - Trigger one run on demand.
   - Confirm source JSON exists, rendered artifact opens, and the message is readable.

## Minimal Project Layout

```text
briefing-project/
├── task_plan.md
├── findings.md
├── progress.md
├── data_sources.md
├── scripts/
│   └── collect_sources.py
├── templates/
│   └── briefing.html
├── data/
│   └── source_cache.json
├── output/
│   ├── YYYY-MM-DD.json
│   └── YYYY-MM-DD.html
└── logs/
```

When the user explicitly asks to maintain the project with `planning-with-files`, create or update `task_plan.md`, `findings.md`, and `progress.md` in the project root before implementation.

## Generic Item Schema

```json
{
  "generated_at": "2026-05-11T09:00:00+08:00",
  "window_hours": 48,
  "items": [
    {
      "id": "stable-hash",
      "type": "news | official | community | github | paper | other",
      "source": "source name",
      "title": "item title",
      "url": "https://example.com/item",
      "published_at": "2026-05-11T00:00:00Z",
      "summary": "short raw summary",
      "authors": [],
      "tags": [],
      "metrics": {
        "stars": null,
        "forks": null,
        "points": null,
        "comments": null,
        "citations": null
      },
      "score": 0.0
    }
  ]
}
```

## Source Selection Guidelines

- Start with 5-10 total sources across all categories.
- Prefer RSS/Atom and official APIs over scraping.
- Include original sources where possible, such as official blogs, repo URLs, paper URLs, or primary announcements.
- Treat social/community sources as heat signals, not authoritative evidence.
- Make API-key-dependent sources optional unless the user already has credentials configured.
- Cache previous runs when metrics such as star growth or repeated stories matter.

## Quality Rules

- Every factual item in the final briefing should have a source URL.
- Deduplicate by canonical URL, normalized title, and source cluster.
- Prefer official/source-of-record links over secondary media links.
- Separate facts from model-generated trend judgments.
- If sources fail or produce too little data, send a degraded but explicit report rather than inventing content.

## AI / LLM Briefing References

For an AI daily briefing with manual/free source integration, see `references/ai-briefing-sources.md` for a proven first-pass source mix using RSS, Hacker News Algolia, GitHub Search, and arXiv.

When the user wants to avoid hand-maintaining many sources, prefer the aggregator-first pattern in `references/third-party-ai-aggregators.md`: Tavily or Exa as the main search/aggregation layer, plus Hugging Face Daily Papers and GitHub Trending/Search for vertical ranking signals.

For Weixin-friendly AIHOT digests, see `references/aihot-compact-digest.md`: the reference covers **two modes** — Compact (merge + truncate) and Full (no truncation, complete summaries). Use Full mode when the user has said "不要省略" or corrected truncated output. Default to Compact only when no preference is known.

## Artifact Rendering Guidelines

For HTML briefings intended to be opened as messaging attachments, prefer a deterministic, mobile-first, standalone HTML file:

- Inline CSS in a single file; avoid JavaScript, external fonts, CDN CSS, images, and framework bundles unless the user explicitly needs them.
- Use a narrow single-column layout with a max width around 720px, semantic `<main>`, `<section>`, and `<article>` elements, and title links that open original sources.
- Recommended sections: top metadata/statistics, 3-5 highlights, news/industry items, GitHub/open-source items, papers/research items, and a collapsed collection-status section.
- Keep rendered density bounded. For a daily briefing, show roughly 18-24 cards total, for example 6-8 news items, 5-8 GitHub items, and 5-8 paper items; archive the full JSON separately.
- Escape all text fields, validate URLs to `http://` or `https://`, and treat source summaries as untrusted content.
- Display only the most useful metrics per card: source/date/tags for news, stars/forks/language for GitHub, and authors/upvotes/comments for papers.
- **Localize the template strings** — if the user reads Chinese (or another language), translate all hardcoded section headers, badges, labels, fallback text ("Untitled" → "无标题"), metrics labels ("Star" → "★", "Upvote" → "▲"), footer text, and the `<title>` / `<h1>`. The English defaults in a render script are a template, not a final output. Verify localized rendering before triggering the cron job.

**Skip HTML attachments for WeChat delivery** — when the delivery target is WeChat (or any platform where the user has said "不用生成 HTML 附件了"), do NOT generate an HTML file. Remove the `render_html()` call and the `MEDIA:` output line from the script. Instead, list ALL collected items with their full summaries in the plain-text output. The text message body IS the delivery artifact.

**Show ALL items, not just a subset** — in `build_text_summary()`, iterate over ALL items (not `items[:6]`). The user wants every item visible in the chat, not a "top N + see HTML" split.
   For translation of **collected content** (item titles, summaries, release notes fetched from English sources), see the "Content Localization Beyond Template Strings" section and `references/content-localization.md`.
- Run `ruff format` after editing any Python script in the project.
- Verify with formatting/static checks, local browser open, article count, horizontal-overflow check, and absence of external assets before saying the artifact is done.

## Dual-channel delivery notes

When a briefing must go to both a messaging platform and email, and email is not available as a Hermes cron `deliver` target, see `references/dual-channel-briefing-delivery.md`. The durable pattern is a `no_agent=True` script that prints the messaging summary and `MEDIA:` attachment while separately attempting email delivery through Himalaya or SMTP, then reports the real email status in the messaging body.

## Merging Project Release Notes into a Main Briefing

When the user wants project-level dynamics (e.g., a GitHub repo's latest releases and commits) merged into a main briefing as a fixed entry rather than maintained as a separate cron job:

1. **Add a fetch function** — `fetch_<project>_brief(now)` that calls the GitHub releases API.
2. **Parse the release body** for: tagline (`> **...**`), highlight bullets (`- **...**`), and stats (commits/PRs/files).
3. **Build a ~200-char Chinese summary** from tagline + top 2 highlights. Keep it concise — the user already gets the main briefing for detail.
4. **Add a new category** to `CATEGORY_LABELS` and `CATEGORY_ORDER` (e.g. `"hermes": "项目动态"`).
5. **Guarantee inclusion** — in `build_briefing()`, keep the project item separate from the main AI items so it's never cut by top-N clustering. Append it after the main section unconditionally.
6. **Consolidate cron jobs** — delete the separate project cron job, update the main briefing cron job's name and workdir.
7. **Do NOT generate HTML or separate MEDIA output** for the merged entry — it lives in the text body.

See `references/hermes-project-briefing.md` for a full implementation example.

## Hermes Cron Notes

Use the `hermes-agent` skill for exact cron CLI details. A typical scheduled prompt should be self-contained and specify:

- Schedule, e.g. `0 9 * * *`.
- Project working directory.
- Collection script path and any proxy flags.
- Output paths.
- Required toolsets, normally `terminal`, `file`, and optionally `web`.
- Delivery format, including the concise text and `MEDIA:/absolute/path/to/artifact` attachment.

**MEDIA attachment pattern:** The cron prompt must explicitly instruct the model to include a `MEDIA:/absolute/path/to/file` line at the end of its final response. Without this explicit instruction, the model is unlikely to generate a MEDIA reference, and no file will be attached. Reference the actual date — the prompt should tell the agent to compute it via `date '+%Y-%m-%d'` rather than hardcoding.

**Cron prompt pitfalls:**
- `last_status=ok` does NOT guarantee the user received the message. It means agent execution completed. Check `last_delivery_error` separately.
- The cron job can show `completed successfully` while gateway delivery (`live adapter`) fails afterward. Always check gateway logs for send status.
- A cron job with `deliver=origin` but no configured origin profile falls back to the weixin home channel — which may or may not be connected.

### Content Localization Beyond Template Strings

When the collection script (`no_agent: true`) fetches data from English-language sources (GitHub, Tavily, Exa, etc.), the raw item titles and summaries are in English. Template-string localization only covers the UI framework ("Untitled" → "无标题"). **The collected content itself remains untranslated.**

**Two approaches to fix this:**

| Approach | When to use | Trade-off |
|---|---|---|
| **Agent-driven (switch no_agent=false)** | Content is in a language the user doesn't read, or the user explicitly asks for Chinese output. | Uses tokens per run. Prompt must be precise about what to translate and what to preserve. The cron `run` action may not trigger immediate execution for agent-mode jobs. |
| **Script-level LLM call** | The script can call a translation API. | Adds API dependency. No built-in model — must add a `curl` or `subprocess` call to an LLM endpoint. |

**Agent-mode switch recipe (preferred):**

1. List existing jobs to find the target: `cronjob(action='list')`
2. Update with `action='update'`:
   - Set `no_agent=false`
   - Clear the `script` field by passing empty string `""`
   - Provide a self-contained `prompt` (see template below)
   - Update `enabled_toolsets` to include `terminal`, `file` (for reading/writing artifacts), and optionally `web`
   - The old `prompt_preview` is auto-replaced; no need to clear it
3. The prompt must be explicit about:
   - Running the collection script first via `terminal`
   - Capturing stdout (which contains the text summary and `MEDIA:` path)
   - Translating specific fields: titles, descriptions, summaries, release notes, commit messages, source names
   - Preserving: URLs, technical names (Hermes Agent, GitHub, NousResearch, etc.), version numbers (v0.x.x), tags, hashes (sha), HTML/CSS tags, `MEDIA:` markers
   - Re-writing the HTML artifact with translated content via `write_file` or `patch`
   - Outputting the final Chinese text summary + `MEDIA:` line

**Translation prompt template:**

```
执行以下操作：
1. 运行脚本 <script_path>，获取输出（包含文本摘要和 MEDIA: 附件路径）。
2. 将输出的文本摘要部分中的所有英文内容（条目标题、来源描述、摘要等）翻译成中文，保持原有的 Markdown 格式和结构不变。
3. 找到 MEDIA: 指向的 HTML 文件，阅读该 HTML 文件，将其中的所有英文内容（标题、摘要、描述等）翻译成中文，保持 HTML 结构和样式不变。翻译完成后重新写入该 HTML 文件。
4. 输出最终的中文文本摘要，并在末尾附带 MEDIA: 路径（保持原有的相对路径格式）。

注意：只翻译英文内容，不要改动中文标题（如"重点条目""本次采集到"等）、URL 链接、数字、日期、技术名称（如 Hermes Agent、GitHub 等专有名词保留原文）和 MEDIA: 标记。
```

**Manual re-send pattern:**

When the cron job already ran for today but the user wants it re-sent with changes (e.g., translation):

1. Run the collection script manually: `terminal(command='cd <workdir> && python3 <script_path>', timeout=200)`
2. Capture the raw output (text summary + `MEDIA:/path/to/file`)
3. Delegate translation to a subagent for large HTML content: `delegate_task(goal='translate content to Chinese', context='<translation rules>', toolsets=['terminal', 'file'])`
4. Verify the HTML was correctly updated by checking translated card titles
5. Send via `send_message(target='weixin', message='<translated summary>\nMEDIA:/path/to/html')` — the user's home channel target is the weixin chat_id from the cron job's `deliver` field

See `references/content-localization.md` for detailed translation conventions (what to preserve, version name mappings, commit message patterns).

## Delivery Troubleshooting

If a scheduled briefing appears not to arrive, use `references/cron-delivery-troubleshooting.md`. Key rule: verify three layers separately before re-triggering repeatedly:

1. **Agent/model execution** — `hermes cron list` plus scheduler logs for `completed successfully` versus provider errors.
2. **Artifact generation** — confirm `data/YYYY-MM-DD.json` and `output/YYYY-MM-DD.html` exist and parse/open.
3. **Gateway delivery** — inspect gateway logs for `delivered to ... via live adapter`, `live adapter delivery ... failed`, `send chunk failed`, and `send_document failed`.

For Weixin, `Cannot connect to host ilinkai.weixin.qq.com:443 ssl:default [None]` is a gateway network delivery issue, not an AI briefing collector issue.

## Pitfalls

| Pitfall | Avoidance |
|---|---|
| User did not receive the message, so the job must have failed | Check logs first. The job can complete and generate artifacts while Weixin delivery fails afterward. |
| Re-triggering before checking delivery logs | Inspect `~/.hermes/logs/{agent,gateway,errors}.log` around the run time first, then decide whether to retry or fix gateway networking. |
| Trusting `last_status` immediately after a just-finished run | For freshest truth, use scheduler/gateway logs; cron list may still show a prior run briefly or in some delivery-fallback edge cases. `last_status=ok` only means agent execution succeeded — check `last_delivery_error` for the actual delivery result. |
| Too many sources in v1 | Start small; expand only after the pipeline is stable. |
| Custom scraping for every site | Use RSS, Atom, existing APIs, or aggregator APIs first. |
| One monolithic agent prompt | Put deterministic collection in scripts; leave synthesis to the agent. |
| No source URLs | Require URLs in normalized JSON and final output. |
| No cache | Cache prior run metadata when tracking growth, deduplication, or repeated stories. |
| Confusing collector networking with UI/server networking | Scope proxies to the collector first. If HF/arXiv timeout but `curl -x` succeeds, add a script-level `--proxy` / env var such as `AI_BRIEFING_PROXY`; do not restart WebUI/gateway unless that process is the one timing out. |
| Default truncation in scripts | Both `aihot_morning_briefing.py` and `hermes_agent_news.py` have separate truncation functions (`shorten()` / `clean_text()`). If the user says "不要省略" / "完整内容", change both: remove `…` suffixes, increase limits to `99999`, and remove explicit small-limit calls like `clean_text(x, 300)`. Verify no `…` in output. |
| HTML attachment on WeChat | The user may reject HTML attachments for messaging delivery. Remove the entire `render_html()` function, the `MEDIA:` print line in `main()`, and the `html_path` variable. The text output is the sole delivery artifact. |
| Only N items shown in text | Scripts may default to `items[:6]` in `build_text_summary()`. The user wants ALL items listed with their full summaries, not just highlights. Remove the slice; iterate all items. |
| English release notes in output | GitHub releases and commits are in English. Script-level collection (`no_agent: true`) cannot translate them. If the user wants Chinese overviews, either switch to agent-mode translation or accept English summaries as-is from the source. |
| Cron script name hides real editable wrapper | For `no_agent=True` jobs, `cronjob(action='list')` may show a script such as `aihot_morning_briefing.py` that resolves under `~/.hermes/scripts/`, even when the job also has a project `workdir`. Always locate and inspect the exact cron script before editing project-local helpers; the real delivery formatting may live in the Hermes script wrapper, not in `workdir/scripts/`. |
| Markdown formatting looks bad in WeChat | For Weixin text-only briefings, avoid `**bold**`, `##` headings, and indented Markdown bullets. Use plain section headers like `【行业动态】3 条`, numbered items, and explicit `来源：` / `摘要：` / `链接：` labels. Verify the real cron entrypoint output, not just helper functions. |
| Compact digest logic violates full-output preference | AIHOT-style scripts may cluster similar items and cap output with constants such as `MAX_DIGEST_ITEMS` plus `select_digest_clusters()`. When the user says the push formatting is wrong or has previously required no truncation, bypass clustering for the chat body and iterate every item by category. Keep project-level release notes as one fixed merged entry if that is the established delivery rule. |
| Fixing a project-local script but cron still uses the old wrapper | After patching, run the exact path shown/resolved from the cron job, e.g. `python3 ~/.hermes/scripts/aihot_morning_briefing.py`, and assert no `MEDIA:`, no HTML attachment hint, no `**`, no `##`, and no `…` when the user's rule forbids truncation. |