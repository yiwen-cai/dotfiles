# CS336 Tensor Shape, Broadcasting, and Loss-Function Coaching Notes

Use this reference when coaching the user through CS336 Assignment 1 model-side components, especially after Lecture 2 when questions are about tensor shapes, broadcasting, `jaxtyping`, `einsum`, `einops`, softmax, cross entropy, and data batch construction. Keep TA-style boundaries: explain concepts, review user snippets, and suggest shape checks; do not write complete graded implementations.

## Jaxtyping is documentation/checking, not execution

`jaxtyping` annotations such as:

```python
Float[Tensor, " ... d_in"]
Float[Tensor, " d_out d_in"]
```

describe expected dtype and shape, but they do not automatically align dimensions or alter PyTorch semantics. PyTorch operations still follow broadcasting, matmul, indexing, and reshape rules. Emphasize that dimension names in annotations are a contract for the human and optional type tooling, not named-dimension execution.

## Broadcasting pitfalls for add/subtract

For add/subtract, PyTorch aligns dimensions by position from the right, not by semantic name.

Common safe patterns:

- `(batch, vocab) - (batch, 1)` broadcasts over vocab.
- `(batch, seq, d_model) + (d_model,)` broadcasts over the final model dimension.
- `(batch, seq, d_model) + (seq,)` is usually wrong; reshape to `(1, seq, 1)` first.
- `(batch, heads, query, key) + (query, key)` is often valid for a shared attention mask.
- `(batch, heads, query, key) + (batch, query, key)` is usually wrong unless reshaped to `(batch, 1, query, key)`.

When reviewing snippets, ask for a shape table before suggesting fixes:

```text
A shape:
B shape:
Which semantic dimension should B align to?
What shape must B have for right-aligned broadcasting?
```

## Choosing dimension tools

Use this rule of thumb:

| Need | Preferred tool |
|---|---|
| Remove a length-1 dimension | `squeeze(dim)` |
| Add a length-1 dimension | `unsqueeze(dim)` or indexing with `None` |
| Preserve a reduced dimension for broadcasting | `keepdim=True` |
| Flatten or reshape by size | `reshape` |
| Swap/reorder raw dimensions | `transpose` / `permute` |
| Readable split/merge/reorder | `einops.rearrange` |
| Multiplication plus summation over named axes | `torch.einsum` / `einops.einsum` |
| Plain add/subtract | normal `+` / `-` after explicit reshape/broadcast alignment |

Do not force `einops` into simple loss functions where `keepdim=True` and `squeeze(-1)` are clearer. Save `einops.rearrange` for split heads, merge heads, flatten batch/sequence, RoPE pair reshaping, and mask dimension insertion.

## Einops syntax pitfall

`einops` patterns separate axes with spaces, not commas.

Correct:

```python
rearrange(x, "b -> b 1")
rearrange(x, "b 1 -> b")
```

Incorrect:

```python
rearrange(x, "b -> b, 1")
rearrange(x, "b, 1 -> b")
```

If the user gets `EinopsError: Unknown character ','`, point to this immediately.

## Einsum mental model

For `torch.einsum`, use short single-letter axis labels. Repeated input axes not present in the output are summed; elements at matching indices are multiplied first. It is not a general add/subtract expression language.

Examples to teach:

```python
# Linear: (..., d_in) and (d_out, d_in) -> (..., d_out)
torch.einsum("...i,oi->...o", x, w)

# Attention scores: (b,h,q,d) and (b,h,k,d) -> (b,h,q,k)
torch.einsum("bhqd,bhkd->bhqk", q, k)

# Attention value aggregation: (b,h,q,k) and (b,h,k,d) -> (b,h,q,d)
torch.einsum("bhqk,bhkd->bhqd", attn, v)
```

If the user wants long axis names, mention `einops.einsum` as an optional readability tool, but keep PyTorch `einsum` as the default because it is universal.

## Cross entropy coaching points

For CS336 `run_cross_entropy`, the adapter contract is:

```text
inputs:  (batch_size, vocab_size) float logits
targets: (batch_size,) integer class indices
return:  scalar mean loss
```

Core formula:

```text
loss_i = logsumexp(inputs[i]) - inputs[i, targets[i]]
loss = mean_i(loss_i)
```

Stable logsumexp:

```text
m = max(logits)
logsumexp = m + log(sum(exp(logits - m)))
```

Common pitfalls observed:

1. Subtracting `targets` directly. `targets` are class indices, not target logits. The code must subtract `inputs[i, targets[i]]` or a vectorized equivalent.
2. Broadcasting `(batch, 1) - (batch,)` accidentally creates `(batch, batch)`. Align both tensors to `(batch,)` or both to `(batch, 1)` before subtraction.
3. Calling `torch.squeeze(x, -1)` without assignment. It returns a new tensor and does not mutate `x` in place.
4. Returning `torch.mean(losses, -1)` when `losses` is `(batch, 1)` produces `(batch,)`, not a scalar. Mean over all examples for the final scalar.
5. Creating temporary tensors with default CPU/device/dtype. Prefer `dtype=inputs.dtype, device=inputs.device` or vectorized indexing that avoids manual allocation.
6. In-place loop assignment can pass tests but is less idiomatic than vectorized row indexing. It is acceptable for learning, but later coach toward vectorized `target_logits = inputs[row_indices, targets]`.

Recommended shape table for review:

```text
inputs:           (batch_size, vocab_size)
targets:          (batch_size,)
m:                (batch_size, 1)
logsumexp:        (batch_size,)
target_logits:    (batch_size,)
loss_per_example: (batch_size,)
loss:             ()
```

## Get-batch setup reminder

For `run_get_batch`, the public test expects:

```text
dataset: 1D numpy array of token IDs
x.shape == y.shape == (batch_size, context_length)
y == x + 1 for the toy np.arange dataset
valid starts: 0 <= start <= len(dataset) - context_length - 1
x/y dtype: torch long / integer tensor
x/y device: requested device
```

Explain that `torch.from_numpy(dataset).to(device=device, dtype=torch.long)` or `torch.tensor(..., dtype=torch.long, device=device)` are common conversion patterns. For newly initialized tensors, specify both dtype and device.
