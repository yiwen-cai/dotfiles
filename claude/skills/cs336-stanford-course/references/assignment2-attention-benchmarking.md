# Assignment 2 PyTorch Attention and Torch Compile Benchmarking

## Scope

Use for Section 4 `pytorch_attention` and `torch_compile` attention benchmarking before implementing FlashAttention kernels.

## Benchmark Script Pattern

Create an independent script such as `cs336_systems/attention_benchmark.py` rather than mixing benchmark-only logic into graded FlashAttention adapters. Use the existing naive scaled dot-product attention shape convention with no head dimension:

```python
scores = einsum(q, k, "b q d, b k d -> b q k") / math.sqrt(k.shape[-1])
probs = torch.softmax(scores, dim=-1)
out = einsum(probs, v, "b q k, b k d -> b q d")
```

CLI fields that worked well:

- `--output traces/attention/pytorch_attention.csv`
- `--repeats 100`
- `--warmup 5`
- `--compiled` to wrap the attention function with `torch.compile`

Always run on an A800 explicitly, e.g. `CUDA_VISIBLE_DEVICES=1`, and call `torch.cuda.synchronize()` after each forward/backward timing segment.

## Matrix

For `Problem (pytorch_attention)`, use:

- `batch_size = 8`
- `d_model in [16, 32, 64, 128]`
- `seq_len in [256, 1024, 4096, 8192, 16384]`
- random `q, k, v` tensors with `requires_grad=True`
- one random `grad` tensor for backward timing

Record at least:

- status (`ok` / `oom`)
- average forward ms
- average backward ms
- memory allocated before backward
- peak allocated GiB

## 2026-06-17 a800 Observations

Using A800 (`CUDA_VISIBLE_DEVICES=1`) and the repo's naive PyTorch attention, all required configurations fit. Peak memory was dominated by `B x S x S` tensors and scaled roughly with `seq_len^2`; `d_model` had a much smaller effect. For `B=8`, one fp32 `B x S x S` tensor is:

- `S=8192`: about `2.00 GiB`
- `S=16384`: about `8.00 GiB`

The largest vanilla run (`d=128`, `S=16384`) used about `32.391 GiB` peak allocated.

With `torch.compile` on the attention function, small sizes can be slower because launch/compile overhead dominates. Larger sizes showed modest backward speedups around `1.1x-1.2x`, and peak allocated memory was roughly halved for large sequences (for example `d=128`, `S=16384`: `32.391 GiB -> 16.391 GiB`). Present this as compiler fusion/recomputation reducing intermediates, not as algorithmically equivalent to FlashAttention.

## Reporting Guidance

For the writeup, include the full CSV/table or a compact table plus the CSV path. Highlight:

1. No OOM on A800 for the required matrix, but memory growth is clearly quadratic in sequence length.
2. The saved attention score/probability tensors dominate memory, not the `q/k/v` tensors.
3. Eliminating the cost requires a tiled/fused attention algorithm such as FlashAttention that avoids materializing the full `S x S` matrix.
4. `torch.compile` improves memory and often backward time, but it is not a substitute for the assignment's FlashAttention kernel implementation.
