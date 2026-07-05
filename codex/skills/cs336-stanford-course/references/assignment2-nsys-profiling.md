# Assignment 2 Nsight Systems Profiling Workflow

## Scope

Use this reference for CS336 Assignment 2 section 2.1.4 profiling on `a800`. It records the validated workflow for producing `.nsys-rep` traces, exporting CSV summaries, distinguishing forward/backward/optimizer in the timeline, and comparing attention softmax against attention matmuls.

## Remote Setup

Work in:

```bash
export PATH=/storage/caiyiwen/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems
```

Commands shown to the user assume they are already inside the remote shell. Agent tool execution still uses `ssh a800`.

## Minimal Phase NVTX Instrumentation

If Nsight Systems timeline does not clearly separate forward, backward, and optimizer work, add a minimal context manager in `cs336_systems/benchmark.py`:

```python
from contextlib import contextmanager

@contextmanager
def nvtx_range(name: str):
    torch.cuda.nvtx.range_push(name)
    try:
        yield
    finally:
        torch.cuda.nvtx.range_pop()
```

Wrap only the measured sections, not the warmup loop:

```python
with nvtx_range("forward"):
    logits = model(inputs)
    torch.cuda.synchronize()

with nvtx_range("backward"):
    loss.backward()
    torch.cuda.synchronize()

with nvtx_range("optimizer"):
    optimizer.step()
    torch.cuda.synchronize()
```

Verify with `nsys stats` that `:forward`, `:backward`, and `:optimizer` appear in `*_stats_nvtx_sum.csv` before asking the user to interpret the GUI.

## Formal Matrix Pattern

For a small first-pass matrix, run one fixed model size across three context lengths and three modes:

```text
context_length = 256, 512, 1024
mode = forward, backward, train
```

Validated profiling command shape:

```bash
mkdir -p traces/formal
nsys profile \
  --force-overwrite=true \
  --trace=cuda,nvtx,osrt \
  --cuda-memory-usage=true \
  --output=traces/formal/train_ctx1024 \
  uv run python cs336_systems/benchmark.py \
    --batch-size 1 \
    --context-length 1024 \
    --num-layers 2 \
    --d-model 128 \
    --num-heads 4 \
    --d-ff 512 \
    --warmup-steps 1 \
    --measure-steps 3 \
    --mode train
```

Export CSV summaries:

```bash
nsys stats traces/formal/train_ctx1024.nsys-rep \
  --force-export=true \
  --format csv \
  --output traces/formal/train_ctx1024_stats
```

Most useful files:

```text
*_stats_cuda_gpu_kern_sum.csv
*_stats_cuda_api_sum.csv
*_stats_nvtx_sum.csv
```

## Validated First Matrix Results

For `batch_size=1`, `num_layers=2`, `d_model=128`, `num_heads=4`, `d_ff=512`, `measure_steps=3`:

| mode | ctx=256 | ctx=512 | ctx=1024 |
|---|---:|---:|---:|
| forward kernel total | 2.346 ms | 3.126 ms | 5.276 ms |
| backward kernel total | 8.312 ms | 11.894 ms | 20.906 ms |
| train kernel total | 11.568 ms | 15.157 ms | 24.193 ms |

Kernel calls:

| mode | ctx=256 | ctx=512 | ctx=1024 |
|---|---:|---:|---:|
| forward | 450 | 450 | 442 |
| backward | 1506 | 1506 | 1498 |
| train | 2850 | 2850 | 2842 |

`ctx=1024` top forward kernel was `ampere_sgemm_128x128_nn`, invoked 8 times, taking about 29.6% of forward kernel time. Explain clearly that the `128x128` in this kernel name is the cuBLAS tile/kernel shape, not the sequence length; larger context increases the problem size and runtime while the kernel template name may remain unchanged.

## Attention Softmax vs Matmul

To answer section 2.1.4(e), add a profiling-only monkeypatch in `benchmark.py` rather than editing core `model.py`:

```python
import cs336_basics.model as model_module
from cs336_basics.nn_utils import softmax
from einops import einsum


def annotated_scaled_dot_product_attention(Q, K, V, mask=None):
    d_k = K.shape[-1]
    with nvtx_range("attention_scores_matmul"):
        attention_scores = einsum(
            Q, K, "... query d_k, ... key d_k -> ... query key"
        ) / math.sqrt(d_k)

    with nvtx_range("attention_mask"):
        if mask is not None:
            attention_scores = torch.where(mask, attention_scores, float("-inf"))

    with nvtx_range("attention_softmax"):
        attention_weights = softmax(attention_scores, dim=-1)

    with nvtx_range("attention_output_matmul"):
        return einsum(attention_weights, V, "... query key, ... key d_v ->  ... query d_v")


def main():
    args = parse_args()
    model_module.scaled_dot_product_attention = annotated_scaled_dot_product_attention
    ...
```

Validated `ctx=1024`, forward-only NVTX averages from one run:

| range | avg time |
|---|---:|
| attention_softmax | 2.951 ms |
| attention_scores_matmul | 1.225 ms |
| attention_output_matmul | 0.092 ms |
| attention_mask | 2.748 ms |

Use this to explain that FLOPs alone do not determine runtime: softmax and mask are memory/reduction/elementwise dominated, while the matmuls use optimized GEMM kernels.

## Draft Answer Pattern for 2.1.4

- (a) Report forward total time from `cuda_gpu_kern_sum.csv` and compare trend to Python timing; note that Python timing includes synchronization/runtime overhead while kernel summary counts GPU kernels only.
- (b) Name the top forward kernel and call count; compare with forward+backward where GEMM remains important but elementwise/reduction kernels increase.
- (c) Mention non-matmul kernels: elementwise, vectorized elementwise, softmax/reduction, mask/copy/fill kernels.
- (d) Compare forward-only with train: complete training has many more kernels and a larger fraction of non-matmul optimizer/backward work.
- (e) Use attention NVTX ranges to compare softmax and matmul runtime, then explain the mismatch with FLOP counts.

## Pitfalls

- Remote bare `python` may be old; prefer `python3` for CSV scripts and `uv run python` for project dependencies such as PyMuPDF.
- Nested SSH heredocs and f-strings can break on quotes. Prefer simple `.format(...)`, `chr(34)` for generated quotes, or write a small script instead of complex one-liners.
- `nsys stats` creates many empty graphics/API summaries; ignore empty OpenGL/Vulkan/DX files for this CUDA workload.
- `ampere_sgemm_128x128_*` names encode kernel tile/layout choices (`nn`, `nt`, `tn`), not user-level context length.
