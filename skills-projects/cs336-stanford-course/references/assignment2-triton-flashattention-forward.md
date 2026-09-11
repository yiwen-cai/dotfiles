# Assignment 2 Triton FlashAttention Forward Implementation Reference

Use this reference when the user implements the Triton forward kernel for `flash_forward` in Assignment 2 Section 4.

## Triton Kernel Structure

```python
import triton
import triton.language as tl

@triton.jit
def flash_fwd_kernel(
    Q_ptr, K_ptr, V_ptr, O_ptr, L_ptr,
    stride_qb, stride_qq, stride_qd,
    stride_kb, stride_kk, stride_kd,
    stride_vb, stride_vk, stride_vd,
    stride_ob, stride_oq, stride_od,
    stride_lb, stride_lq,
    N_QUERIES, N_KEYS,
    scale,
    D: tl.constexpr,
    Q_TILE_SIZE: tl.constexpr,
    K_TILE_SIZE: tl.constexpr,
):
    query_tile_index = tl.program_id(0)
    batch_index = tl.program_id(1)
    ...
```

## Block Pointer Creation

```python
Q_block_ptr = tl.make_block_ptr(
    base=Q_ptr + batch_index * stride_qb,
    shape=(N_QUERIES, D),
    strides=(stride_qq, stride_qd),
    offsets=(query_tile_index * Q_TILE_SIZE, 0),
    block_shape=(Q_TILE_SIZE, D),
    order=(1, 0),
)
```

- `order=(1, 0)` means dimension 1 (the last dimension, `D`) changes fastest — row-major layout.
- `order` describes the **current memory layout**, not a request to rearrange.
- For PyTorch tensors, always use `order=(1, 0)` for 2D.

## Loading Data

```python
q = tl.load(Q_block_ptr, boundary_check=(0, 1)).to(tl.float32)
```

- `boundary_check=(0, 1)` checks both dimensions; out-of-bounds elements are not loaded (or padded if `other=` is specified).
- Convert to `fp32` immediately for numerical stability in softmax.

## Tiling and Advancing Pointers

**Pitfall**: `tl.advance` is **relative** to the current pointer position. Do not accumulate `k_tile_index * K_TILE_SIZE` inside the loop — that double-advances.

**Correct pattern**:

```python
K_block_ptr = tl.make_block_ptr(
    base=K_ptr + batch_index * stride_kb,
    shape=(N_KEYS, D),
    strides=(stride_kk, stride_kd),
    offsets=(0, 0),                    # start at k=0
    block_shape=(K_TILE_SIZE, D),
    order=(1, 0),
)

for k_tile_index in range(tl.cdiv(N_KEYS, K_TILE_SIZE)):
    if k_tile_index > 0:
        K_block_ptr = tl.advance(K_block_ptr, (K_TILE_SIZE, 0))
    ...
```

Alternative: recreate the block pointer each iteration with `offsets=(k_tile_index * K_TILE_SIZE, 0)`.

## Matrix Multiplication with `tl.dot`

**Critical clarification**: `tl.dot(a, b)` performs **standard matrix multiplication** `a @ b` (not `a @ b.T`). The assertion `a_shape[-1] == b_shape[-2]` must hold.

| Desired math | Triton code | Shapes | Notes |
|-------------|-------------|--------|-------|
| `Q @ K^T` | `tl.dot(q, tl.trans(k))` | `q:(Q,D)`, `k:(K,D)`, `k.T:(D,K)` → `(Q,K)` | **Must explicitly transpose `k`** |
| `P @ V` | `tl.dot(p, v)` | `p:(Q,K)`, `v:(K,D)` → `(Q,D)` | Standard matmul, no transpose needed |

**Verified pitfall from session**: Writing `tl.dot(q, k)` with `q:(Q_TILE_SIZE,D)` and `k:(K_TILE_SIZE,D)` fails with `AssertionError: input and other must have equal reduction dimensions` because `D != K_TILE_SIZE`. The fix is `tl.dot(q, tl.trans(k))`.

## Online Softmax State Updates

