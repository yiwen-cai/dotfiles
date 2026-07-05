---
name: cs336-stanford-course
description: Stanford CS336 course assignments and components — tokenizers, model architectures, training pipelines, and evaluation.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Stanford CS336: Language Modeling from Scratch

This skill covers the Stanford CS336 course assignments and components, including byte-level BPE tokenizers, model architecture components, training pipelines, and evaluation methodologies.

## When to Use

Trigger when the user:
- Mentions Stanford CS336 or related assignments
- Asks about BPE tokenizers, model components, or training pipelines from the course
- Needs help with course-specific code, debugging, or concepts
- References specific assignment weeks or components

## Working Style for This User

Use an assignment-first tutoring workflow for CS336. The user's priority is advancing the current assignment; do not schedule lectures in course order by default. Introduce lecture material only when the current assignment step needs it, and frame it as just-in-time background for the next implementation, debugging, profiling, or writeup task.

Preserve TA-style boundaries: guide, review, explain errors, suggest sanity checks and profiler checks, but do not write core graded implementations or complete TODOs.

**AGENTS.md / CLAUDE.md Check**: Before answering any project-specific question, check the project folder (local or remote) for `AGENTS.md` or `CLAUDE.md`. If present, read it and follow its constraints. For CS336 on `a800`, the file is at `/storage/caiyiwen/code/cs336/assignment/assignment2-systems/AGENTS.md`. This rule takes precedence over default behavior when there is a conflict.

## Knowledge Management Convention

**Knowledge management convention (per user preference)**: Save stable facts and routing indices in memory; save workflows, commands, and troubleshooting steps in this skill (SKILL.md or references/). Procedural depth does not belong in memory.

**CS336 Wiki Migration (2026-06-18)**: All CS336 notes, papers, lecture notes, assignment notes, and learning records (day plans/completions) are now managed in the wiki directory:
- `raw/cs336/` — Course papers, notes, assignments data, paper notes
- `study_archive/cs336/` — Lecture notes, assignment notes, FlashAttention explanation, README, study.py
- `queries/cs336-day*-plan.md` / `queries/cs336-day*-completion.md` — Learning records
- `concepts/cs336-language-modeling.md` — Course overview and navigation hub

When user asks about CS336, first orient by reading `concepts/cs336-language-modeling.md` and relevant `queries/` files.

**CS336 Wiki Migration**: All CS336 notes, papers, lecture notes, assignment notes, and learning records (day plans/completions) are now managed in the wiki directory:
- `raw/cs336/` — Course papers, notes, assignments data, paper notes
- `study_archive/cs336/` — Lecture notes, assignment notes, FlashAttention explanation, README, study.py
- `queries/cs336-day*-plan.md` / `queries/cs336-day*-completion.md` — Learning records
- `concepts/cs336-language-modeling.md` — Course overview and navigation hub

When user asks about CS336, first orient by reading `concepts/cs336-language-modeling.md` and relevant `queries/` files.

**Shell quoting pitfall**: When patching Python files remotely via SSH heredocs with `python3 - <<'PY'`, f-strings containing nested quotation marks will be corrupted. Use `.format(...)` or `chr(34)` for generated quotes inside such blocks, or write a script file directly.

**a800 GPU selection pitfall**: Before running CS336 CUDA experiments on `a800`, check `nvidia-smi -L` and explicitly select an A800. As of 2026-06-17, GPU 0 can be an RTX PRO 6000 Blackwell Server Edition (`sm_120`), while GPUs 1/2 are A800 (`sm_80`). Use `CUDA_VISIBLE_DEVICES=1` or `CUDA_VISIBLE_DEVICES=2` for assignment benchmarks by default. On 2026-06-18, GPU0 was visible under driver 580.126.09 / system CUDA 13.0 / nvcc 12.8, but the assignment env `torch 2.11.0+cu126` only exposed arch list `sm_50..sm_90`; a simple `CUDA_VISIBLE_DEVICES=0` PyTorch matmul failed with `CUDA error: no kernel image is available for execution on the device`. Do not migrate CS336 runs to GPU0 until the env has a Blackwell-capable PyTorch/CUDA build (e.g. CUDA 12.8/13.0 wheels including `sm_120`) and a real matmul smoke test passes. On 2026-06-18, the PyTorch official `cu130` index contained Linux x86_64 cp313 wheels for `torch-2.11.0+cu130` and `torch-2.12.x+cu130`, plus matching `torchvision` wheels. `pyproject.toml` and editable `cs336-basics/pyproject.toml` in assignment2-systems must use the same CUDA wheel index; mixing `cu126` and `cu130` makes `uv lock --upgrade-package torch` fail with conflicting torch indexes. After syncing `torch 2.11.0+cu130`, GPU0 Blackwell was validated: `torch.version.cuda == 13.0`, `torch.cuda.get_arch_list()` included `sm_120`, GPU0 FP32/BF16 matmul and SDPA backward passed, CS336 `benchmark.py` forward/backward smoke passed, and A800 GPU1 matmul still worked. If `uv sync` times out fetching `download-r2.pytorch.org`, prefer direct download first and set `UV_HTTP_TIMEOUT=600`; proxy `127.0.0.1:7897` can work but may be very slow. See `references/assignment2-blackwell-pytorch-cu130.md` for the validated migration, troubleshooting, and smoke-test commands. If `cudaGetDeviceCount() ... Error 101: invalid device ordinal` appears, verify current boot/driver state with `uptime -s`, `nvidia-smi -L`, `/proc/driver/nvidia/gpus/*/information`, and `dmesg -T | grep -i nvidia`; do not assume the issue is permanent, because a reboot/driver reload can change enumeration and make A800 usable again.

