# CS336 Model Components TDD Coaching Notes

Use this reference when guiding the user through CS336 Assignment 1 model-side implementation without directly writing graded code.

## TA-style boundary

For CS336 assignment code, act as a teaching assistant, not a solution generator:

- read public tests/adapters;
- explain concepts and shape contracts;
- suggest sanity checks and toy tensors;
- review user-written snippets;
- interpret failures;
- give staged TDD plans.

Do not directly edit core assignment implementations or paste complete graded-code solutions.

## Recommended component order

1. Pure utilities/data: `softmax`, `cross_entropy`, `get_batch`.
2. Basic layers: `linear`, `embedding`, `rmsnorm`, `silu`.
3. FFN/position: `swiglu`, `rope`.
4. Attention core: scaled dot-product attention and 4D attention.
5. MHA: without RoPE, then with RoPE.
6. Block and full LM.
7. Optimizer/schedule/checkpoint/training loop.

## SwiGLU pitfall

CS336/LLaMA-style FFN uses:

```text
SwiGLU(x) = W2(SiLU(W1 x) ⊙ W3 x)
```

`w1` is the gate branch that receives SiLU; `w3` is the up branch. If `test_swiglu` shows 100% snapshot mismatch with large max diff while shapes are correct, check whether the implementation accidentally used:

```text
W2(W1(x) ⊙ SiLU(W3(x)))
```

Multiplication is commutative, but moving the nonlinear SiLU between branches is not.

## Snapshot test debugging via candidate formula comparison

When a CS336 public test fails with 100% element mismatch and large max diff, shapes are usually right but the formula is wrong. Don't guess — enumerate candidates and compare them against the snapshot directly.

Procedure:

1. Locate the snapshot file under `tests/fixtures/ts_tests/` (commonly `model.pt`).
2. Load it with `torch.load(path, map_location="cpu")`; strip `_orig_mod.` prefixes if present.
3. Extract the test's input fixture (e.g. `in_embeddings`, `pos_ids`) and the weight tensors the test uses.
4. Write each candidate formula in a small script and compute the output.
5. Compare each output to the snapshot's expected output using `numpy_snapshot` semantics: `np.allclose(actual, expected, atol=1e-5)`.
6. The candidate with `max abs diff ≈ 0.0` is the correct one.

Concrete example — `test_swiglu` failure:

```text
Mismatched elements: 3072 / 3072
Max absolute difference: 3.42755
```

Candidates to compare against the snapshot:

```text
A: linear(x, w1) * SiLU(linear(x, w3))    # wrong
B: SiLU(linear(x, w1)) * linear(x, w3)    # correct
```

Both can be computed from the same fixture weights; the one with `max diff = 0.0` matches the snapshot.

Pitfall: do not rely on intuition for branch ordering when a nonlinearity is involved. Multiplication is commutative, but `a * SiLU(b) != SiLU(a) * b` in general. The snapshot is the ground truth; the comparison script is faster than visual code review and scales to multiple candidates at once.

The same approach generalizes to:

- RoPE candidate exponent formulations (e.g. `-i/d` vs `-2i/d`).
- Causal mask direction (`k <= q` vs `k < q`).
- Whether RoPE is applied to V or not (it should not be).
- Multi-head split location (split projected Q/K/V, not raw `in_features`).
- Embedding / unembedding weight tying vs separate LM head.

## RoPE implementation checklist

RoPE acts on paired dimensions of the final head/model dimension.

1. Split the last dimension:

```text
even = x[..., 0::2]
odd  = x[..., 1::2]
```

2. Compute frequencies:

```text
freq_i = theta ** (-2*i/d_k)
```

3. Form angles from token positions:

```text
angle = token_positions * freq
```

For current 1D positions, `angle.shape` may be `(seq, d_k/2)` and broadcast over batch. For batched positions, preserve prefix dims conceptually as:

```text
... s, d -> ... s d
```

4. Rotate:

```text
out_even = even*cos(angle) - odd*sin(angle)
out_odd  = even*sin(angle) + odd*cos(angle)
```

5. Interleave back:

```text
out[..., 0::2] = out_even
out[..., 1::2] = out_odd
```

Do not concatenate evens then odds; that changes dimension order from `[0,1,2,3,...]` to `[0,2,4,...,1,3,5,...]`.

## RoPE device/broadcast pitfalls

