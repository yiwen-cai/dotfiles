# Assignment 2 FlashAttention Preparation Workflow

Use this reference when the user reaches Assignment 2 Section 4 (`GPU Kernels`, `pytorch_attention`, `torch_compile`, `flash_forward`, `flash_backward`).

## GPU Selection on `a800`

Before running CUDA benchmarks, query `nvidia-smi -L` and pin to an A800 explicitly. The machine may expose a newer Blackwell GPU as index 0, while the CS336 PyTorch build may not support its compute capability. For current Assignment 2 benchmarks, prefer:

```bash
export CUDA_VISIBLE_DEVICES=1
```

or another visible A800 index. Do not assume GPU 0 is an A800.

## PyTorch Attention Benchmark

For `Problem (pytorch_attention)`, use a standalone benchmark script rather than mixing this into the graded FlashAttention implementation. The matrix required by the handout is:

- `batch_size = 8`
- no multi-head dimension
- `d_model in [16, 32, 64, 128]`
- `seq_len in [256, 1024, 4096, 8192, 16384]`
- 100 timed forward passes and 100 timed backward passes, with warmup and `torch.cuda.synchronize()` after each measured forward/backward
- record memory allocated before backward and peak allocated memory

A minimal useful output schema is:

```text
batch_size,seq_len,d_model,compiled,status,forward_ms,backward_ms,memory_before_backward_gib,peak_allocated_gib,error
```

For the user's a800 A800 run, all listed PyTorch attention configurations fit. The observed pattern is that memory is dominated by `B x S x S` attention matrices and grows approximately with `seq_len^2`; `d_model` changes runtime but barely changes the dominant memory term.

## Torch Compile Attention Comparison

Add `--compiled` to the attention benchmark and wrap the attention function with `torch.compile(attention)`. Compare the same grid against the uncompiled CSV and compute speedups.

Observed pattern from the a800 A800 run:

- very small shapes such as `seq_len=256` can be slower after compile because overhead/fusion benefits are too small;
- medium/large shapes show steadier backward speedup, often around `1.1x–1.2x`;
- peak allocated memory can drop by about half for long sequences because Inductor reduces/fuses some intermediate materialization, but this is still not algorithmically equivalent to FlashAttention.

## Torch Compile Whole Transformer

For `Problem (torch_compile)` part (b), add a surgical flag to `cs336_systems/benchmark.py`:

```python
parser.add_argument("--compile-model", action="store_true")
...
if args.compile_model:
    model = torch.compile(model)
```

Create the optimizer after the model is optionally compiled so the measured configuration only differs by compile state. Run the same model configuration, warmup, and measure steps for vanilla and compiled modes, and compare `forward`, `backward`, `optim`, plus total step time.

A validated small-model command shape:

```bash
cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems
export PATH=/storage/caiyiwen/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
export CUDA_VISIBLE_DEVICES=1
for mode in forward backward train; do
  uv run python cs336_systems/benchmark.py \
    --batch-size 4 \
    --context-length 512 \
    --num-layers 12 \
    --d-model 768 \
    --num-heads 12 \
    --d-ff 3072 \
    --warmup-steps 5 \
    --measure-steps 10 \
    --mode "$mode"
done
```

Then repeat with `--compile-model`. On the a800 A800 small-model run, whole-model compile gave stable but modest speedups: roughly `1.14x` forward, `1.16x` forward+backward, and `1.19x` full train step.

## FlashAttention Paper Note for Implementation Prep

The user downloaded the FlashAttention paper locally at:

```text
/Users/yiwencai/Documents/code/cs336/papers/FlashAttention.pdf
```

A Chinese HTML explanation focused on Triton implementation was generated at:

```text
/Users/yiwencai/Documents/code/cs336/paper_notes/flashattention/index.html
```

When preparing `flash_forward`, direct the user first to the sections on:

1. online softmax (`m`, `l`, `acc` updates),
2. mapping paper tiles to Triton `program_id`,
3. causal masking by global query/key indices,
4. saving `LSE = m + log(l)` for backward.

## PyTorch FlashAttention Forward Implementation (Step-by-Step)

Assignment 2 `flash_forward` requires a `torch.autograd.Function` subclass that implements FlashAttention-2 forward using only PyTorch ops (no Triton). The test (`test_flash_forward_pass_pytorch`) calls the function returned by `get_flashattention_autograd_function_pytorch()`.

### File Structure

```
cs336_systems/flashattention.py          # implementation
cs336_systems/__init__.py                # export FlashAttentionPytorch
tests/adapters.py                        # return cs336_systems.flashattention.FlashAttentionPytorch
```

### Function Signature

```python
class FlashAttentionPytorch(torch.autograd.Function):
    @staticmethod
    def forward(ctx, q, k, v, is_causal=False):
        ...
        ctx.save_for_backward(q, k, v, O, L)
        ctx.is_causal = is_causal
        return O
```

### Algorithm Skeleton (Online Softmax Tiling)