## Assignment 2 Model Sizes (Table 1)

Vocabulary size = 10,000 for all models below the leaderboard tier. Default context length is 512 unless specified otherwise.

| Size | d_model | d_ff | num_layers | num_heads |
|---|---:|---:|---:|---:|
| small | 768 | 3072 | 12 | 12 |
| medium | 1024 | 4096 | 24 | 16 |
| large | 1280 | 5120 | 36 | 20 |
| xl | 2560 | 10240 | 32 | 32 |
| 10B | 4608 | 12288 | 50 | 36 |

For 2.1.5/2.1.6, use `--batch-size 1` when running the xl model context lengths ≥ 1024 to avoid OOM. ctx=2048 with the xl model FP32 exhausts ~80 GB HBM; BF16 also OOMs due to attention intermediate sizes. Use ctx=1024 as the practical maximum.

For Assignment 2 Nsight Systems profiling, add minimal NVTX ranges around measured `forward`, `backward`, and `optimizer` sections in `benchmark.py` when timeline phases are hard to distinguish. Verify with `nsys stats ..._stats_nvtx_sum.csv` that `:forward`, `:backward`, and `:optimizer` ranges appear before asking the user to interpret the GUI timeline. For section 2.1.4(e), use a profiling-only attention monkeypatch in `benchmark.py` to add NVTX ranges for `attention_scores_matmul`, `attention_softmax`, `attention_mask`, and `attention_output_matmul`; see `references/assignment2-nsys-profiling.md` for the validated command matrix, summary CSV pattern, and answer template.

Assignment 2 numbering pitfall: after `2.1.6 Profiling Memory`, the PDF transitions to `3 Single-GPU Memory`; the next problem is `Problem (gradient_checkpointing): Memory-Optimal Gradient Checkpointing`, not "2.1.7". Refer to it as Section 3 gradient checkpointing.

## Remote Execution Convention

Operate on `a800` SSH host. **Two conventions:**

- **Commands shown to the user**: written as if already inside the a800 shell (no `ssh a800` prefix).
- **Agent tool execution**: still uses `ssh a800` with proper PATH.

- Local notes/repo root: `/Users/yiwencai/Documents/code/cs336`
- Remote assignment root: `/storage/caiyiwen/code/cs336/assignment`
- Assignment 1: `/storage/caiyiwen/code/cs336/assignment/assignment1-basics`
- Assignment 2: `/storage/caiyiwen/code/cs336/assignment/assignment2-systems`
- Default PATH: `export PATH=/storage/caiyiwen/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\$PATH`
- Example shown to user (no ssh prefix):

```bash
cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems
uv run pytest -q
```

When referencing the server in reports to the advisor, use the public wording `实验室 H100 服务器` unless the user explicitly asks for internal hostnames.

## Course Overview

Stanford CS336 is a course on language modeling from scratch. It covers:
- **Week 1**: Byte-level BPE tokenizers
- **Assignment 1**: Tokenizer + model components (embeddings, attention, MLP blocks, layer norm) + training-side utilities (AdamW, LR schedule, checkpoint)
- **Training pipelines**: Data loading, optimization, distributed training
- **Evaluation**: Perplexity, downstream tasks, scaling laws

## Tokenizers (Week 1)

### BPE Tokenizer Implementation

The byte-level BPE tokenizer is the first assignment. Key concepts:
- **Byte-level**: Operates on raw bytes, not characters
- **BPE merging**: Iteratively merge the most frequent byte pairs
- **Vocabulary building**: Build a vocabulary of subword units
- **Encoding/decoding**: Convert text to token IDs and back

### Common Issues

- **Unicode handling**: Ensure proper UTF-8 byte encoding
- **Special tokens**: Add BOS, EOS, PAD, UNK tokens
- **Vocabulary size**: Trade-off between coverage and efficiency
- **Pre-tokenization**: Handle whitespace, punctuation, and casing

