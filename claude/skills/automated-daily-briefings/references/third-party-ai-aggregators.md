# Third-Party Aggregator Sources for AI Daily Briefings

Use this reference when the user wants to avoid hand-maintaining many RSS/API integrations. The most maintainable pattern is one general search/aggregation API plus a few vertical, already-aggregated sources.

## Recommended Architecture

```text
Tavily or Exa
  -> AI news, company announcements, technical blogs, community discussion candidates

Hugging Face Daily Papers
  -> paper/research hot list

GitHub Trending or GitHub Search
  -> open-source project hot list

Agent / renderer
  -> deduplication, grouping, synthesis, HTML rendering, delivery
```

This is not fully one-source, but it avoids maintaining dozens of publisher feeds while preserving good coverage for news, papers, and repositories.

## Aggregator Options

| Source | Best use | API key | Notes |
|---|---|---:|---|
| Tavily | Agent-friendly web/news search and research-style queries | Yes | Good default for scheduled AI briefings; returns structured JSON with title, URL, content/snippet, score. |
| Exa | Semantic search over technical/web content | Yes | Strong for technical blogs, project pages, research-adjacent content; useful as backup/enrichment to Tavily. |
| Perplexity Sonar | Search plus answer/citations | Yes | Lowest implementation effort for candidate event lists, but less controllable than raw search result APIs. |
| Brave Search | General web/news search | Yes | Good if the pipeline needs more control over search results and ranking. |
| SerpAPI Google News | News search results | Yes | Better for media/news coverage than technical ecosystem coverage. |
| NewsAPI/Event Registry | News database/event monitoring | Yes | Useful for media monitoring or policy/regulation sections; less ideal as a full AI technical briefing source. |
| Feedly/Inoreader | RSS management | Usually | Still requires maintaining subscriptions; useful only if the user already has curated feeds. |
| RSSHub | Route-based RSS generation | Optional/self-hosted | Good for filling gaps; still creates route maintenance burden. |

## Recommended Query Set

Run a small set of stable queries daily, then dedupe and group results:

```text
latest AI news today OpenAI Anthropic Google DeepMind Meta Mistral
latest large language model news today agents inference training
new AI agent framework open source GitHub today
latest AI infrastructure inference training framework open source
LLM research breakthrough today reasoning alignment multimodal
AI startup funding regulation product launch today
```

Use simple query strings rather than overly clever Boolean syntax; general search APIs vary in parser behavior.

## Vertical Sources Worth Keeping

Even with a general aggregator, keep these vertical sources because they provide domain-specific ranking signals:

- **Hugging Face Daily Papers**: paper heat signal. If it times out, fall back to HF papers page scraping or arXiv search. Record failures but do not block the briefing.
- **GitHub Trending RSS**: no-auth open-source hot list. Treat as a useful fallback or complement.
- **GitHub REST Search**: structured repo metadata, stars, forks, language, updated time. Use it when rate limits allow; cache prior stars for growth metrics.

## Implementation Pattern

1. Load project-local `.env` for aggregator keys, not global shell profile files.
2. Make the collector degrade gracefully:
   - Tavily primary.
   - Exa fallback/enrichment.
   - HF Daily Papers for papers, with HF page/arXiv fallback.
   - GitHub Trending/Search for repositories.
3. Normalize all sources into the same schema:

```json
{
  "id": "stable-hash",
  "type": "news | github | paper | other",
  "source": "Tavily",
  "title": "...",
  "url": "...",
  "published_at": "...",
  "summary": "...",
  "authors": [],
  "tags": [],
  "metrics": {},
  "score": 0.0
}
```

4. Store source errors in the JSON output instead of failing the whole run.
5. Let the agent synthesize only from items with URLs; do not invent replacement content when a source fails.

## macOS Python SSL Pitfall

In some macOS Python installs, `urllib.request` may fail against Tavily/Exa with `SSL: CERTIFICATE_VERIFY_FAILED` even when `curl` succeeds. For small briefing collectors, a pragmatic workaround is to call APIs through `curl` subprocess and parse JSON. Alternative: install/configure `certifi` and pass an SSL context explicitly.

Do not encode this as "Python networking is broken"; it is an environment-specific certificate issue. The reusable lesson is to verify with `curl` and use a curl subprocess or certifi context when necessary.

## Local Proxy for Research Sources

When general aggregators work but research/academic sources such as Hugging Face Daily Papers or arXiv time out, test the local proxy separately and keep it scoped to the collector script instead of unrelated UI/server processes.

Recommended pattern:

```bash
# Probe the proxy itself.
curl -sS --connect-timeout 5 --max-time 10 -x http://127.0.0.1:7897 https://api.ipify.org

# Probe sources that were timing out.
curl -L -sS --connect-timeout 5 --max-time 25 -x http://127.0.0.1:7897 https://huggingface.co/api/daily_papers -o /tmp/hf_daily_papers.json
curl -L -sS --connect-timeout 5 --max-time 25 -x http://127.0.0.1:7897 'https://export.arxiv.org/api/query?search_query=cat%3Acs.CL&max_results=1' -o /tmp/arxiv.xml
```

Then add a collector-level option such as `--proxy http://127.0.0.1:7897` and/or `AI_BRIEFING_PROXY=http://127.0.0.1:7897`. Do not restart or reconfigure the chat WebUI/gateway unless that process itself is timing out; the collector script can use the proxy independently.

