---
name: hermes-memory-providers
description: "Configure and switch between Hermes Agent external memory providers: Holographic, Hindsight, Honcho, OpenViking, Mem0, RetainDB, ByteRover, Supermemory, Memori."
version: 1.0.0
author: Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, memory, configuration, holographic, hindsight, honcho, openviking]
    related_skills: [hermes-agent]
---

# Hermes Agent Memory Providers

Hermes Agent ships with 9 external memory provider plugins that give the agent persistent, cross-session knowledge beyond the built-in `MEMORY.md` and `USER.md`.

**Core rule:** Only **one** external provider can be active at a time — the built-in memory is always active alongside it.

## Quick Commands

```bash
hermes memory status      # Check current provider
hermes memory setup       # Interactive picker to switch provider
hermes memory off         # Disable external provider
hermes config set memory.provider <name>  # Direct config switch
```

Config file: `~/.hermes/config.yaml`
```yaml
memory:
  provider: holographic   # or hindsight, honcho, mem0, openviking, retaindb, byterover, supermemory, memori
```

**After switching:** Run `/reset` or restart hermes for changes to take effect.

---

## Provider Comparison Matrix

| Provider | Core Tech | Storage | External Deps | Cost | Best For |
|----------|-----------|---------|-----------------|------|----------|
| **Holographic** | HRR algebraic memory | Local SQLite | **None** | Free | Lightweight local memory, zero API cost |
| **Hindsight** | Structured knowledge graph | Local/Cloud | Optional LLM/embedding | Free(local)/paid(cloud) | Complex agent memory, multi-strategy retrieval |
| **Honcho** | User modeling + dialectic reasoning | Cloud/Self-hosted | `pip install honcho-ai` | Paid/Free self-hosted | Multi-agent user alignment |
| **OpenViking** | Session archival + semantic search | Self-hosted | Embedding model | Free | Long session archiving, semantic search |
| **Mem0** | Vector memory API | Cloud/Self-hosted | API key | Paid/Free self-hosted | Drop-in personalization |
| **RetainDB** | — | — | — | — | — |
| **ByteRover** | Knowledge tree in Markdown | Local/Cloud | — | Freemium | Multi-hop/temporal reasoning |
| **Supermemory** | Search-heavy RAG | Cloud | API key | Paid | Search-heavy workflows |
| **Memori** | — | — | — | — | — |

---

## Holographic (Local, Zero Dependency)

### What it is
- **HRR-based** (Holographic Reduced Representations) algebraic memory system
- Stores structured facts with categories, tags, entities
- Uses **trust scoring** — memories gain/lose weight based on confirmation/contradiction across sessions
- Built on local SQLite (`~/.hermes/memory_store.db`)
- **Zero external dependencies** — no API keys, no LLM calls, no embedding models

### Tools (2)
- `fact_store` — Store structured facts with metadata
- `fact_feedback` — Provide feedback on existing facts (confirm/correct/negate)

### Switching to Holographic

```bash
# Method 1: Interactive (may cancel if no TTY — prefer Method 2)
hermes memory setup
# Select "holographic" from the picker

# Method 2: Direct config (recommended — avoids TTY issues)
hermes config set memory.provider holographic

# Verify
hermes memory status

# Activate (restart session)
/reset   # or exit and restart hermes
```

**Pitfall:** `hermes memory setup` runs an interactive picker that may cancel with "No changes saved" if the terminal environment doesn't support the curses UI. Always fall back to `hermes config set memory.provider holographic`.

### When to Choose Holographic
✅ **Choose when:**
- You want **completely local** memory with zero external API calls
- You need **low-latency** memory retrieval
- You want **structured fact storage** with categories/tags/entities
- You value **self-correcting memory** via trust scoring
- You don't need cross-session semantic search (use OpenViking or Hindsight for that)

❌ **Avoid when:**
- You need **semantic search** across sessions → use OpenViking
- You need **multi-strategy retrieval** (semantic + keyword + graph + temporal) → use Hindsight
- You need **team-shared memory** → use Hindsight Cloud

### Known Issues