```python
m = tl.full((Q_TILE_SIZE,), float("-inf"), dtype=tl.float32)
l = tl.zeros((Q_TILE_SIZE,), dtype=tl.float32)
o = tl.zeros((Q_TILE_SIZE, D), dtype=tl.float32)

for ...:
    scores = tl.dot(q, k) * scale        # (Q_TILE_SIZE, K_TILE_SIZE)
    m_new = tl.maximum(m, tl.max(scores, axis=1))
    alpha = tl.exp(m - m_new)
    p_tilde = tl.exp(scores - m_new[:, None])
    l = l * alpha + p_tilde.sum(axis=1)
    pv = tl.dot(p_tilde.to(tl.float32), tl.trans(v))
    o = o * alpha[:, None] + pv
    m = m_new
```

**Pitfall**: `alpha` must rescale **both** `l` and `o`. Forgetting to rescale `o` when `m` increases is a common correctness bug.

## Dtype Design

| Tensor | Recommended dtype | Reason |
|--------|-----------------|--------|
| `Q, K, V` input | `bf16`/`fp16` | Memory bandwidth |
| `scores`, `m`, `l`, `o` | `fp32` | Numerical stability |
| Final `O` output | `bf16`/`fp16` | Match input dtype |
| `L` (logsumexp) | `fp32` | Backward needs precision |

```python
q = tl.load(Q_block_ptr).to(tl.float32)   # load half, compute fp32
...
o = o.to(tl.bfloat16)                     # convert back before store
tl.store(O_block_ptr, o, boundary_check=(0, 1))
```

## Storing Output

```python
O_block_ptr = tl.make_block_ptr(
    base=O_ptr + batch_index * stride_ob,
    shape=(N_QUERIES, D),
    strides=(stride_oq, stride_od),
    offsets=(query_tile_index * Q_TILE_SIZE, 0),
    block_shape=(Q_TILE_SIZE, D),
    order=(1, 0),
)

tl.store(O_block_ptr, o, boundary_check=(0, 1))
```

- `boundary_check` prevents writing out-of-bounds on the last tile.
- `tl.store` does **not** have a `dtype` parameter; convert `o` before storing.

## 1D Block Pointer for `L`

```python
L_block_ptr = tl.make_block_ptr(
    base=L_ptr + batch_index * stride_lb,
    shape=(N_QUERIES,),          # tuple with trailing comma!
    strides=(stride_lq,),        # tuple with trailing comma!
    offsets=(query_tile_index * Q_TILE_SIZE,),  # tuple with trailing comma!
    block_shape=(Q_TILE_SIZE,),  # tuple with trailing comma!
    order=(0,),                  # tuple with trailing comma!
)

tl.store(L_block_ptr, L, boundary_check=(0,))
```

**Pitfall**: Forgetting the trailing comma makes `(N_QUERIES)` an integer, not a tuple. Triton will error or misinterpret.

## Common User Questions

### Q: Does `tl.zeros` need a `device` argument?
A: **No.** Triton kernels run on GPU; `tl.zeros` allocates in SRAM automatically. No `device="cuda"` needed.

### Q: Can I use `/` for scalar division?
A: **Yes.** `scores * scale` where `scale = 1.0 / sqrt(D)` works exactly like PyTorch. Ensure `scale` is a Python float, not an integer.

### Q: Does `unsqueeze` work in Triton?
A: **Partially.** The `[:, None]` slice syntax works identically to PyTorch. However, **Triton tensor objects do NOT have an `.unsqueeze()` method** — calling `m_new.unsqueeze(-1)` raises `AttributeError: 'tensor' object has no attribute 'unsqueeze'`. Always use `m_new[:, None]` in Triton kernels.

### Q: What is `acc` in `tl.dot(q, k, acc=scores)`?
A: It means `scores = scores + q @ k.T`. **Not used in standard FlashAttention** — each key tile is processed independently. Use `acc` only for true tiled matrix multiplication (GEMM), not for online softmax.

## Host-Side Launch Pattern