### Debugging Tips

- Verify byte-level encoding with `text.encode('utf-8')`
- Check merge order against frequency counts
- Test round-trip: `decode(encode(text)) == text`
- Profile memory usage for large vocabularies

See `references/train-bpe-debugging-and-speed.md` for detailed debugging and performance optimization.

## Model Components (Assignment 1)

### Core Components

The model-side components include:
- **Token embeddings**: Map token IDs to dense vectors
- **Positional embeddings**: Add position information
- **Attention mechanisms**: Self-attention, multi-head attention
- **MLP blocks**: Feed-forward layers with GELU activation
- **Layer normalization**: Pre-norm and post-norm configurations
- **Residual connections**: Skip connections around attention and MLP blocks

### Architecture Patterns

- **Transformer decoder**: Stack of attention + MLP blocks
- **Causal masking**: Prevent attending to future tokens
- **Gradient checkpointing**: Trade compute for memory
- **Mixed precision**: FP16/BF16 training for efficiency

### Common Issues

- **Shape mismatches**: Verify tensor dimensions at each layer
- **Numerical stability**: Use layer norm before attention/MLP
- **Initialization**: Xavier/He initialization for weights
- **Gradient flow**: Check for vanishing/exploding gradients

## Mixed Precision (Assignment 2.1.5)

### Accumulation Accuracy

FP16 accumulation loses precision over many iterations (e.g., 0.01 × 1000 → 9.953 instead of 10.0). The fix: keep the accumulator in FP32. This is why `torch.autocast` keeps loss/gradients/reductions in FP32 while only downcasting matmuls.

### Autocast dtype Reasoning

Under `torch.autocast(device_type="cuda", dtype=torch.float16)`:
- Parameters: FP32 (unchanged)
- Linear/matmul outputs: FP16
- LayerNorm: FP32 (autocast excludes it; numerically sensitive statistics)
- Loss: FP32
- Gradients: FP32

LayerNorm still needs special treatment with BF16 (same exponent range but reduced mantissa).

### Benchmark Modification

Add `--mix-precision {fp32,bf16,fp16}` CLI arg. Map to `torch.dtype`, wrap forward/backward in `torch.autocast(device_type='cuda', dtype=dtype)`. `dtype=torch.float32` is a safe no-op for autocast.

Small models (d_model=128) won't show speedup. Use the larger Section 2.1.2 model sizes.

See `references/assignment2-mixed-precision.md` for the full workflow, accumulation demo, dtype table, and benchmark modification pattern.

## Training Pipelines

### Data Loading

- **Batching**: Pack sequences efficiently
- **Shuffling**: Randomize order each epoch
- **Distributed**: Shard data across GPUs
- **Streaming**: Load data on-the-fly for large datasets

### Optimization

- **Learning rate scheduling**: Warmup + cosine decay
- **Gradient clipping**: Prevent gradient explosion
- **Weight decay**: L2 regularization
- **Optimizer choice**: AdamW, Lion, etc.

### Distributed Training

- **DDP**: Data Distributed Parallel
- **FSDP**: Fully Sharded Data Parallel
- **Tensor parallelism**: Split layers across GPUs
- **Pipeline parallelism**: Split model stages across GPUs

### Training Verification (Tiny Sanity Run)

After completing Assignment 1 components, a tiny training run verifies the full pipeline is connected:

- **Weight initialization**: `normal(0, 1/sqrt(fan_in))` for linear layers, ones for RMSNorm
- **Weight dict**: 30 keys for a 3-layer TinyStories model (see reference)
- **Training step**: forward → cross-entropy loss → backward → optimizer step → checkpoint
- **Validation**: loss finite, grad exists, params change, checkpoint round-trips

See `references/weight-init-and-training-sanity-run.md` for the full weight dict structure, init formulas, and training loop skeleton.

## Evaluation

### Metrics

- **Perplexity**: Standard LM evaluation metric
- **Bits per byte**: Normalized perplexity
- **Downstream tasks**: GLUE, SuperGLUE, etc.
- **Human evaluation**: For generation quality

### Scaling Laws

- **Loss vs compute**: Power law relationship
- **Loss vs parameters**: Predictable scaling
- **Loss vs data**: Data size matters
- **Chinchilla**: Optimal compute allocation

## References

