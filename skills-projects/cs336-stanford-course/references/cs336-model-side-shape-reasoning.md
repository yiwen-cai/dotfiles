# CS336 Model-Side Shape Reasoning Reference

Use this reference when coaching CS336 Assignment 1 model-side implementation after tokenizer completion. It captures session-specific guidance for jaxtyping annotations, PyTorch broadcasting, `einsum`, `einops`, and the first numerical utilities.

## TA-safe boundary

The CS336 repo guidance requires TA-style help. Do not implement core model components for the user or edit graded code. Use this reference to explain concepts, review snippets, and suggest tests/invariants.

## jaxtyping annotations

`tests/adapters.py` imports:

```python
from jaxtyping import Bool, Float, Int
from torch import Tensor
```

Examples:

```python
Float[Tensor, " d_out d_in"]
Float[Tensor, " ... d_in"]
Int[Tensor, " batch_size"]
Float[Tensor, ""]
```

Interpretation:

- `Float[Tensor, " d_out d_in"]`: floating PyTorch tensor with shape `(d_out, d_in)`.
- `Float[Tensor, " ... d_in"]`: arbitrary leading dimensions, last dimension `d_in`.
- `Int[Tensor, " batch_size"]`: integer tensor shape `(batch_size,)`.
- `Float[Tensor, ""]`: scalar tensor.

These annotations document dtype and shape contracts. Unless paired with runtime checkers such as `jaxtyped` and `beartype`, they do not enforce shapes at runtime and do not affect PyTorch computation.

## No automatic dimension alignment

jaxtyping names are not used by PyTorch, `torch.einsum`, or `einops`. PyTorch aligns dimensions by positional broadcasting rules, not semantic names.

Example pitfall:

```text
x:       (batch, seq, d_model)
y:       (batch, d_model)
x + y -> PyTorch tries to align seq with batch from the right.
```

Correct semantic broadcasting often requires reshaping to `(batch, 1, d_model)`.

## `einsum`: computation with contraction

PyTorch `torch.einsum` uses single-character local dimension labels. Labels are local to the equation and do not bind to jaxtyping names.

Core rule:

```text
Input elements with the same index are multiplied; any label that appears in inputs but not in the output is summed over.
```

Examples:

```python
torch.einsum("i,i->", x, y)          # dot product: sum_i x_i * y_i
torch.einsum("i,i->i", x, y)         # elementwise product
torch.einsum("ij->i", x)             # sum over j
torch.einsum("ij->ji", x)            # transpose
torch.einsum("mn,np->mp", a, b)      # matrix multiply
torch.einsum("...i,oi->...o", x, w)  # linear with weight shape (out, in)
torch.einsum("bhqd,bhkd->bhqk", q, k) # attention scores
torch.einsum("bhqk,bhkd->bhqd", a, v) # attention weighted value sum
```

For readable long dimension names, `einops.einsum` can be used if available:

```python
from einops import einsum

out = einsum(x, w, "... d_in, d_out d_in -> ... d_out")
```

Do not use `einsum` for ordinary addition; use normal PyTorch operators for `x + y` and basic broadcasting.

## `einops`: shape manipulation

Use `einops.rearrange`, `reduce`, and `repeat` for reshaping, transposing, splitting, merging, and repeating dimensions.

Common CS336 patterns:

```python
from einops import rearrange, reduce, repeat

# split model dimension into heads
rearrange(x, "b s (h d) -> b h s d", h=num_heads)

# merge heads back
rearrange(x, "b h s d -> b s (h d)")

# flatten batch and sequence before CE
rearrange(logits, "b s v -> (b s) v")

# transpose-like reorder
rearrange(x, "b s d -> b d s")

# reduce over last dim
reduce(x, "b s d -> b s", "mean")
```

Important: `einops` patterns are explicit; they do not read jaxtyping annotations.

## Stage 1 numerical utilities

After tokenizer, start model-side TDD with pure functions/data utilities:

1. `run_softmax`
2. `run_cross_entropy`
3. `run_get_batch`

### Softmax invariant

For arbitrary input and chosen `dim`:

```text
output.shape == input.shape
output.sum(dim) ≈ 1
softmax(x + constant along dim) == softmax(x)
```

Stable method:

```text
max_along_dim = max(input, dim, keepdim=True)
exp_shifted = exp(input - max_along_dim)
denominator = sum(exp_shifted, dim, keepdim=True)
output = exp_shifted / denominator
```

The user's softmax snippet using `torch.amax(..., keepdim=True)`, `torch.exp`, `torch.sum(..., keepdim=True)`, and division passed `test_softmax_matches_pytorch`.

### Cross entropy invariant

Adapter contract:

```text
inputs:  (batch_size, vocab_size)
targets: (batch_size,)
return:  scalar mean loss
```

Stable formula:

```text
loss_i = logsumexp(inputs_i) - target_logit_i
loss = mean_i loss_i
```

Avoid computing `softmax` then `log` directly; tests include large logits (`1000.0 * inputs`). Ensure `logsumexp` and `target_logits` have compatible shape, e.g. both `(batch_size,)`, to avoid accidental `(batch_size, batch_size)` broadcasting.

### get_batch invariant

Given 1D token dataset, `batch_size`, and `context_length`:

```text
x.shape == (batch_size, context_length)
y.shape == (batch_size, context_length)
y == x shifted by one token
start index in [0, len(dataset) - context_length - 1]
```

The last valid start is `len(dataset) - context_length - 1` because labels read one token beyond the input window.
