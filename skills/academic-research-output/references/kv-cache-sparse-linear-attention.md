# KV Cache sparse / linear attention presentation notes

Use this reference when preparing or revising academic presentations on long-context LLM KV Cache optimization, especially when the user asks about sparse attention, GDN/Gated DeltaNet, or linear complexity.

## Core distinction

Do not collapse all "sparse attention" into "KV Cache reduction". Separate four mechanisms:

1. **Sparse access over explicit KV**
   - Full or page-structured KV usually still exists.
   - Each decode step reads only a selected subset, e.g. top-k tokens/pages/blocks.
   - Examples: Quest, MInference, LServe, some NSA selection components.
   - Effect: reduces bandwidth and attention compute; does not necessarily reduce total stored KV.

2. **Learned constant-budget sparse attention**
   - Training or fine-tuning learns a fixed-budget sparse pattern per query.
   - If each query attends to `k` keys and `k` is constant, attention edges fall from `O(T^2)` to `O(Tk)`, i.e. linear when `k` is fixed.
   - Examples: SPARSEK Attention, Native Sparse Attention (NSA).
   - Caveat: actual memory reduction depends on whether unselected KV can be discarded or avoided, not just masked.

3. **Linear / recurrent-state attention**
   - Replaces explicit per-token KV history with a fixed-size recurrent state.
   - Examples: Gated Delta Networks (GDN), Gated DeltaNet-2, FG²-GDN, Kimi Delta Attention.
   - Effect: changes the representation of history; decode state no longer grows linearly with context in the same way as softmax KV cache.
   - Caveat: fixed state has capacity/interference limits, so hybrid stacks often keep some full/sliding-window attention layers.

4. **System-level sparse serving**
   - Turns sparse access into real HBM relief using hierarchical KV storage.
   - Full KV may live in CPU/SSD, while GPU HBM keeps only the active working set.
   - Examples: Spin, LServe.
   - Caveat: indexing, metadata, irregular fetch, and PCIe transfers can erase theoretical sparse gains.

5. **Token-axis compressed KV / compressed-history attention**
   - Compresses groups of past tokens into fewer KV/cache entries before or as they enter the long-context cache.
   - Distinct from MLA-style latent caching: MLA makes each token's cached representation narrower, while token-axis compression makes the cached sequence shorter.
   - Examples and terms from DeepSeek V4 reporting: CSA (Compressed Sparse Attention), HCA (Heavily Compressed Attention), often paired with SWA/local branches for recent exact tokens.
   - Effect: can reduce both stored cache entries and attention over distant history; actual serving gains depend on the engine's multi-cache policy for CSA/HCA/SWA and prefix reuse.
   - Caveat: treat reported numbers (e.g. 1M-context FLOPs/KV-cache reductions) as source-specific claims unless independently reproduced; state this boundary in talks.

6. **Quantization / KV cache compression**
   - Reduces the bytes per KV cache entry, not the number of entries.
   - Examples: KIVI (2-bit asymmetric per-channel Key + per-token Value), KVQuant (per-channel Key + pre-RoPE + non-uniform + dense-and-sparse outliers), TurboQuant (vector quantization).
   - Effect: directly reduces memory footprint and bandwidth; does not change the attention mechanism or the number of tokens in cache.
   - Caveat: "asymmetric quantization" in KIVI/KVQuant refers to different quantization dimensions for Key vs Value, not merely the presence of a zero-point. See `references/kv-cache-quantization-asymmetric.md` for defense wording.

## Recommended slide structure

When updating a PPT section, prefer 3 main slides + 1 backup, or replace the overview slide with a focused DeepSeek V4 CSA/HCA slide when the user asks specifically about DeepSeek V4:

- Slide A: "Sparse attention is not one thing" — five-mechanism taxonomy, including token-axis compressed KV.
- Slide B: "Top-k/page sparse attention: O(T²) to O(Tk)" — explain constant-budget query-key edges.
- Slide C: "DeepSeek V4 CSA/HCA: cache is shorter, not just narrower" — contrast MLA per-token latent compression with token-axis history compression.
- Slide D: "GDN: fixed recurrent state instead of explicit KV" — explain why GDN is not top-k sparse attention.
- Backup: compare sources of linear/near-linear behavior: fixed-budget sparse access, native/compressed sparse attention, token-axis compressed KV, recurrent state, hierarchical serving.

## Defense wording

Use this center sentence:

> Sparse attention reduces long-context cost through different mechanisms. Top-k/page methods reduce per-step KV access and attention compute; learned constant-budget methods make the number of query-key edges `O(Tk)`; DeepSeek V4-style CSA/HCA compresses the token axis so distant history becomes fewer cache entries; GDN-style linear attention replaces per-token KV with a fixed recurrent state; and sparse serving systems convert reduced access into GPU HBM savings. These mechanisms all reduce pressure, but they are not equivalent to deleting the full KV Cache.

For DeepSeek V4-specific questions, use this compact answer:

> MLA makes each token's KV state narrower, but DeepSeek V4's CSA/HCA-style compressed attention is described as making the history sequence shorter: groups of previous tokens become fewer compressed KV entries, while local/SWA branches preserve recent exact detail. That directly attacks the `T` term in the KV cache formula, but published FLOPs/KV-cache reduction numbers should be presented as reported-source claims unless reproduced.

## Pitfalls

- Do not say "sparse attention reduces KV Cache" without specifying whether it reduces storage, access bandwidth, or compute.
- Do not call GDN ordinary sparse attention; frame it as linear/recurrent-state attention.
- Do not present DeepSeek V4 CSA/HCA as merely another top-k/page sparse read method; its key distinction is token-axis/history compression that shortens cached entries, typically alongside local exact attention.
- Do not cite DeepSeek V4 efficiency percentages as your own measured results unless you actually reproduced them; phrase as "reported by the technical report / public sources" when used in slides.
- Do not claim linear complexity unless the budget `k` is constant, the compressed history length is bounded/controlled by the architecture, or the recurrent state size is independent of `T`.
- Always mention the system caveat: sparse selection or compressed history only becomes GPU memory relief when paired with storage/layout/prefix-cache support.
- Do not confuse "asymmetric quantization" in KIVI/KVQuant with the generic zero-point definition. In this context, "asymmetric" specifically means **Key and Value caches use different quantization dimensions** (Key per-channel, Value per-token), not merely that the quantizer has a zero-point. When asked, explain the distribution-driven rationale: Key has channel-wise outliers so per-channel confines error; Value has no channel outliers but attention sparsity means per-token confines error to unimportant tokens.