```python
def flash_attention_triton(q, k, v, is_causal=False):
    batch, n_q, d = q.shape
    n_k = k.shape[1]
    
    o = torch.empty_like(q)
    l = torch.empty(batch, n_q, device=q.device, dtype=torch.float32)
    
    grid = (triton.cdiv(n_q, Q_TILE_SIZE), batch)
    
    flash_fwd_kernel[grid](
        q, k, v, o, l,
        q.stride(0), q.stride(1), q.stride(2),
        k.stride(0), k.stride(1), k.stride(2),
        v.stride(0), v.stride(1), v.stride(2),
        o.stride(0), o.stride(1), o.stride(2),
        l.stride(0), l.stride(1),
        n_q, n_k,
        1.0 / (d ** 0.5),
        D=d,
        Q_TILE_SIZE=64,
        K_TILE_SIZE=64,
    )
    
    return o, l
```

## Adapter Wiring for Triton

Same pattern as PyTorch version:

```python
# tests/adapters.py
import cs336_systems

def get_flashattention_autograd_function_triton() -> type:
    return cs336_systems.flashattention.FlashAttentionTriton
```

The Triton `autograd.Function` should:
1. Call the Triton kernel in `forward`
2. Save `q, k, v, o, L` for backward
3. Implement `backward` (or raise `NotImplementedError` until ready)

## Causal Mask in Triton

Pass `is_causal` as a `constexpr` and apply the mask before softmax:

```python
@triton.jit
def flash_fwd_kernel(
    ...,
    is_causal: tl.constexpr,
):
    query_tile_index = tl.program_id(0)
    ...
    q_idx = query_tile_index * Q_TILE_SIZE + tl.arange(0, Q_TILE_SIZE)

    for k_tile_index in range(0, tl.cdiv(N_KEYS, K_TILE_SIZE)):
        ...
        scores = tl.dot(q, tl.trans(k)) * scale

        if is_causal:
            k_idx = k_tile_index * K_TILE_SIZE + tl.arange(0, K_TILE_SIZE)
            causal_mask = q_idx[:, None] >= k_idx[None, :]
            scores = tl.where(causal_mask, scores, -1e6)

        m_new = tl.maximum(m, tl.max(scores, axis=1))
        ...
```

**Host-side launch** — pass `is_causal` as a keyword argument (it becomes `constexpr` automatically):

```python
flash_fwd_kernel[grid](
    ...,
    is_causal=is_causal,  # Python bool → tl.constexpr
)
```

**Boundary pitfall**: `q_idx` may exceed `N_QUERIES` on the last tile (e.g., `N_QUERIES=130`, `Q_TILE_SIZE=16`, last tile has `q_idx=128..143`). The `tl.load` with `boundary_check` pads invalid queries with `0`, but `q_idx` itself is still large. For `is_causal=True`, this means invalid positions get `q_idx >= k_idx → True`, incorrectly including them in the mask. The test shapes happen to be multiples of 16, so this may not trigger in the provided tests, but it is a real bug for arbitrary shapes. A robust fix is to additionally mask `q_idx < N_QUERIES`.

## Verified Pitfalls from Session

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| `tl.dot(q, k)` without transpose | `AssertionError: input and other must have equal reduction dimensions` | `tl.dot(q, tl.trans(k))` — `tl.dot` is standard matmul, not `a @ b.T` |
| `m_new.unsqueeze(-1)` in Triton kernel | `AttributeError: 'tensor' object has no attribute 'unsqueeze'` | Use `m_new[:, None]` instead |
| `tl.advance` with absolute `k_tile_index * K_TILE_SIZE` | Pointer advances exponentially, wrong tiles loaded | Use fixed `K_TILE_SIZE` step with `if k_tile_index > 0` |
| `shape=(N_QUERIES)` without comma | Type error or silent misshape | Always use `(N_QUERIES,)` for 1D |
| `p_tilde.to(v.dtype)` not assigned | `pv` still fp32, potential dtype mismatch | `p_tilde = p_tilde.to(v.dtype)` |
| `tl.store(..., dtype=...)` | `TypeError` — `dtype` is not a `tl.store` argument | Convert tensor before store: `o = o.to(tl.bfloat16)` |
| Forgetting `boundary_check` on last tile | Writes out-of-bounds, CUDA error | Add `boundary_check=(0,)` or `(0, 1)` |
| `scale` as integer | Integer division, wrong attention weights | `scale = 1.0 / (D ** 0.5)` |
| `q_idx` out of bounds on last tile | Invalid queries incorrectly included in causal mask | Also mask `q_idx < N_QUERIES` |
