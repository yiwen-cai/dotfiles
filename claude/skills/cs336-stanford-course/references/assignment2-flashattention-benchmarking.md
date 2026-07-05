# Assignment 2 FlashAttention Benchmarking Workflow

Use this reference after `flash_forward` and `flash_backward` tests pass and the user reaches `Problem (flash_benchmarking)`.

## Assignment Requirements

Benchmark with `triton.testing.do_bench` and compare:

- regular PyTorch attention (not FlashAttention)
- the user's Triton `FlashAttention.apply(q, k, v, True)` implementation

Report latencies for:

- forward only
- backward only, if separated cleanly
- end-to-end forward + backward

Required sweep:

- `batch_size = 1`
- `is_causal = True`
- `seq_len`: powers of 2 from `128` up to `65536`
- `d`: powers of 2 from `16` up to `128`
- dtype: `torch.bfloat16` and `torch.float32`

Prefer A800 selection unless the current CS336 environment has already validated the Blackwell GPU for PyTorch/Triton:

```bash
cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems
export CUDA_VISIBLE_DEVICES=1
```

## Recommended Script Shape

Use a dedicated script such as `cs336_systems/flash_benchmark.py` or extend the existing assignment `cs336_systems/attention_benchmark.py`; do not mix this into the model-level `benchmark.py`.

When the user says their benchmark code is "on a800", do **not** ask them to paste it. Proactively inspect `/storage/caiyiwen/code/cs336/assignment/assignment2-systems` over SSH, search benchmark/flash-related Python files, read the likely script, and run a small smoke test. This is especially important when the user is iterating quickly and expects remote-file review.

Per configuration:

1. allocate `q`, `k`, `v` once with `requires_grad=True` and a fixed random `do`;
2. define regular attention with causal mask using the same `-1e6` masking convention as tests;
3. define FlashAttention as `FlashAttention.apply(q, k, v, True)`;
4. optionally run a forward correctness smoke for small configs only (e.g. `seq_len <= 2048`) to avoid OOM before benchmarking;
5. clone inputs per implementation with `x.detach().clone().requires_grad_(True)` so PyTorch and FlashAttention benchmarks use equal values but independent leaf tensors and gradients;
6. benchmark closures with `triton.testing.do_bench`;
7. inside each measured closure, clear `q.grad = k.grad = v.grad = None` before running;
8. catch OOMs and record status instead of stopping the whole sweep;
9. write CSV rows immediately or frequently, because the full sweep is long.

A minimal output schema:

```text
impl,seq_len,d_model,dtype,status,forward_ms,backward_ms,fwd_bwd_ms,error
```

If separating backward-only latency, compute it as `fwd_bwd_ms - forward_ms` only as an approximate derived metric unless the script carefully precomputes/reuses forward outputs without changing the measurement target. In the final writeup, explicitly label this as a derived/estimated backward latency.

After the full sweep, verify coverage before writing conclusions:

```python
import csv
from collections import Counter
rows = list(csv.DictReader(open("attention_benchmark_results.csv")))
print("rows", len(rows))
print("status", Counter(r["status"] for r in rows))
print("dtype", Counter(r["dtype"] for r in rows))
print("seq_len", Counter(r["seq_len"] for r in rows))
```

For the required grid, expect exactly `160` rows:

```text
2 impl × 10 seq_len × 4 d_model × 2 dtype = 160
```

Do not treat the benchmark as complete if it only has the 48-row fp32 medium sweep or 96-row fp32+bf16 medium sweep through `seq_len=4096`. The final required sequence-length set is `128..65536`.

## Smoke-Test Before Full Sweep

Before the full grid, run one tiny fp32 case:

- `batch=1`
- `seq_len=128`
- `d=64`
- `dtype=torch.float32`

This validates that `do_bench` can call both implementations and that gradients are cleared correctly. Then test the same tiny case with `torch.bfloat16` before starting the full sweep.

## Durable Pitfalls From Debugging

### PyTorch vs Triton broadcast syntax differs

In PyTorch forward with tensors shaped `(batch, q)`, broadcasting to `(batch, q, k_or_d)` requires a trailing dimension:

