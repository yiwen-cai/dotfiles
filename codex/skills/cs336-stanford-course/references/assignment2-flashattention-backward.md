# Assignment 2 FlashAttention Backward Implementation

Use this reference after `flash_forward` tests pass and the user is working on `flash_backward`.

## Implementation Approach

The assignment allows implementing backward with `torch.compile` over a PyTorch helper rather than a Triton backward kernel. This is the recommended path:

1. Implement `flash_attention_backward_pytorch(q, k, v, L, o, do, is_causal)` as a regular PyTorch function
2. In `FlashAttention.backward`, call `torch.compile(flash_attention_backward_pytorch)(...)`
3. Return `dq, dk, dv, None` (the `None` is for `is_causal` which doesn't need grad)

## Backward Derivation

Given:
- `s = QK^T / sqrt(d)` — attention scores
- `p = softmax(s)` — attention probabilities
- `o = p @ V` — output
- `do` — gradient w.r.t. output

We need to compute `dq`, `dk`, `dv`.

### Step 1: Recompute probabilities from saved LSE

`L = logsumexp(s)` was saved in forward. Recompute:

```python
s = einsum(q, k, "b q d, b k d -> b q k") * scale
if is_causal:
    mask = torch.arange(n_q, device=q.device)[:, None] >= torch.arange(n_k, device=q.device)[None, :]
    s = s.masked_fill(~mask, -1e6)
p = torch.exp(s - L.unsqueeze(-1))
```

**Critical**: Cast `p` to the input dtype before matmuls to avoid `torch.compile`/Inductor dtype mismatch errors in BF16 mode.

### Step 2: Compute dv

```python
dv = einsum(p, do, "b q k, b q d -> b k d")
```

### Step 3: Compute dp and D (diagonal scaling factor)

```python
dp = einsum(do, v, "b q d, b k d -> b q k")
D = (o * do).sum(dim=-1)  # shape: (batch, n_q)
```

### Step 4: Compute ds (gradient w.r.t. scores)

```python
ds = p * (dp - D.unsqueeze(-1))  # shape: (batch, n_q, n_k)
```

This is the standard softmax backward: `dL/ds = p * (dL/dp - sum(dL/dp * p))`.

### Step 5: Compute dq and dk

```python
dq = einsum(ds, k, "b q k, b k d -> b q d") * scale
dk = einsum(ds, q, "b q k, b q d -> b k d") * scale
```

## Full Backward Function

```python
def flash_attention_backward_pytorch(q, k, v, L, o, do, is_causal=False):
    n_q, d = q.shape[-2], q.shape[-1]
    n_k = k.shape[-2]
    scale = 1 / math.sqrt(d)
    
    # Recompute scores and probabilities
    s = einsum(q, k, "b q d, b k d -> b q k") * scale
    if is_causal:
        mask = (
            torch.arange(n_q, device=q.device)[:, None]
            >= torch.arange(n_k, device=q.device)[None, :]
        )
        s = s.masked_fill(~mask, -1e6)
    
    # Cast to input dtype for matmul compatibility
    p = torch.exp(s - L.unsqueeze(-1)).to(q.dtype)
    
    # Gradients
    dv = einsum(p, do, "b q k, b q d -> b k d")
    dp = einsum(do, v, "b q d, b k d -> b q k")
    D = (o * do).sum(dim=-1)
    ds = p * (dp - D.unsqueeze(-1))
    dq = einsum(ds, k, "b q k, b k d -> b q d") * scale
    dk = einsum(ds, q, "b q k, b q d -> b k d") * scale
    
    return dq, dk, dv
```

## Critical Pitfalls

### Dtype mismatch in BF16

When inputs are `torch.bfloat16`, `torch.exp(s - L)` produces `float32` (because `L` is `float32`). If `v` and `do` are `bfloat16`, `einsum(p, do)` will fail with:

```
expected mat1 and mat2 to have the same dtype, but got: float != c10::BFloat16
```

**Fix**: Always cast `p` to the input dtype: `p = torch.exp(s - L.unsqueeze(-1)).to(q.dtype)`

### Causal mask in backward

If forward used causal masking, backward must also apply the same causal mask when recomputing `s`. Otherwise the gradient will be incorrect for the masked positions.

### Forgetting to scale

`dq` and `dk` must be multiplied by `scale = 1/sqrt(d)` because `s = QK^T / sqrt(d)`. Forgetting this scale factor causes gradient magnitude mismatch.

### Shape broadcasting with `D.unsqueeze(-1)`

`D` has shape `(batch, n_q)`. To broadcast with `p` of shape `(batch, n_q, n_k)`, use `D.unsqueeze(-1)` to get `(batch, n_q, 1)`. Using `D[:, None]` on a 2D tensor gives `(batch, 1, n_q)` which is wrong.

## Triton Backward Kernel Design

### The Core Problem: Different Parallelization Axes for dq vs dk/dv

The backward pass must compute three gradients (`dq`, `dk`, `dv`), but they have **different data-locality patterns**. A single kernel cannot efficiently compute all three because the parallelization axis differs:

| Gradient | Parallelization axis | Inner loop | Why |
|----------|---------------------|------------|-----|
| `dq` | over `q_tiles` | iterates over `k_tiles` | `dq[i]` depends on all `k[j]` |
| `dk` | over `k_tiles` | iterates over `q_tiles` | `dk[j]` depends on all `q[i]` |
| `dv` | over `k_tiles` | iterates over `q_tiles` | `dv[j]` depends on all `q[i]` (via `p[i,j]`) |

**Key insight**: `dk` and `dv` share the same parallelization axis (`k_tiles`), so they belong in the **same kernel**. `dq` needs its **own kernel**.

### Kernel 1: `flash_attention_backward_dq`

```python
# Grid: (num_q_tiles, batch)
# Each block: computes one q_tile's dq
# Inner loop: iterates over all k_tiles

for k_tile_index in range(num_k_tiles):
    k_tile = load_k_tile(k_tile_index)
    v_tile = load_v_tile(k_tile_index)
    
    # Recompute p_tile for this q_tile x k_tile
    s = dot(q_tile, k_tile.T) * scale
    p = exp(s - l_tile[:, None])
    
    # Accumulate dq
    dp = dot(do_tile, v_tile.T)
    D = sum(o_tile * do_tile, axis=-1)
    ds = p * (dp - D[:, None])
    dq += dot(ds, k_tile) * scale
```

**Isolated diagnostic**: when only `dq` is suspect, compare a standalone `flash_attention_backward_dq` launch against PyTorch autograd while feeding it PyTorch-computed `o` and `L`; see `references/assignment2-flashattention-dq-kernel-diagnostic.md`.

**Boundary pitfall**: even though each program owns one `q_tile`, the last `q_tile` may be partial. Use ceil-div grid launch, then mask every query-indexed load/store with `q_offsets < n_queries`, especially `tl.store(dq, ..., mask=q_mask[:, None])`. An unmasked store for logical `(batch=0, q=n_q)` can overwrite contiguous `(batch=1, q=0)`.

### Kernel 2: `flash_attention_backward_dk_dv`

```python
# Grid: (num_k_tiles, batch)
# Each block: computes one k_tile's dk and dv
# Inner loop: iterates over all q_tiles

for q_tile_index in range(num_q_tiles):
    q_tile = load_q_tile(q_tile_index)
    do_tile = load_do_tile(q_tile_index)
    o_tile = load_o_tile(q_tile_index)
    l_tile = load_l_tile(q_tile_index)
    
    # Recompute p_tile for this q_tile x k_tile
    s = dot(q_tile, k_tile.T) * scale
    p = exp(s - l_tile[:, None])
    
    # Accumulate dv and dk
    dv += p.T @ do_tile           # (K_TILE_SIZE, Q_TILE_SIZE) @ (Q_TILE_SIZE, D)
    dp = do_tile @ v_tile.T        # (Q_TILE_SIZE, D) @ (D, K_TILE_SIZE)
    D = sum(o_tile * do_tile, axis=-1)
    ds = p * (dp - D[:, None])
    dk += ds.T @ q_tile * scale   # (K_TILE_SIZE, Q_TILE_SIZE) @ (Q_TILE_SIZE, D)
```

### Why dv Does NOT Go in the dq Kernel

A common mistake is to try to compute `dv` inside the `dq` kernel. The problem:

- In the `dq` kernel, you iterate over `k_tiles` **sequentially** within each block
- `dv[j]` needs contributions from **all** `q_tiles`, but each block only sees one `q_tile` at a time
- You would need atomic writes or a reduction across blocks to accumulate `dv`, which is inefficient

Instead, by launching a separate kernel with `grid=(num_k_tiles, batch)`, each block has exclusive ownership of one `k_tile`'s `dv` and `dk`, and can accumulate locally without atomics.

### Memory Access Pattern Summary

| Kernel | Loads per block | Writes per block | SRAM footprint |
|--------|----------------|------------------|----------------|
| `backward_dq` | `q_tile` (fixed), `k_tile`, `v_tile` (streamed) | `dq_tile` | `2 * Q_TILE_SIZE * D + 2 * K_TILE_SIZE * D` |
| `backward_dk_dv` | `k_tile`, `v_tile` (fixed), `q_tile`, `do_tile`, `o_tile` (streamed) | `dk_tile`, `dv_tile` | `2 * K_TILE_SIZE * D + 3 * Q_TILE_SIZE * D` |

### Triton Backward (Optional/Advanced)

If implementing Triton backward kernel, the approach is:

1. Load `q`, `k`, `v`, `o`, `do` tiles
2. Recompute `p` from saved `L` (or recompute online)
3. Compute `dv = p^T @ do` tile by tile
4. Compute `dp = do @ v^T`
5. Compute `D = sum(o * do, axis=-1)`
6. Compute `ds = p * (dp - D)`
7. Compute `dq = ds @ k * scale` and `dk = ds^T @ q * scale`

The Triton backward is significantly more complex than forward due to the need to load tiles in different orders for `dq`, `dk`, `dv`.

## Test Expectations

- `test_flash_backward_pytorch`: Compares against naive attention backward with `rtol=1e-2, atol=1e-2`
- `test_flash_backward_triton[False/True]`: Same comparison but on CUDA with Triton implementation
- All gradients (`q.grad`, `k.grad`, `v.grad`) must match the reference

## Adapter Wiring

```python
# tests/adapters.py
def get_flashattention_autograd_function_triton() -> type:
    return cs336_systems.flashattention.FlashAttention
```

And in `cs336_systems/__init__.py`:
```python
from .flashattention import FlashAttention, FlashAttentionPytorch
```
