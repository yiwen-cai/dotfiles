---
name: research-content-monitoring
description: Monitor research content sources — arXiv papers, RSS/Atom feeds, and AI news aggregators for staying current
  with the latest research.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Research Content Monitoring

Monitor research content sources to stay current with the latest papers, news, and developments.

## When to Use

- User wants to search for academic papers
- User wants to monitor RSS/Atom feeds
- User asks about recent AI news or developments
- Building an automated briefing pipeline
- Finding related work for a research project

## Three Source Types

| Source | Content | Update Frequency |
|--------|---------|------------------|
| **arXiv** | Academic papers | Daily |
| **RSS/Atom Feeds** | Blogs, news, publishers | Real-time |
| **AI News Aggregators** | Curated AI news | Daily/hourly |

## arXiv Search

### Basic Search
```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5"
```

### Query Syntax
| Prefix | Searches | Example |
|--------|----------|---------|
| `all:` | All fields | `all:transformer+attention` |
| `ti:` | Title | `ti:large+language+models` |
| `au:` | Author | `au:vaswani` |
| `abs:` | Abstract | `abs:reinforcement+learning` |
| `cat:` | Category | `cat:cs.AI` |

### Boolean Operators
```
# AND (default)
search_query=all:transformer+attention

# OR
search_query=all:GPT+OR+all:BERT

# AND NOT
search_query=all:language+model+ANDNOT+all:vision

# Exact phrase
search_query=ti:"chain+of+thought"
```

### Fetch Specific Papers
```bash
# By ID
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300"

# Multiple papers
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300,2401.12345"
```

### Semantic Scholar (Citations)
```bash
# Get paper details + citations
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,authors,citationCount"

# Get who cited it
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/citations?limit=10"

# Get recommendations
curl -s -X POST "https://api.semanticscholar.org/recommendations/v1/papers/" \
  -H "Content-Type: application/json" \
  -d '{"positivePaperIds": ["arXiv:2402.03300"]}'
```

### Common Categories
| Category | Field |
|----------|-------|
| `cs.AI` | Artificial Intelligence |
| `cs.CL` | Computation and Language (NLP) |
| `cs.CV` | Computer Vision |
| `cs.LG` | Machine Learning |
| `cs.CR` | Cryptography and Security |
| `stat.ML` | Machine Learning (Statistics) |

## RSS/Atom Feed Monitoring

### Installation
```bash
go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest
```

### Common Commands
```bash
# Add a blog
blogwatcher-cli add "My Blog" https://example.com

# Scan all blogs
blogwatcher-cli scan

# List unread articles
blogwatcher-cli articles

# Mark article read
blogwatcher-cli read 1
```

### Feed Discovery
- Auto-discovers RSS/Atom from blog homepages
- Falls back to HTML scraping with `--scrape-selector`
- Supports OPML import for bulk subscriptions

### Output Example
```
Unread articles (2):

  [1] [new] Paper Title
       Blog: arXiv cs.AI
       URL: https://arxiv.org/abs/2402.03300
       Published: 2026-04-02

  [2] [new] Blog Post Title
       Blog: Distill
       URL: https://distill.pub/2026/example
       Published: 2026-04-01
```

## AI News Aggregators

### AI HOT (Chinese)
Chinese AI news aggregator at aihot.virxact.com.

### Endpoints
| Endpoint | Purpose |
|----------|---------|
| `/api/public/daily` | Latest daily digest |
| `/api/public/daily/{YYYY-MM-DD}` | Specific date |
| `/api/public/items?mode=selected` | Curated items |
| `/api/public/items?mode=all` | All items |
| `/api/public/items?q={keyword}` | Search |

### Categories
- `ai-models` — Model releases/updates
- `ai-products` — Product releases
- `industry` — Industry news
- `paper` — Research papers
- `tip` — Tips and opinions

### Example
```bash
# Latest curated items
curl -sH "User-Agent: Mozilla/5.0 aihot-skill/0.2.0" \
  "https://aihot.virxact.com/api/public/items?mode=selected&take=50"

# Search for OpenAI
curl -sH "User-Agent: Mozilla/5.0 aihot-skill/0.2.0" \
  "https://aihot.virxact.com/api/public/items?q=OpenAI&take=30"
```

## Building Briefing Pipelines

### Architecture
1. **Collect** — RSS, APIs, feeds
2. **Normalize** — Common item schema
3. **Deduplicate** — By URL, title
4. **Rank** — By relevance, freshness
5. **Render** — HTML/Markdown artifact
6. **Deliver** — Cron + messaging

### Minimal Layout
```
briefing-project/
├── scripts/collect_sources.py
├── templates/briefing.html
├── data/source_cache.json
└── output/YYYY-MM-DD.html
```

### Quality Rules
- Every item must have a source URL
- Deduplicate by canonical URL
- Prefer official sources over secondary
- Separate facts from model-generated judgments
- Send degraded but explicit report if sources fail

## Rate Limits

| Source | Rate | Auth |
|--------|------|------|
| arXiv | ~1 req / 3 sec | None |
| Semantic Scholar | 1 req / sec | None (100/sec with key) |
| AI HOT | 600 req / min | None |
| RSS Feeds | Be polite | None |

## Related Skills

- `automated-daily-briefings` — For building automated pipelines
- `academic-research-output` — For writing up findings
- `arxiv` — Legacy arXiv skill (archived)
- `blogwatcher` — Legacy RSS skill (archived)
- `aihot` — Legacy AI HOT skill (archived)

## Local AIHOT Briefing Project

User maintains a local AIHOT daily briefing pipeline at `~/Documents/code/ai-daily-briefing`. See `references/aihot-daily-briefing.md` for project structure, manual run commands, and cron configuration.