```python
m_new.unsqueeze(-1)      # or m_new[:, :, None]
alpha.unsqueeze(-1)      # or alpha[:, :, None]
l.unsqueeze(-1)          # or l[:, :, None]
```

Using `x[:, None]` on a 2D PyTorch tensor gives `(batch, 1, q)`, which causes shape errors such as `64` vs `16` on dimension 2.

In Triton, row vectors such as `m_new`, `alpha`, and `l` are 1D `(Q_TILE_SIZE,)`, so the kernel should still use:

```python
m_new[:, None]
alpha[:, None]
l[:, None]
```

Do not global-replace one form with the other across PyTorch and Triton code.

### Regular attention einsum pitfall

For regular attention, after `p = softmax(scores, dim=-1)`, shapes are:

```python
p.shape == (batch, query, key)
v.shape == (batch, key, d)
```

The output contraction must reduce the key axis:

```python
einsum(p, v, "b q k, b k d -> b q d")
```

Do not write `"b q k, b q d -> b q d"`; it can silently appear to work when `query == key`, but it is semantically wrong.

### `run_one_config` parameter pitfall

After abstracting a single-config smoke into `run_one_config(batch_size, seq_len, d_model, dtype, device)`, do not leave a hard-coded line like:

```python
batch_size, seq_len, d_model = 1, 128, 64
```

inside the function. It makes later sweeps appear to run while all rows actually benchmark the same fixed shape. Verify printed rows show varying `seq_len` and `d_model` after adding the small grid.

### Leaf tensor cloning pattern

When comparing PyTorch attention and FlashAttention on equal inputs, clone per implementation as:

```python
x.detach().clone().requires_grad_(True)
```

`detach()` cuts old graph history, `clone()` avoids storage sharing, and `requires_grad_(True)` makes the clone a new leaf tensor with an independent `.grad`. This avoids benchmark contamination while preserving identical values.

### BF16 correctness smoke tolerance

Forward correctness smoke in the benchmark script is only a guard against obvious wiring errors, not a replacement for the official tests. For bf16, `rtol=1e-2, atol=1e-2` can be too strict; a single element can differ by about `0.01171875` and abort the whole sweep. Use dtype-dependent tolerance, for example:

```python
if dtype == torch.bfloat16:
    rtol, atol = 2e-2, 2e-2
else:
    rtol, atol = 1e-2, 1e-2
```

Wrap this smoke check in `try/except AssertionError` and print a warning instead of stopping the benchmark. Official correctness should come from `tests/test_attention.py`; the benchmark should still record timings for all configurations.

### Summary/writeup pattern

After generating `attention_benchmark_results.csv`, create a concise `summary.md` rather than pasting all rows. Include:

- setup table: batch=1, causal=True, seq_len set, d set, dtype set, GPU used;
- coverage check: 160 rows and all `status=ok` (or list OOM/error rows);
- representative tables for one fp32 configuration and one bf16 configuration;
- speedups computed as `pytorch_ms / flash_ms` for forward, estimated backward, and fwd+bwd;
- a caveat that this assignment implementation may use a Triton forward kernel with a PyTorch fallback backward, so short-sequence end-to-end results can favor PyTorch while long-sequence results show the expected FlashAttention scaling advantage.

### Chinese wiki summary sync pattern

When the user asks to sync benchmark summaries into the local wiki, use the local wiki root `/Users/yiwencai/wiki` if present (do not assume the older ai-daily-briefing path). For CS336 benchmark summaries, write query notes under:

```text
/Users/yiwencai/wiki/queries/
```

Use stable note names:

```text
cs336-attention-benchmark-summary.md
cs336-model-benchmark-summary.md
```

Add YAML frontmatter with `type: query`, `tags: [cs336, benchmark, ...]`, source CSV/summary paths, and `confidence: high`. Then update `/Users/yiwencai/wiki/concepts/cs336-language-modeling.md` under `## 相关页面` with wikilinks to the new notes. Verify by reading the first lines of both new notes and the updated index section.


## Interpretation Notes

Because the assignment backward may be implemented with `torch.compile` over a PyTorch helper rather than a Triton backward kernel, forward can be much faster while forward+backward may not beat regular PyTorch attention. Explain this distinction in the writeup rather than treating it as a failed FlashAttention forward kernel.
