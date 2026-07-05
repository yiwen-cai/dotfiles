# Assignment 2 Memory Profiling (2.1.6)

## Scope

CS336 Assignment 2 section 2.1.6 on `a800`: PyTorch memory profiler integration, pickle generation, memory_viz interpretation, and OOM handling for large models.

## Remote Setup

```bash
export PATH=/storage/caiyiwen/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems
```

## Adding a Memory Profile Flag

Use `action="store_true"` for a boolean flag:

```python
parser.add_argument("--memory-profile", action="store_true",
                    help="Enable PyTorch memory profiling")
```

## Recording a Single Step

Record only ONE measured step (not warmup, not all measured steps):

```python
def run_model(..., memory_profile: bool):
    # Warmup — do NOT record memory
    for _ in range(warmup_steps):
        ...

    test_memory = False
    for _ in range(measure_steps):
        if memory_profile and not test_memory:
            torch.cuda.memory._record_memory_history(max_entries=1000000)

        # Run the step
        logits = model(inputs)
        loss = cross_entropy(logits, targets)
        loss.backward()
        optimizer.step()

        if memory_profile and not test_memory:
            torch.cuda.memory._dump_snapshot("memory_snapshot.pickle")
            torch.cuda.memory._record_memory_history(enabled=None)
            test_memory = True
```

Move the pickle to a descriptive name after each run to avoid overwrites.

## Named Pickle Outputs

After each benchmark run, rename immediately:

```bash
uv run python cs336_systems/benchmark.py \
  --batch-size 1 --context-length 128 \
  --num-layers 32 --d-model 2560 --num-heads 32 --d-ff 10240 \
  --warmup-steps 1 --measure-steps 1 --mode forward --memory-profile
mv memory_snapshot.pickle traces/memory/xl_forward_ctx128.pickle
```

## Validated Results

XL model (d_model=2560, d_ff=10240, num_layers=32, num_heads=32, batch=1):

| Config | Pickle Size |
|---|---|
| FP32 forward ctx=128 | 1.1 MB |
| FP32 train ctx=128 | 4.1 MB |
| FP32 forward ctx=1024 | 1.1 MB |
| FP32 train ctx=1024 | 4.6 MB |
| BF16 forward ctx=1024 | 1.3 MB |
| BF16 train ctx=1024 | 4.8 MB |

ctx=2048 OOMs — XL model parameters (~3B FP32 ≈ 12 GB) plus attention intermediates (`32 heads × 2048² × 4 bytes = 512 MB` per layer) exceed 80 GB HBM. Use ctx=1024 as the practical maximum.

## Viewing Results

Upload pickle files to [pytorch.org/memory_viz](https://pytorch.org/memory_viz). Key panels:

- **Active Memory Timeline**: Shows allocated memory over time; peaks align with forward pass accumulation and backward gradient computation
- **Memory Events**: Per-allocation stack traces and sizes
- **Detail slider**: Filters allocations by size percentile (e.g., 10% = only top 10% largest allocations)

### Finding Detail, Module, and Stack Traces

The memory_viz UI can be visually sparse before a pickle is loaded. Load the local `.pickle` first, then use `Active Memory Timeline` and click allocations near the peak to reveal stack traces. If `Require click to show trace` is enabled, the trace appears only after clicking a specific allocation; if the trace is hard to find, uncheck it and reload the file.

A separate **Module** panel may not appear for course snapshots because `_dump_snapshot` may contain stack frames but no explicit module metadata. In that case, use Python frames in the stack trace as the module evidence: e.g. `cs336_basics/model.py:<line>` and `cs336_systems/benchmark.py:<line>`.

Common interpretation for Assignment 2 XL snapshots:

- Stack trace ending at `TransformerLM.forward -> self.lm_head(x) -> Linear.forward -> einsum/bmm` is the final logits projection, not attention. For `batch=1, ctx=1024, vocab=10000, fp32`, logits size is `1 × 1024 × 10000 × 4 = 40,960,000 bytes = 39.1 MiB`.
- Stack traces through attention score matmul/softmax indicate attention intermediates; these are the ones to cite for `O(seq_len^2)` context-length growth.
- For writeups, phrase this as “At Detail=10%, one large allocation is from `<module/function>`; the stack trace points to `<file:line>`, corresponding to `<tensor role>`.”

## Answer Template for 2.1.6

- (a) Timeline images show: forward pass grows memory as activations accumulate per layer; training step peaks during backward (activations + gradients coexist), then optimizer updates. Forward-only peaks are lower than training peaks.
- (b) Peak memory table (read from memory_viz timeline y-axis):

| context | forward peak | train peak |
|---|---:|---:|
| 128 | from memory_viz | from memory_viz |
| 1024 | from memory_viz | from memory_viz |

- (c) BF16 mixed precision modestly reduces peak memory (activations stored in 2 vs 4 bytes), but model parameters remain FP32, so total reduction is partial. The effect is more visible at larger context lengths where activations dominate.
- (d) Residual stream tensor: `batch × ctx × d_model × sizeof(FP32)` = `1 × 512 × 2560 × 4` = 5,242,880 bytes = **5 MiB**.
- (e) At Detail 10%, largest allocations are typically activation tensors from attention and MLP layers. Stack traces point to the model forward pass.
- (f) Forward pass saves residuals for backward; each TransformerBlock's saved tensors include attention intermediates (QK^T scores, softmax weights) and MLP activations. Backward frees these and allocates gradient tensors of similar size.

## Pitfalls

- `_record_memory_history()` without `max_entries` may overflow for large models. Always pass `max_entries=1000000`.
- Record only ONE measure step; multi-step recording merges warmup and measured allocations into a confusing timeline.
- FP32 XL model ctx=2048 OOMs regardless; BF16 also OOMs because attention `QK^T` intermediate is `heads × ctx² × sizeof(BF16)` = 256 MB per layer, which cumulatively exhausts memory. Use ctx=1024 or lower.
- Rename pickle files immediately after each run to avoid clobbering.
