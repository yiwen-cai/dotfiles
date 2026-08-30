# Reasoning-model KV Cache Compression Notes

Use this reference when preparing LLM systems talks on KV Cache optimization, especially recent work targeting long-output reasoning models.

## LongFlow positioning

LongFlow should be introduced as a **decode-time, reasoning-aware KV Cache compression** method, not as another prompt-side long-input compression method.

Core contrast:

| Family | Typical workload | Compression timing | Representative methods |
|---|---|---|---|
| Long-input compression | long input, short output | prefill / prompt KV | SnapKV, PyramidKV, DapQ, ChunkKV |
| Reasoning-output compression | moderate/long input, long CoT output | decode-time generated-token KV | LongFlow |

Use this framing in survey narratives:

> The bottleneck shifts from "large prompt KV" to "continuously growing generated-token KV" in reasoning models.

## LongFlow core mechanism

Paper: **LongFlow: Efficient KV Cache Compression for Reasoning Models** (arXiv:2603.11504, 2026).

Main idea:

- Use only the current query `q_t` to estimate historical-token importance (**zero-history estimation**).
- Reuse an intermediate attention contribution already produced during attention computation (**zero-cost estimation**).
- Fuse FlashAttention, importance estimation, and token eviction into a custom Triton kernel.

Attention output:

```text
o_t = sum_i alpha_t^i v_i
```

Importance score:

```text
LongFlowScore(i) = || alpha_t^i v_i ||_1
```

Interpretation:

- `alpha_t^i`: current attention weight for token `i`.
- `v_i`: value vector for token `i`.
- `alpha_t^i v_i`: token `i`'s contribution vector to current attention output.
- Lower score means lower approximate contribution, so the token is a better eviction candidate.

Explain the approximation chain:

1. Ideal eviction objective: remove the token that minimally changes future output/logits.
2. Approximate future next-step impact with current-step impact because adjacent decode queries are empirically similar: `q_t ≈ q_{t+1}`.
3. Approximate attention output change from deleting token `i` by the token's contribution vector, ignoring softmax denominator re-normalization for efficiency.

## System point to highlight

LongFlow is not just an eviction score. Its reported speedups rely on system-level implementation:

- Static KV cache to avoid dynamic allocation and fragmentation.
- Fused Triton kernel integrating:
  - FlashAttention,
  - LongFlowScore computation,
  - token eviction.

Reported numbers from the paper:

- Attention module latency example: roughly `47 ms -> 8 ms` on Qwen3-8B, batch size 128, sequence length 3200, evicting one token after each attention computation.
- Up to `11.8x` throughput improvement with `80%` KV Cache compression and limited accuracy degradation.

Use these as paper-reported results, not independently verified production claims.

## Advantages

- Targets reasoning models with long generated outputs, where decode-stage KV growth dominates.
- Avoids historical attention/query buffers and auxiliary metadata.
- Considers value contribution, not just attention weight.
- System-aware: designed to preserve/fuse with modern attention kernels rather than adding a separate expensive importance pass.
- Provides actual latency/throughput-oriented experiments, unlike some quantization papers that mainly report quality and compression ratio.

## Limitations and caveats

Always mention these in an academic talk:

- Relies on adjacent-query similarity; abrupt generation-state shifts may weaken the approximation.
- Ignores softmax denominator changes when approximating deletion impact; large-attention-mass tokens may violate this approximation.
- Eviction is lossy and may remove reasoning steps that become useful later for verification or backtracking.
- System gains depend on the custom fused Triton kernel; a naive implementation of the score may not reproduce reported throughput.
- Best fit is long-output/decode-time reasoning workloads, not necessarily all long-context tasks.

## Suggested slide structure

Title: `LongFlow: Reasoning-aware Decode-time KV Compression`

Left: workload shift

```text
Traditional: long input -> short output
Reasoning: input -> long CoT / long output
KV Cache grows during decode
```

Center: formula

```text
o_t = sum_i alpha_t^i v_i
LongFlowScore(i) = ||alpha_t^i v_i||_1
```

Right: fused system path

```text
FlashAttention + importance estimation + token eviction
                  -> Fused Triton Kernel
```

Bottom takeaway:

> LongFlow moves KV compression from prompt-side long-input compression to decode-time long-output compression for reasoning models.
