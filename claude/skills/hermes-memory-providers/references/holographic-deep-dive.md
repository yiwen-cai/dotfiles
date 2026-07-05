# Holographic Memory Deep Dive

## Technical Architecture

### HRR (Holographic Reduced Representations)

Holographic uses **HRR-based algebraic memory** rather than traditional vector databases:

- Memory is represented via **superposition/associative recovery** — algebraic operations on distributed representations
- Design tradeoff: favors compact algebraic storage/retrieval over graph-like fact structuring
- Retrieval is **compositional** — can combine and decompose memory representations algebraically

### Trust Scoring System

- Every fact has an associated confidence/weight score
- **Confirmation** across sessions increases weight
- **Contradiction** by newer information decreases weight over time
- Goal: reduce unbounded error accumulation from stale or noisy observations
- This makes Holographic **self-correcting** — bad memories naturally fade, good ones persist

### Storage Layer

- **Backend:** Local SQLite (`~/.hermes/memory_store.db`)
- **Schema:** Structured facts with categories, tags, entities
- **Latency:** Very fast local recall (no network calls, no embedding computation)
- **Footprint:** Minimal — no external services, no Python dependencies beyond Hermes core

### Data Flow

```
Conversation → Model identifies important facts → fact_store(tool) → SQLite
                                                    ↓
Next session ← Holographic recalls high-trust facts ← Trust scoring
                                                    ↓
User/Model corrects facts → fact_feedback(tool) → Updates trust scores
```

## Comparison with Other Providers

| Dimension | Holographic | Hindsight | Honcho | OpenViking |
|-----------|-------------|-----------|--------|------------|
| Core idea | HRR algebraic memory | Structured fact memory | User modeling + dialectic | Session archival + semantic search |
| Storage | Local SQLite | Local or Cloud | Cloud/Self-hosted | Self-hosted |
| External deps | **None** | Optional LLM/embedding | `honcho-ai` + API | Embedding model |
| Retrieval | Algebraic recall | Semantic + keyword + graph + temporal | Semantic + reasoning | Semantic search |
| Trust model | Explicit trust scoring | Evolving facts/entities | Dialectic reasoning | — |
| Shared memory | Not primary | First-class | Multi-peer workspace | — |
| Best fit | Local lightweight | Durable cross-session | Multi-agent user alignment | Long session archiving |

## Known Issues & Workarounds

### Issue #4781: Tools not injected into agent loop

**Symptom:**
```
Memory provider 'holographic' registered (2 tools)
# But model says:
{"error": "Unknown tool: fact_store"}
```

**Root cause:** Gateway-level registration and per-session agent loop initialization are separate code paths. The gateway registers the provider but the sequential memory handler doesn't route through the memory manager.

**Workaround:**
1. `/reset` to start a new session
2. If persists, fully exit and restart hermes
3. Verify with `hermes memory status` that provider is active

**Code path analysis:**
- Concurrent path (`_invoke_tool`): routes through `memory_manager` ✓
- Sequential path (`handle_function_call`): missing `memory_manager` routing ✗
- `on_memory_write` bridge exists in concurrent path but not sequential path

### Issue #4708: Sequential path missing memory routing

Related to #4781. The sequential memory handler lacks:
1. `memory_manager` routing between `delegate_task` handler and `handle_function_call` fallthrough
2. `on_memory_write` bridge to mirror built-in writes to external provider

### Issue #4726: Profile-scoped namespaces

**Symptom:** Multiple Hermes profiles share the same `memory_store.db`

**Impact:**
- All profiles read/write to the same fact pool
- No profile attribution on facts
- Trust/feedback system gets muddied when different roles rate the same facts

**Workaround:** Use separate `HERMES_HOME` directories for strict isolation

**Potential fix directions:**
- Option 1: Separate DB per profile (`memory_store.<profile>.db`)
- Option 2: Shared DB with `profile` column for attribution
- Option 3: Namespace prefix on fact IDs

## When to Choose Holographic

### ✅ Choose Holographic when:

1. **Zero external dependencies** — no API keys, no LLM calls, no embedding models, no PostgreSQL
2. **Low latency** — local SQLite retrieval is extremely fast
3. **Structured facts** — need categories, tags, entities on memories
4. **Self-correcting** — want trust scoring to naturally fade bad memories
5. **Privacy-first** — all data stays local, no cloud calls
6. **Cost-sensitive** — completely free, no usage limits

### ❌ Avoid Holographic when:

1. **Semantic search needed** — Holographic does algebraic recall, not semantic similarity
2. **Cross-session search** — no session search capability (use OpenViking)
3. **Multi-strategy retrieval** — no keyword/graph/temporal search (use Hindsight)
4. **Team sharing** — no built-in shared memory (use Hindsight Cloud)
5. **Rich knowledge extraction** — no LLM-based fact extraction at retention time

## External References

- Official Hermes docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers
- Technical comparison: https://hindsight.vectorize.io/guides/2026/04/21/guide-hermes-agent-holographic-memory-technical-deep-dive
- Reddit user testing: https://www.reddit.com/r/hermesagent/comments/1tms3g6/memory_providers_i_tested_them_all
- GitHub issues:
  - #4781: Holographic tools not injected
  - #4708: Sequential path missing memory routing
  - #4726: Profile-scoped namespaces
  - #24418: Feature request for multiple simultaneous providers

## Session-Specific Notes

- 2026-06-19: Successfully switched user from built-in-only to Holographic
- Config location: `~/.hermes/config.yaml` line 433
- Verified: `hermes memory status` shows `Provider: holographic`
- Post-switch requirement: `/reset` or restart hermes for tools to activate
- **Tested and confirmed working:** `add`, `search`, `list`, `update`, `fact_feedback` operations
- **Tested with limitations:** `probe`, `related`, `reason` return empty results when entities aren't explicitly tagged during storage — use `search` for reliable retrieval
- **Pitfall discovered:** `hermes memory setup` interactive picker cancels with "No changes saved" in non-TTY environments; prefer `hermes config set memory.provider holographic`
- **Verification:** 6 test facts stored successfully, database `~/.hermes/memory_store.db` created at 4096 bytes