```python
B_q = 16
B_k = 16
batch, n_q, d = q.shape[0], q.shape[-2], q.shape[-1]
n_k = k.shape[-2]

O = torch.zeros_like(q)          # (batch, n_q, d)
L = torch.zeros(batch, n_q, device=q.device, dtype=q.dtype)

for q_start in range(0, n_q, B_q):
    q_end = min(q_start + B_q, n_q)
    q_tile = q[:, q_start:q_end, :]      # actual length may be < B_q at boundary
    q_tile_len = q_end - q_start

    # per-query-tile state (must use actual tile length, not fixed B_q)
    m = torch.full([batch, q_tile_len], float("-inf"), device=q.device, dtype=q.dtype)
    l = torch.zeros([batch, q_tile_len], device=q.device, dtype=q.dtype)
    o = torch.zeros([batch, q_tile_len, d], device=q.device, dtype=q.dtype)

    for k_start in range(0, n_k, B_k):
        k_end = min(k_start + B_k, n_k)
        k_tile = k[:, k_start:k_end, :]
        v_tile = v[:, k_start:k_end, :]

        scores = einsum(q_tile, k_tile, "b q d, b k d -> b q k") / (d**0.5)
        m_new = torch.maximum(m, scores.max(dim=-1).values)
        alpha = torch.exp(m - m_new)
        p_tilde = torch.exp(scores - m_new.unsqueeze(-1))

        l = alpha * l + p_tilde.sum(dim=-1)      # NOT einsum(l, alpha, ...)
        pv = einsum(p_tilde, v_tile, "b q k, b k d -> b q d")
        o = o * alpha.unsqueeze(-1) + pv
        m = m_new

    o = o / l.unsqueeze(-1)
    L_tile = torch.log(l) + m
    O[:, q_start:q_end, :] = o
    L[:, q_start:q_end] = L_tile
```

### Critical Correctness Points

| Issue | Why it matters | Fix |
|-------|---------------|-----|
| `m,l,o` shape uses fixed `B_q` | Last tile may be shorter | Use `q_tile_len = q_end - q_start` |
| `m,l,o` on wrong device/dtype | Silent CPU tensor or dtype mismatch | Pass `device=q.device, dtype=q.dtype` |
| `ctx.save_for_backward` inside q loop | Only saves last tile, loses earlier state | Move **outside** the q loop |
| `l = einsum(l, alpha, ...)` | Unnecessary and confusing | Use `alpha * l` (element-wise) |
| Forgetting `o = o * alpha + pv` | Old output not rescaled when m changes | Both `l` and `o` must be scaled by `alpha` |
| `o` divided inside k loop | Each tile would have wrong local softmax | Divide **after** all k tiles processed |

### State Scope FAQ (Common User Questions)

**Q: Why are `m, l, o` initialized outside the k loop but inside the q loop?**
A: Each query tile needs its own running max (`m`) and sum (`l`) across **all key tiles**. Query tiles are independent — `q1` and `q2` never share softmax state.

**Q: Is `o` inside the k loop the final output or unnormalized?**
A: It is **unnormalized** during the k loop. The division `o / l` happens only after all key tiles are processed. This is the core of online softmax: accumulate numerator and denominator separately, normalize once at the end.

**Q: Do query tiles update each other?**
A: **No.** Each query tile is completely independent. The only "global" structure is the output tensor `O` where each tile writes its result.

**Q: What does `scores.max(dim=-1).values` mean?**
A: For each query in the tile, find the maximum score across the current key tile. Shape: `(batch, q_tile_len)`.

**Q: `m_new[:, :, None]` vs `m_new.unsqueeze(-1)`?**
A: Identical. Both add a trailing dimension for broadcasting with `(batch, q_tile_len, B_k)` scores. Use `unsqueeze(-1)` for clarity.

### Test Expectations

- `get_flashattention_autograd_function_pytorch()` returns a **class** (not instance)
- The class is a `torch.autograd.Function` subclass
- `forward` returns only `O` (not `L`)
- `ctx.save_for_backward(...)` saves exactly one tensor of shape `(batch, n_q)` — the log-sum-exp `L`
- Test compares against naive `softmax(QK^T/sqrt(d)) @ V` with `rtol=1e-2, atol=1e-2`
- `is_causal=False` is tested first; causal masking can be added later

### Adapter Wiring

```python
# tests/adapters.py
import cs336_systems

def get_flashattention_autograd_function_pytorch() -> type:
    return cs336_systems.flashattention.FlashAttentionPytorch
```

And in `cs336_systems/__init__.py`:
```python
from .flashattention import FlashAttentionPytorch
```

## Implementation Pitfalls for FlashAttention Forward

- A `for` loop over K/V tiles inside one Triton program is serial for that program; parallelism comes from many programs over Q tiles and batch/head groups, while tile-internal `tl.dot` is parallelized by the hardware.
- When `m` changes, rescale both `l` and the old output accumulator `acc`; forgetting to rescale `acc` is a common correctness bug.
- Keep softmax statistics and accumulators in fp32 even if inputs are fp16/bf16.
- Apply causal masks using global row/column positions, not local tile indices alone.
- Store output and the per-row log-sum-exp/normalizer needed by backward; tests may inspect the saved tensor shape.