- Create frequency indices on `in_query_or_key.device`.
- Move external `token_positions` to `in_query_or_key.device` before computing `angle`.
- Device propagates through tensor ops only when participating tensors are already on the same device.
- Python scalars do not change device.
- A CPU `token_positions` multiplied by a CUDA `freq` will fail.
- `torch.cos(angle)` and `torch.sin(angle)` preserve `angle.device`.
- `torch.empty_like(in_query_or_key)` inherits shape, dtype, and device from the input.
- For future MHA input like `(batch, heads, seq, head_dim)`, a batched angle `(batch, seq, head_dim/2)` may need an inserted singleton head dimension `(batch, 1, seq, head_dim/2)` before broadcasting.

## Scaled dot-product attention checklist

Use this after RoPE passes and before MHA.

Shape contract:

```text
Q:    (..., queries, d_k)
K:    (..., keys, d_k)
V:    (..., keys, d_v)
mask: (..., queries, keys) | None
out:  (..., queries, d_v)
```

Implementation checks:

- Scores should have shape `(..., queries, keys)` via either `Q @ K.transpose(-2, -1)` or einsum pattern `... q d, ... k d -> ... q k`.
- Divide scores by `sqrt(d_k)` before softmax.
- Mask semantics in the CS336 tests: `True` means keep, `False` means block. Apply `masked_fill(~mask, -inf)` before softmax.
- Softmax must be over the key dimension (`dim=-1`).
- The output contraction is `... q k, ... k d -> ... q d`.
- Prefer non-in-place `scores = scores.masked_fill(...)` when possible; in-place works on fresh temporaries in the public tests but is less robust for autograd/debugging.
- Do not hard-code 3D shapes; the same implementation should pass 4D inputs where prefix dims include heads.

## Multi-head attention checklist

Use this after scaled dot-product attention and 4D attention pass.

Flow for non-RoPE MHA:

```text
in_features
  -> Q/K/V projection
  -> split Q/K/V heads: ... s (h d) -> ... h s d
  -> causal scaled dot-product attention
  -> merge heads: ... h s d -> ... s (h d)
  -> output projection
```

Pitfalls:

- Split heads on the projected `Q`, `K`, and `V`, not on raw `in_features`. Splitting only `in_features` while passing un-split Q/K/V to attention makes the later merge reinterpret a 3D tensor as multi-head output and can inflate the final dimension (e.g. 64 -> 256).
- Keep heads in prefix dims for the attention core: `(batch, heads, seq, d_head)` fits the `(..., queries, d_k)` contract.
- Build a causal mask with `mask[q, k] = True iff k <= q` (lower triangular including diagonal). Put it on the input device for GPU safety.
- Do not forget the final output projection with `o_proj_weight` after merging heads.

## MHA with RoPE checklist

Use this after ordinary MHA passes.

Flow:

```text
Q/K/V projection
  -> split heads
  -> RoPE(Q), RoPE(K), V unchanged
  -> causal scaled dot-product attention
  -> merge heads
  -> output projection
```

Important details:

- Apply RoPE after splitting heads, not before. The RoPE dimension is `d_head = d_model // num_heads`, not full `d_model`.
- Apply RoPE only to Q and K; never to V. Position should affect `QK^T` attention logits, not the values being aggregated.
- In the public test, `token_positions` is reshaped from `(seq,)` to `(1, seq)`. A RoPE implementation that preserves prefix dims in the angle computation (`... s, d -> ... s d`) broadcasts naturally to `(batch, heads, seq, d_head/2)`.

## Transformer block and LM checklist

Use this after MHA with RoPE passes. Treat these as composition tests: most failures come from ordering, missing positions, or state-dict key handling rather than new formulas.

### Pre-LN Transformer block

CS336/LLaMA-style block uses:

```text
x1 = x0 + MHA_with_RoPE(RMSNorm(x0, ln1.weight))
x2 = x1 + SwiGLU(RMSNorm(x1, ln2.weight))
```

Block-local weight keys expected by `run_transformer_block` are typically:

```text
attn.q_proj.weight
attn.k_proj.weight
attn.v_proj.weight
attn.output_proj.weight
ln1.weight
ln2.weight
ffn.w1.weight
ffn.w2.weight
ffn.w3.weight
```

Pitfalls:

- Generate `token_positions` inside the block from the **actual** input sequence length, usually `in_features.shape[-2]`, and pass it to MHA with RoPE. If positions are omitted, RoPE may be skipped; position 0 can still match because angle 0 leaves Q/K unchanged, while later positions mismatch the snapshot.
- Put generated `token_positions` on `in_features.device`; shape `(1, seq)` broadcasts cleanly over batch/head dimensions.
- Use `max_seq_len/context_length` as the RoPE maximum, but do not confuse it with the actual current sequence length.
- Use `eps=1e-5` consistently with earlier RMSNorm tests unless the adapter/test specifies otherwise.

