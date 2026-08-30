# CS336 Lecture 6: Kernels, Triton, XLA

**Source**: `lecture_06.py` from https://github.com/stanford-cs336/lectures (reproduced via `lecture6-kernels.md`)

## Core Topics

1. **Hardware review** — SM parameters, thread/block/grid model, warps, occupancy, bank conflicts, memory coalescing, wave quantization
2. **Benchmarking & Profiling** — CUDA events vs Python timers, `torch.profiler`, reading CUDA kernel names (tile sizes, architecture codes)
3. **Kernel fusion** — naive vs builtin vs `torch.compile` GeLU demo
4. **Triton kernels** — GeLU (elementwise), softmax (row reduction), row sum (tiled reduction), matmul+ReLU (tiling + fusion)

## Key Takeaways for Assignments

- CUDA kernel names encode tile shapes and architecture (e.g. `ampere_sgemm_128x128_nn` → 128×128 output tile, Ampere, not-transposed-not-transposed). These are **not** user-level sequence lengths.
- Operator fusion reduces HBM traffic by keeping intermediate values in registers instead of writing them to global memory.
- Triton programming model: "think in thread blocks, not threads" — load to shared memory, operate, write back.
- Matmul tiling arithmetic intensity ≈ O(tile_size), much better than naive O(1).

## Local Files

- `/Users/yiwencai/Documents/code/cs336/notes/lecture6-kernels.md` — Full markdown notes
- `/Users/yiwencai/Documents/code/cs336/notes/lecture6-kernels.html` — Rendered HTML