- `references/train-bpe-debugging-and-speed.md` — BPE tokenizer debugging and performance
- `references/api-quirks.md` — API quirks and workarounds for model components
- `references/weight-init-and-training-sanity-run.md` — Weight initialization formulas, weight dict structure, and tiny training sanity run setup
- `references/tiny-training-sanity-run.md` — Practical debugging checklist for Assignment 1 tiny training: `ParameterList + param_names`, dotted adapter keys, forward/backward/optimizer/checkpoint verification order
- `references/a800-assignment-workflow.md` — User-specific CS336 assignment-first workflow on the `a800` host, including paths, SSH command pattern, profiling progression, and GitHub SSH setup.
- `references/assignment2-nsys-profiling.md` — Validated Assignment 2 Nsight Systems profiling workflow (2.1.4): NVTX phase/attention annotations, formal matrix, kernel summary, and answer template.
- `references/assignment2-mixed-precision.md` — Validated Assignment 2 mixed precision workflow (2.1.5): accumulation demo, autocast dtype reasoning, BF16 benchmark integration, and validated speedup results.
- `references/assignment2-memory-profiling.md` — Validated Assignment 2 memory profiling workflow (2.1.6): memory profiler flag, single-step recording, pickle generation, OOM handling for XL model, and answer template.
- `references/assignment2-gradient-checkpointing.md` — Assignment 2 Section 3 gradient checkpointing workflow: handout numbering pitfall, activation checkpointing explanation, single-level block-size experiment, benchmark patch pattern, and answer template.
- `references/assignment2-flashattention-prep.md` — Assignment 2 Section 4 workflow: PyTorch attention benchmark, `torch.compile` comparisons, whole-model compile flag, FlashAttention paper-note path, **PyTorch FlashAttention-2 forward step-by-step implementation with online softmax tiling, state-scope FAQ, and common correctness pitfalls**.
- `references/assignment2-triton-flashattention-forward.md` — Triton FlashAttention-2 forward kernel reference: `tl.make_block_ptr`, `tl.advance` pitfall, `tl.dot` semantics, online softmax in Triton, dtype design, 1D block pointer tuple comma pitfall, host launch pattern, and verified pitfalls from session.
- `references/assignment2-flashattention-backward.md` — FlashAttention backward implementation: PyTorch backward helper with `torch.compile`, online softmax reverse derivation, gradient formulas for `dq/dk/dv`, **Triton backward kernel design (two-kernel strategy: dq vs dk/dv parallelization axes, tiling, and memory access patterns)**, causal masking in backward, and common dtype/broadcast pitfalls.
- `references/assignment2-flashattention-benchmarking.md` — FlashAttention benchmark workflow: `triton.testing.do_bench` sweep requirements, dedicated script shape, PyTorch-vs-Triton broadcast pitfall, bf16 backward dtype smoke test, and interpretation notes.
- `references/assignment2-torch-compile-attention.md` — Assignment 2 Section 4 workflow: naïve attention benchmarking, `torch.compile` attention comparison, full Transformer compile benchmark, validated A800 results, and shell pitfalls.
- `references/assignment2-ddp-implementation.md` — DDP implementation: parameter broadcast, async gradient all-reduce with hooks, `ReduceOp.AVG`, pending ops cleanup, and gradient accumulation patterns.
- `references/assignment2-fsdp-implementation.md` — FSDP implementation: parameter sharding, all-gather for forward/backward, reduce-scatter for gradients, `compute_dtype` casting, and `gather_full_params` for checkpointing.
- `references/assignment2-sharded-optimizer.md` — Sharded optimizer implementation: optimizer state sharding, compatibility with FSDP, `state_dict`/`load_state_dict` for sharded state, and memory efficiency patterns.
- `references/lecture6-kernels.md` — Brief overview of CS336 Lecture 6 (Kernels, Triton, XLA) and pointers to the full local notes.
- `references/assignment2-torch-compile-attention.md` — Assignment 2 Section 4 workflow: naïve attention benchmarking, `torch.compile` attention comparison, full Transformer compile benchmark, validated A800 results, and shell pitfalls.
- `references/assignment2-blackwell-pytorch-cu130.md` — GPU0 Blackwell (`sm_120`) migration notes: CUDA driver/toolkit/PyTorch wheel distinction, `cu128`/`cu130` wheel availability, uv workspace index conflict fix, slow wheel download recovery, and GPU0 smoke test.
- `references/lecture6-kernels.md` — Brief overview of CS336 Lecture 6 (Kernels, Triton, XLA) and pointers to the full local notes.
- Course website: https://stanford-cs336.github.io/
- `references/assignment2-mixed-precision.md` — Assignment 2.1.5 mixed precision workflow: accumulation accuracy demo, autocast dtype reasoning (a)-(b), benchmark modification pattern with `--mix-precision` flag, smoke test commands, and pitfalls (small models won't show speedup).
- Course website: https://stanford-cs336.github.io/

## Related Skills

- `llm-fine-tuning` — For fine-tuning trained models
- `llm-inference-serving` — For deploying trained models
- `research-paper-writing` — For writing up results