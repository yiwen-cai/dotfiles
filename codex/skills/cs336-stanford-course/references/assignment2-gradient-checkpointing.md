# Assignment 2 Gradient Checkpointing (Section 3)

## Scope

CS336 Assignment 2 Section 3 `Problem (gradient_checkpointing)`: memory-optimal activation checkpointing and the single-level checkpointing experiment for the XL model.

## Section Naming Pitfall

The handout does **not** label this as `2.1.7`. After `2.1.6 Profiling Memory`, the PDF moves to:

- `3 Single-GPU Memory`
- `3.1 Autograd Residuals`
- `3.2 Activation Checkpointing`
- `3.2.1 Recomputation`
- `Problem (gradient_checkpointing)`

Refer to it as **Section 3 gradient checkpointing**, not `2.1.7`.

## Concept Summary

Activation checkpointing saves memory by storing only checkpoint boundary activations during forward. During backward, PyTorch reruns the checkpointed forward region to regenerate internal saved tensors, then performs normal backward through that region. It trades extra compute for lower long-lived activation memory.

Distinguish this from disk/model checkpoints (`torch.save(state_dict)`); this is activation/gradient checkpointing.

## Single-Level Checkpointing Reasoning for Part (b)

Be explicit about what `k` means in the implementation/report. Two common conventions invert the observed trend:

1. If `k` means **checkpoint interval / chunk length** (one checkpointed region contains `k` layers), larger `k` creates a larger recomputation window and can monotonically increase the measured peak for a PyTorch `checkpoint(run_group, x)` implementation, because no internal boundaries are stored inside the group. In the 2026-06-17 a800 run with XL (`batch=4`, `ctx=2048`), `k=1..7` increased from ~38.2 GiB to ~74.0 GiB allocated, and `k=8` OOM.
2. The textbook `O(N/k + k)` optimum near `sqrt(N)` applies when the memory model includes both saved checkpoint boundaries and a recomputation window of length `k` under a convention where boundary storage actually varies with `N/k` and those boundaries dominate enough to create the trade-off.

For this repo's minimal wrapper:

```python
checkpoint(run_group, x, use_reentrant=False)
```

where `run_group` spans `k` consecutive Transformer layers, report that the tested implementation's best measured peak is the smallest chunk length (`k=1`), and explain the naming/convention difference rather than forcing a `sqrt(32)` conclusion.

## a800 Measurement Record

For the 2026-06-17 a800 run, use A800 explicitly (for example `CUDA_VISIBLE_DEVICES=1`) because GPU 0 was a newer Blackwell card. The measured XL backward-step peaks for `batch=4`, `ctx=2048`, 32 layers, and chunk-length `k` were:

| k | peak allocated GiB | peak reserved GiB | status |
|---:|---:|---:|---|
| 1 | 38.2163 | 41.4648 | ok |
| 2 | 44.1781 | 47.4668 | ok |
| 3 | 50.1402 | 53.4668 | ok |
| 4 | 56.1031 | 59.4688 | ok |
| 5 | 62.0631 | 65.4688 | ok |
| 6 | 68.0231 | 71.4707 | ok |
| 7 | 73.9851 | 77.4707 | ok |
| 8 | OOM | OOM | failed |

Interpretation: for the current wrapper where `k` is the number of layers inside one checkpointed `run_group`, larger `k` means a larger recomputation window, so measured peak memory increases. The best measured chunk length is `k=1`; explain the convention mismatch if comparing against textbook `sqrt(N)` interval language.

## Minimal Benchmark Integration Pattern

Add a CLI flag:

```python
parser.add_argument("--checkpoint-block-size", type=int, default=0)
```

Wrap only the Transformer block stack for experiments; leave embeddings, final norm, and `lm_head` outside the checkpointed region:

```python
from torch.utils.checkpoint import checkpoint

if checkpoint_block_size > 0:
    layers = model.layers

    def run_checkpointed_layers(x):
        for start_idx in range(0, len(layers), checkpoint_block_size):
            group = layers[start_idx : start_idx + checkpoint_block_size]

            def run_group(y, group=group):
                for layer in group:
                    y = layer(y)
                return y

            x = checkpoint(run_group, x, use_reentrant=False)
        return x

    def checkpointed_forward(input_ids):
        x = model.token_embeddings(input_ids)
        x = run_checkpointed_layers(x)
        x = model.ln_final(x)
        return model.lm_head(x)
else:
    checkpointed_forward = model
```

Use `use_reentrant=False` for modern PyTorch checkpointing behavior.

## Experiment Commands

Run one measured backward step per block size and dump one memory snapshot:

```bash
export PATH=/storage/caiyiwen/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems
mkdir -p traces/checkpoint

for k in 4 6 8; do
  rm -f memory_snapshot.pickle
  uv run python cs336_systems/benchmark.py \
    --batch-size 4 \
    --context-length 2048 \
    --num-layers 32 \
    --d-model 2560 \
    --num-heads 32 \
    --d-ff 10240 \
    --warmup-steps 0 \
    --measure-steps 1 \
    --mode backward \
    --checkpoint-block-size "$k" \
    --memory-profile \
    2>&1 | tee "traces/checkpoint/checkpoint_k${k}.log"
  mv memory_snapshot.pickle "traces/checkpoint/checkpoint_k${k}.pickle"
done
```

Open each pickle in `https://pytorch.org/memory_viz`, read the peak memory from `Active Memory Timeline`, and compare the three peaks.

## A800 Measured Results for Part (b)

Validated on `a800` with `CUDA_VISIBLE_DEVICES=1` (A800), XL config (`batch=4`, `ctx=2048`, `layers=32`, `d_model=2560`, `heads=32`, `d_ff=10240`), one measured backward step, and the repo wrapper where `k` is layers per checkpointed group:

| k | peak allocated | peak reserved | status |
|---:|---:|---:|---|
| 1 | 38.2163 GiB | 41.4648 GiB | ok |
| 2 | 44.1781 GiB | 47.4668 GiB | ok |
| 3 | 50.1402 GiB | 53.4668 GiB | ok |
| 4 | 56.1031 GiB | 59.4688 GiB | ok |
| 5 | 62.0631 GiB | 65.4688 GiB | ok |
| 6 | 68.0231 GiB | 71.4707 GiB | ok |
| 7 | 73.9851 GiB | 77.4707 GiB | ok |
| 8 | OOM | OOM | failed |

Use `k=1` as the measured optimum for this implementation, and explain that larger groups create larger recomputation windows. Logs/snapshots were saved under `traces/checkpoint/a800_peak_k*.log` and `traces/checkpoint/a800_checkpoint_k*.pickle` in the remote assignment repo.

## Answer Template for Part (b)

Use a concise response:

- With one-level checkpointing, the peak memory is controlled by checkpoint boundary storage `O(N/k)` and recomputation-window activations `O(k)`.
- This predicts an optimum near `k = sqrt(32) ~= 6`, so I profiled `k = 4, 6, 8`.
- Report a table of measured peak memory from memory_viz.
- Conclude that the lowest measured peak validates or slightly adjusts the theoretical optimum, depending on implementation overheads and non-block memory such as embeddings, logits, gradients, and allocator caching.

## Pitfalls

- Do not call this problem `2.1.7`; the handout labels it as Section 3.
- Do not checkpoint the whole model including logits/head if the question is about Transformer block residuals; checkpoint the block stack to isolate the intended effect.
- Use one measured step for memory snapshots; multi-step recordings make timelines harder to interpret.
- If CUDA initialization fails in a remote session, do not record that as a durable CS336 fact; rerun when the GPU/PyTorch environment is healthy.
