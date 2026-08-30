# AI Briefing Sources

Use this reference when building an AI/LLM daily briefing pipeline. The goal is a small, reliable source mix rather than a large fragile scraper set.

## Recommended First-Version Source Mix

| Section | Source | Access | API key | Notes |
|---|---|---|---:|---|
| Industry news | TechCrunch AI | RSS: `https://techcrunch.com/category/artificial-intelligence/feed/` | No | Startups, funding, product, policy. |
| Industry news | VentureBeat AI | RSS: `https://venturebeat.com/category/ai/feed/` | No | Enterprise AI, applied AI, productization. |
| Industry news | MIT Technology Review AI | RSS: `https://www.technologyreview.com/topic/artificial-intelligence/feed/` | No | Higher-quality trend and impact coverage. |
| Industry news | The Decoder | RSS: `https://the-decoder.com/feed/` | No | AI-focused models/products/policy coverage. |
| Official updates | OpenAI News | RSS: `https://openai.com/news/rss.xml` | No | Official OpenAI announcements. |
| Official updates | Google DeepMind Blog | RSS: `https://deepmind.google/blog/rss.xml` | No | Research and model releases. |
| Official updates | Google AI Blog | RSS: `https://blog.google/innovation-and-ai/technology/ai/rss/` | No | Optional extension. |
| Official updates | Microsoft AI Blog | RSS: `https://blogs.microsoft.com/ai/feed/` | No | Optional extension for Copilot/Azure AI. |
| Community heat | Hacker News Algolia | JSON: `https://hn.algolia.com/api/v1/search_by_date` | No | Search recent AI/LLM stories and rank by points/comments. |
| Open source | GitHub REST Search | JSON: `https://api.github.com/search/repositories` | Optional | Prefer with token for higher rate limits. Cache stars for 24h growth. |
| Papers | arXiv API | Atom: `https://export.arxiv.org/api/query` | No | Search cs.CL/cs.AI/cs.LG/cs.CV/stat.ML. |

## Suggested HN Query

Use several simple keyword queries rather than one complex query when the API parser behaves unexpectedly:

```text
AI
LLM
OpenAI
Claude
Gemini
Anthropic
agent
inference
```

Post-process:

- Keep recent 24-48 hour stories.
- Score by a weighted combination of points and comment count.
- Treat HN as a heat signal, not authoritative source of record.

## Suggested GitHub Queries

Use topic queries with minimum star thresholds and recent activity filters:

```text
topic:llm stars:>500 pushed:>YYYY-MM-DD
topic:agents stars:>200 pushed:>YYYY-MM-DD
topic:rag stars:>200 pushed:>YYYY-MM-DD
topic:inference stars:>200 pushed:>YYYY-MM-DD
topic:machine-learning stars:>1000 pushed:>YYYY-MM-DD
topic:multimodal stars:>200 pushed:>YYYY-MM-DD
```

Notes:

- GitHub Search does not directly provide daily star growth.
- Save previous run stars locally and compute `star_delta_24h` on later runs.
- GitHub Trending RSS, e.g. `https://mshibanami.github.io/GitHubTrendingRSS/daily/python.xml`, is a useful no-auth fallback but should not be the primary source if the REST API is available.

## Suggested arXiv Query Strategy

Categories:

```text
cs.CL
cs.AI
cs.LG
cs.CV
stat.ML
```

Keywords:

```text
large language model
LLM
agent
RAG
reasoning
alignment
inference
multimodal
diffusion
```

Implementation notes:

- arXiv returns Atom XML.
- Respect low request rates and use retry/backoff.
- Prefer recent 24-48h results, but include 72h on Mondays or after holidays if the briefing would otherwise be sparse.

## Sources to Defer

| Source | Why defer | When to add |
|---|---|---|
| Semantic Scholar | No-key usage can hit 429 quickly. | Add with API key to enrich papers with citations and metadata. |
| GDELT | Very broad and noisy; can hit rate limits. | Add when policy/regulation/global news becomes a first-class section. |
| NewsAPI | Requires key; free tier constraints. | Add if the user wants a unified news aggregator and accepts key management. |
| Reddit RSS | Noisy; needs stronger filtering. | Add for community-specific sections such as LocalLLaMA. |
| Many Chinese media feeds | Often duplicate English/source-of-record items. | Add later as a Chinese-language supplement. |

## Verification Snippet

```bash
python3 - <<'PY'
import urllib.request
urls = [
    'https://techcrunch.com/category/artificial-intelligence/feed/',
    'https://venturebeat.com/category/ai/feed/',
    'https://www.technologyreview.com/topic/artificial-intelligence/feed/',
    'https://the-decoder.com/feed/',
    'https://openai.com/news/rss.xml',
    'https://deepmind.google/blog/rss.xml',
    'https://hn.algolia.com/api/v1/search_by_date?query=LLM&tags=story&hitsPerPage=1',
    'https://api.github.com/search/repositories?q=topic:llm+stars:%3E1000&sort=updated&order=desc&per_page=1',
]
for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ai-daily-briefing/0.1'})
        with urllib.request.urlopen(req, timeout=12) as r:
            print(r.status, url, r.headers.get('content-type', '')[:50])
    except Exception as e:
        print('ERR', url, type(e).__name__, str(e)[:120])
PY
```