### Full Transformer LM forward

Flow:

```text
in_indices
  -> token embedding
  -> repeated TransformerBlock layers
  -> final RMSNorm
  -> LM head
  -> logits
```

State-dict handling:

- Top-level keys include `token_embeddings.weight`, `ln_final.weight`, and `lm_head.weight`.
- For each layer `i`, extract keys under `layers.{i}.` and strip that prefix before calling `run_transformer_block`.
- Use `ln_final.weight` for final norm; do not guess `norm.weight`.
- Use the separate `lm_head.weight` for output projection; do not assume weight tying with token embeddings unless the test explicitly says so.

Truncated/short input pitfall:

- Build causal masks and RoPE positions from `in_indices.shape[-1]` / hidden state sequence length, not from fixed `context_length`. Passing short inputs should naturally produce logits for the short sequence.

## Training-side utilities checklist

Use this after model-side utilities/components pass and the user moves to CS336 Assignment 1 training-side work. Treat these as TDD targets around optimizer state and serialization rather than model forward math.

### Recommended order

```text
1. run_get_lr_cosine_schedule
2. get_adamw_cls / AdamW
3. run_save_checkpoint + run_load_checkpoint
```

Rationale:

- LR schedule is a pure function and gives the fastest first green test.
- AdamW is the main conceptual target because it introduces optimizer state.
- Checkpointing should come after AdamW because the serialization test compares optimizer `state_dict()` contents.

### Cosine schedule with warmup

Expected piecewise behavior:

```text
it < warmup_iters:
  lr = it / warmup_iters * max_learning_rate

warmup_iters <= it <= cosine_cycle_iters:
  progress = (it - warmup_iters) / (cosine_cycle_iters - warmup_iters)
  lr = min_learning_rate + 0.5 * (max_learning_rate - min_learning_rate) * (1 + cos(pi * progress))

it > cosine_cycle_iters:
  lr = min_learning_rate
```

Pitfalls:

- `it == warmup_iters` should return `max_learning_rate`, not continue the warmup branch.
- `it == cosine_cycle_iters` should return `min_learning_rate`.
- Use the actual test's `warmup_iters` and `cosine_cycle_iters` semantics; do not assume `cosine_cycle_iters` is a duration if the public test treats it as an absolute iteration boundary.

### AdamW optimizer

`get_adamw_cls()` should return a `torch.optim.Optimizer` subclass or compatible class. For each parameter with a gradient, maintain:

```text
step
exp_avg
exp_avg_sq
```

Core update:

```text
m = beta1 * m + (1 - beta1) * grad
v = beta2 * v + (1 - beta2) * grad**2
m_hat = m / (1 - beta1**step)
v_hat = v / (1 - beta2**step)
p = p - lr * m_hat / (sqrt(v_hat) + eps)
p = p - lr * weight_decay * p
```

Pitfalls:

- AdamW uses decoupled weight decay; do not add weight decay into the gradient.
- Skip parameters whose `grad is None`.
- Initialize moment tensors with `torch.zeros_like(p)` on the parameter's device/dtype.
- Perform parameter mutation under `torch.no_grad()` or via safe in-place `.data`-free patterns.
- The public test accepts either PyTorch AdamW-equivalent behavior or the course reference snapshot, so matching PyTorch AdamW is a valid target.

### Checkpointing

Save at least:

```text
model_state_dict
optimizer_state_dict
iteration
```

Typical flow:

```text
torch.save({...}, out)
checkpoint = torch.load(src)
model.load_state_dict(checkpoint[...])
optimizer.load_state_dict(checkpoint[...])
return checkpoint["iteration"]
```

Pitfalls:

- `out` and `src` may be path-like objects or file-like binary objects; `torch.save` and `torch.load` support both.
- Save and restore the optimizer state, not only the model.
- Return the serialized iteration as an `int`; the serialization test compares it exactly.
- Checkpoint tests often compare optimizer `param_groups` and per-parameter state keys, so use `optimizer.state_dict()` / `load_state_dict()` directly rather than reconstructing state manually.

## Useful checks

- RoPE output shape equals input shape.
- Position 0 is unchanged because angle is zero.
- `test_swiglu` should be isolated before `test_rope`.
- After RoPE passes, move to `run_scaled_dot_product_attention`.
- After SDPA and 4D SDPA pass, move to ordinary MHA, then MHA with RoPE.
