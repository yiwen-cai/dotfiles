# Assignment 2 Torch Compile and Attention Benchmarking

## Scope

Use for CS336 Assignment 2 Section 4 problems:

- `pytorch_attention`: naïve PyTorch attention timing/memory benchmark.
- `torch_compile`: compare compiled vs uncompiled attention and full Transformer benchmark.

## A800 GPU Selection

On `a800`, explicitly choose an A800 with:

```bash
export CUDA_VISIBLE_DEVICES=1
```

or `2`. Avoid default GPU 0 when it is RTX PRO 6000 Blackwell unless the PyTorch build supports `sm_120`.

## Naïve Attention Benchmark Script Pattern

Use an isolated script (e.g. `cs336_systems/attention_benchmark.py`) that:

1. Fixes `batch_size=8` and removes the head dimension (`q/k/v` shape `[B, S, D]`).
2. Iterates `D in [16, 32, 64, 128]` and `S in [256, 1024, 4096, 8192, 16384]`.
3. Warms up, then times 100 synchronized forward passes and 100 synchronized backward passes.
4. Records `torch.cuda.memory_allocated()` after forward/before backward and `torch.cuda.max_memory_allocated()`.
5. Writes CSVs under `traces/attention/`.

For the compiled variant, wrap the attention function with `torch.compile(attention)` and reuse the same matrix.

## Validated A800 Results

On 2026-06-17 using A800 (`CUDA_VISIBLE_DEVICES=1`), all naïve attention matrix entries ran without OOM. Largest naïve case `B=8, S=16384, D=128` reached ~32.391 GiB peak allocated; compiled reduced that to ~16.391 GiB.

Observed compile trends:

- Small shapes (`S=256`) can be slower after compile due to overhead.
- Large shapes generally improve backward by ~1.1x–1.2x.
- Peak allocated memory is roughly halved for large `S`, suggesting compiler fusion/recomputation reduces saved intermediate pressure, but this is not a substitute for FlashAttention's algorithmic avoidance of full `S×S` materialization.

Memory accounting for `B=8`, fp32 attention-score-like tensors:

```text
one B×S×S tensor = 8 * S * S * 4 bytes
S=8192  -> ~2 GiB per tensor; scores + probabilities ~= 4 GiB
S=16384 -> ~8 GiB per tensor; scores + probabilities ~= 16 GiB
```

## Full Transformer `torch.compile` Benchmark

Add a flag to `benchmark.py`:

```python
parser.add_argument("--compile-model", action="store_true")
...
if args.compile_model:
    model = torch.compile(model)
```

Validated small-model config:

```bash
CUDA_VISIBLE_DEVICES=1 uv run python cs336_systems/benchmark.py \
  --batch-size 4 --context-length 512 \
  --num-layers 12 --d-model 768 --num-heads 12 --d-ff 3072 \
  --warmup-steps 5 --measure-steps 10 --mode train --compile-model
```

Measured on A800:

| mode | vanilla total | compiled total | speedup |
|---|---:|---:|---:|
| forward | 43.641 ms | 38.164 ms | 1.14x |
| backward | 134.804 ms | 116.397 ms | 1.16x |
| train | 152.471 ms | 128.047 ms | 1.19x |

Logs were saved under `traces/compile_model/vanilla_*.log`, `traces/compile_model/compiled_*.log`, and `traces/compile_model/model_compile_comparison.csv`.

## Chinese Summary Notes

When asked to summarize the earlier attention/model benchmarks in Chinese, produce two separate notes instead of one mixed summary:

1. `attention_benchmark_summary_zh.md` for the FlashAttention-vs-PyTorch causal attention benchmark, sourced from `attention_benchmark_results.csv`.
2. `model_benchmark_summary_zh.md` for the earlier `torch.compile` attention/model experiments, sourced from `traces/attention/attention_compile_comparison.csv` and `traces/compile_model/model_compile_comparison.csv`.

If syncing to the local wiki, copy them to `/Users/yiwencai/wiki/queries/cs336-attention-benchmark-summary.md` and `/Users/yiwencai/wiki/queries/cs336-model-benchmark-summary.md`, then update `/Users/yiwencai/wiki/concepts/cs336-language-modeling.md` with wikilinks. Keep summaries in Chinese, include source files, coverage checks, representative tables, and concise interpretation.

## Pitfalls

- Remote zsh treats `status` as a read-only variable and can parse bare `echo === ... ===` unexpectedly; use neutral variable names like `state` and `printf` in SSH one-liners.
- SSH heredocs with nested quotes can corrupt Python f-strings; use temporary script files or `.format()` in generated Python snippets.
- `torch.compile` may warn about TF32 not being enabled; mention this as a possible additional speed knob rather than changing it mid-comparison unless the experiment explicitly asks for it.
