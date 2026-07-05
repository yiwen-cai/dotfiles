# Assignment 2 Mixed Precision (2.1.5)

## Scope

CS336 Assignment 2 section 2.1.5 on `a800`: accumulation demo, dtype reasoning under autocast, BF16 benchmark integration, and comparison with FP32.

## Part 1 — Accumulation Demo

Run on a800 to reproduce:

```bash
cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems
uv run python - <<'PY'
import torch
print("FP32:", sum(torch.tensor(0.01, dtype=torch.float32) for _ in range(1000)).item())
print("FP16:", sum(torch.tensor(0.01, dtype=torch.float16) for _ in range(1000)).item())
PY
```

Validated results:
- FP32 accumulation: ~10.0001 (accurate)
- FP16 accumulation: ~9.953 (off by ~0.047 due to precision loss)
- FP16 addend → FP32 accumulator: ~10.002 (much better; accumulator precision matters the most)

## Part 2 — dtype Reasoning under autocast(FP16)

For `ToyModel(fc1 → ReLU → LayerNorm → fc2)`, dtypes are:

| Component | dtype | Reason |
|---|---|---|
| Model parameters | FP32 | autocast does not change parameter storage |
| fc1 output | FP16 | Linear → matmul is autocasted |
| LayerNorm output | FP32 | PyTorch excludes LayerNorm from autocast |
| Final logits | FP16 | fc2 is another matmul |
| Loss | FP32 | Loss is kept at high precision |
| Gradients | FP32 | Gradient accumulation needs FP32 |

LayerNorm is excluded because mean/variance statistics are numerically sensitive. BF16 (same exponent range as FP32) is less sensitive than FP16 but still has reduced mantissa (7 vs 23 bits), so PyTorch keeps LayerNorm in FP32 under either autocast dtype.

## Part 3 — Benchmark Integration

### Adding a dtype flag

```python
parser.add_argument(
    "--mix-precision", type=str,
    choices=["fp32", "bf16", "fp16"],
    default="fp32",
)

# In main():
if args.mix_precision == "fp16":
    dtype = torch.float16
elif args.mix_precision == "bf16":
    dtype = torch.bfloat16
else:
    dtype = torch.float32
```

Pass `dtype` to `run_model`. Inside `run_model`, wrap forward/backward:

```python
with torch.autocast(device_type="cuda", dtype=dtype):
    for _ in range(warmup_steps):
        ...
    for _ in range(measure_steps):
        ...
```

FP32 autocast is a no-op (`torch.autocast(dtype=torch.float32)` passes through without changes), so no separate `nullcontext` is needed.

### Validated Results

Small model (d_model=128, num_layers=2): No measurable speedup — small matmuls don't benefit from Tensor Cores, autocast dispatch overhead dominates.

Large model (d_model=768, batch=4, default params):

| Mode | FP32 | BF16 | Speedup |
|---|---:|---:|---:|
| forward | 43.8 ms | 14.0 ms | ~3× |
| backward | 92.0 ms | 33.2 ms | ~2.8× |

XL model (d_model=2560, num_layers=32, batch=1, ctx=1024):

| Mode | FP32 | BF16 | Speedup |
|---|---:|---:|---:|
| forward | 0.470 s | 0.093 s | ~5× |
| backward | ~1.01 s | 0.251 s | ~4× |

Trend: larger models → higher matmul fraction → larger BF16 speedup. Elementwise/reduction/optimizer kernels benefit less (memory bandwidth bound).

## Pitfalls

- `torch.autocast` does NOT cast model parameters; they remain in the original dtype. Only operations inside the context may use lower precision.
- For parameter-heavy models, the memory savings from BF16 are modest because parameters stay in FP32 unless manually cast.
- BF16 with d_model=128 models may appear slower than FP32 due to autocast dispatch overhead. Always test with realistic model sizes.
- LayerNorm, softmax, and loss computation stay in FP32 under autocast per PyTorch's default policy.
