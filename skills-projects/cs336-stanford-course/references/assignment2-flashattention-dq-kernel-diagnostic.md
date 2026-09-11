# Isolated dq Kernel Diagnostic for CS336 FlashAttention Backward

Use this when the user has written a Triton `flash_attention_backward_dq` kernel and wants to verify only the `dq` path, independent of Triton forward and independent of `dk/dv`.

## Purpose

The test isolates `dq` correctness by:

1. Building random `q, k, v, do` tensors on CUDA.
2. Computing reference `o` and `L=logsumexp(scores)` with pure PyTorch attention.
3. Computing `dq_expected` using PyTorch autograd.
4. Launching only `flash_attention_backward_dq`, writing `dq_actual`.
5. Comparing `dq_actual` vs `dq_expected` with `rtol=1e-2, atol=1e-2`.

This prevents false attribution from bugs in:
- Triton forward output/LSE generation.
- `dk/dv` kernels.
- Autograd wrapper return order.

## Recommended Cases

Run both `is_causal=False` and `is_causal=True`:

| Case | Shape `(batch, n_q, n_k, d)` | Why |
|---|---:|---|
| tiny | `(1, 8, 8, 16)` | Single tile, easy formula debugging |
| tile boundary | `(2, 16, 16, 32)` | Exactly one full tile |
| non-multiple query/key | `(2, 31, 29, 32)` | Boundary masks |
| assignment shape | `(4, 128, 128, 64)` | Official default scale |

## Key Diagnostic Pattern

If `(n_q=31, n_k=32)` fails but `(n_q=32, n_k=29)` passes, the issue is likely query-tile boundary handling rather than key-tile boundary handling.

A common signature is that the bad row appears as `(batch=1, q=0)` after a non-causal run with `batch=2, n_q=31`: an unmasked store for logical `(batch=0, q=31)` can overwrite the contiguous memory location for `(batch=1, q=0)`.

## Boundary Rule for dq Kernel

The host launch should use ceil-div:

```python
grid = (triton.cdiv(n_queries, Q_TILE_SIZE), batch)
```

Do not floor-divide, or the last partial query tile is skipped. Instead, the kernel must mask every query-indexed load/store:

```python
q_offsets = q_tile_id * Q_TILE_SIZE + tl.arange(0, Q_TILE_SIZE)
q_mask = q_offsets < n_queries
```

Apply `q_mask` to:

- `tl.load(q, mask=q_mask[:, None], other=0.0)`
- `tl.load(o, mask=q_mask[:, None], other=0.0)`
- `tl.load(do, mask=q_mask[:, None], other=0.0)`
- `tl.load(L, mask=q_mask, other=...)`
- `tl.store(dq, ..., mask=q_mask[:, None])`

For safety, combine query and key masks when reconstructing score/probability tiles:

```python
valid = q_mask[:, None] & k_mask[None, :]
s = tl.where(valid, s, -float("inf"))
```

The minimum correctness requirement is masked query loads and masked `dq` store; score masking is a robustness improvement.

## Interpreting Tolerances

For FP32 Triton kernels on this assignment, `rtol=1e-2, atol=1e-2` matches official backward tolerance. `1e-3` may fail due to tile accumulation order and exp/dot differences even when the implementation is acceptable.