⚠️ **GitHub Issue #4781** — `fact_store`/`fact_feedback` tools may not inject into agent tool list
- Symptom: Model reports `"Unknown tool: fact_store"`
- Workaround: Try `/reset` or restart hermes process
- Root cause: Gateway-level registration and per-session agent loop initialization are separate code paths

⚠️ **GitHub Issue #4726** — Multi-profile shared database
- All profiles share the same `~/.hermes/memory_store.db` by default
- Facts from different profiles mix together with no attribution
- Monitor issue for profile-scoped namespace fix

⚠️ **Entity probe/reason/related may return empty** — HRR matching sensitivity
- Symptom: `fact_store(action="probe", entity="...")` returns `{"count": 0}` even when facts exist
- Cause: HRR-based entity resolution uses exact string matching on extracted entities; if the entity wasn't explicitly tagged during `add`, probe won't find it
- Workaround: Use `action="search"` with keyword queries instead of entity probe for reliable retrieval
- Note: This is expected behavior for HRR algebraic memory — compositional retrieval works best when entities are explicitly bound during storage

### Storage Details
- Database: `~/.hermes/memory_store.db` (SQLite)
- No config file needed — works out of the box after activation
- Trust scores evolve automatically based on `fact_feedback` usage

---

## Hindsight (Structured Knowledge Graph)

### What it is
- Stores **structured facts** rather than text chunks
- Multi-strategy retrieval: semantic + keyword + graph + temporal
- Supports **reflection synthesis** — automatically re-evaluates and consolidates knowledge
- Available in local (free) or cloud (paid) mode

### Best For
- Complex agent workflows requiring rich, durable memory
- Cross-session persistence with high retrieval accuracy
- Team-shared memory (cloud mode)
- Benchmark: LongMemEval 91.4–94.6%

### Setup
```bash
hermes memory setup
# Select "hindsight"
# For cloud: set HINDSIGHT_API_KEY in .env
# For local: leave blank, runs local daemon
```

---

## Honcho (User Modeling)

### What it is
- AI-native **cross-session user modeling** with dialectic reasoning
- Session-scoped context injection
- Two-layer context: base (summary + representation + peer card) + dialectic (LLM reasoning)
- Multi-peer model: one user peer per workspace, one AI peer per Hermes profile

### Best For
- Multi-agent systems where user context must align across different agent roles
- Scenarios requiring user representation and peer cards

### Setup
```bash
pip install honcho-ai
hermes memory setup
# Select "honcho"
```

Config: `$HERMES_HOME/honcho.json` or `~/.hermes/honcho.json`

---

## OpenViking (Session Archival)

### What it is
- **Tiered L0/L1/L2** memory loading with 80-90% token savings
- Session archival with semantic search
- Resource ingestion capabilities

### Best For
- Long-running sessions where context compression is critical
- Scenarios requiring session search and semantic recall

### Setup
```bash
hermes memory setup
# Select "openviking"
```

---

## Troubleshooting Memory Providers

### "Unknown tool: fact_store" (Holographic)
- The tool registered at gateway but didn't inject into the session
- **Fix:** `/reset` or restart hermes
- If persists: check `hermes memory status` confirms holographic is active

### Memory provider not showing in status
- Config may not have been read yet
- **Fix:** Ensure `memory.provider` is set in `~/.hermes/config.yaml`, then `/reset`

### Switching doesn't seem to work
- External provider changes require session restart
- **Fix:** `/reset` in CLI, or `/restart` in gateway, or exit and relaunch

### Multi-profile memory mixing (Holographic)
- All profiles share `~/.hermes/memory_store.db`
- No automatic profile attribution yet (GitHub #4726)
- **Workaround:** Use separate Hermes homes if strict isolation is needed

---

## Verification

After switching to Holographic, run the verification script to confirm everything works:

```bash
python3 ~/.hermes/skills/autonomous-ai-agents/hermes-memory-providers/scripts/verify-holographic.py
```

This checks: plugin import, instance creation, tool registration, fact storage, search retrieval, database file, and system prompt generation.

## References

- Official docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers
- Holographic deep dive: `references/holographic-deep-dive.md`
- Verification script: `scripts/verify-holographic.py`
- GitHub issues tracking: #4781 (tool injection), #4708 (sequential path), #4726 (profile namespaces)
