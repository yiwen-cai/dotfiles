# CS336 Stage 1-2 Shape and Indexing Pitfalls

Session-derived coaching notes for CS336 Assignment 1 model-side work. Use as a reference when guiding `softmax`, `cross_entropy`, `get_batch`, and the first basic layers.

## Cross entropy

Target tensor semantics:

- `inputs.shape == (batch_size, vocab_size)` contains logits.
- `targets.shape == (batch_size,)` contains class indices, not logit values.
- The per-example target logit is `inputs[i, targets[i]]`.

Vectorized target-logit selection:

```python
row_indices = torch.arange(batch_size, device=inputs.device)
target_logits = inputs[row_indices, targets]
```

Explain that advanced indexing pairs the two index tensors elementwise:

```text
output[i] = inputs[row_indices[i], targets[i]] = inputs[i, targets[i]]
```

Pitfalls:

- `logsumexp - targets` is wrong because `targets` are indices, not logits.
- `inputs[:, targets]` is wrong for CE target selection; it selects all requested columns for every row and usually returns a 2D tensor.
- `(batch_size, 1) - (batch_size,)` broadcasts to `(batch_size, batch_size)`; make both tensors `(batch_size,)` or both `(batch_size, 1)` before subtraction.
- `torch.squeeze(x, dim)` is not in-place; assign its return value if using it.
- Prefer `keepdim=True` during reductions used for broadcasting, then explicitly `squeeze(-1)` after the broadcast-sensitive step.

Stable formula:

```text
loss_i = logsumexp(logits_i) - logits_i[target_i]
logsumexp(x) = max(x) + log(sum(exp(x - max(x))))
```

## `get_batch`

Correct language-modeling semantics:

```text
x = dataset[start : start + context_length]
y = dataset[start + 1 : start + context_length + 1]
```

Pitfalls:

- `y` is the next-position token sequence, not numerically `x + 1`. `np.arange` tests can hide this distinction.
- For a 1D numpy dataset, use slice syntax with `:`; `dataset[start + 1, start + 1 + context_length]` is 2D indexing and is invalid.
- Return a 2-tuple `(x_batch, y_batch)`, not `batch_size` tuples of `(x_i, y_i)`.
- Final shapes must be `(batch_size, context_length)` for both `x` and `y`.
- Preserve the requested device and use integer token dtype, typically `torch.long`.
- If slicing numpy arrays, keep start indices as Python/numpy integers rather than torch scalar tensors when possible.

## `einops` / dimension manipulation

- `einops.rearrange` patterns use spaces, not commas: `"b -> b 1"`, not `"b -> b, 1"`.
- Do not force `einops` into simple reduction/broadcasting cases where `keepdim=True`, `squeeze`, or `unsqueeze` are clearer.
- `einops` is especially useful later for head split/merge patterns such as `"b s (h d) -> b h s d"`.

## Basic layer Day 6 ordering

After Stage 1 (`softmax`, `cross_entropy`, `get_batch`) is green, guide the user through Stage 2 in this order:

```text
run_linear -> run_embedding -> run_silu -> run_rmsnorm -> run_gradient_clipping
```

First target, `run_linear`:

```text
weights:     (d_out, d_in)
in_features: (..., d_in)
output:      (..., d_out)
output[..., o] = sum_i in_features[..., i] * weights[o, i]
```

Use either `in_features @ weights.T` or the einsum interpretation `"...i,oi->...o"`. Remind the user there is no bias in the adapter.
