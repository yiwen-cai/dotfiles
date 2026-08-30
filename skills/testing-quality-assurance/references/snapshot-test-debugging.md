# Debugging Snapshot Test Failures in ML/Model Component Testing

## When Your Code is Logically Correct but the Snapshot Fails

A common pattern in model-component assignments and ML libraries: your implementation of a function (e.g., SwiGLU, RMSNorm) is correct by independent verification — einsum patterns check out, @-operator comparison matches — but a `numpy_snapshot.assert_match(actual_output, atol=1e-5)` fails with 100% mismatched elements.

## Systematic Debugging Flow

### Phase 1: Verify the Implementation Independently

Before assuming the snapshot is wrong, eliminate implementation errors:

```python
# Compare multiple equivalent implementations
import torch
from einops import einsum as e_einsum

# Method A: einsum (the implementation under test)
o1 = e_einsum(a, b, '... i, j i -> ... j')

# Method B: @ operator (verification)
o2 = a @ b.T

# Method C: torch.einsum
o3 = torch.einsum('...i,ji->...j', a, b)

# If all agree, the compute is correct
assert torch.allclose(o1, o2)  # → passes means the formula is right
```

If methods A, B, C all match each other but not the snapshot, the issue is NOT in how you wrote the computation — move to Phase 2.

### Phase 2: Check Snapshot Metadata

```bash
# When was the snapshot created? Same day as fixtures?
stat tests/_snapshots/test_component.npz
stat tests/fixtures/ts_tests/model.pt
```

If snapshot and fixtures share the same creation date, they were generated together and are consistent. If dates differ, a fixture may have been regenerated without updating the snapshot.

### Phase 3: Cross-Reference Against Reference Implementations

Some tests offer two acceptance paths:

```python
# Test: match PyTorch reference OR match snapshot
matches_pytorch = torch.allclose(actual_weights, pytorch_weights, atol=1e-4)
if matches_pytorch:
    return  # Early exit — our implementation is correct by PyTorch standard
numpy_snapshot.assert_match(actual_weights, atol=1e-4)
```

If the test allows matching PyTorch's reference as an alternative, returning the PyTorch implementation directly (`torch.optim.AdamW`, `torch.nn.functional.silu`, etc.) is valid.

### Phase 4: Verify Fixture Consistency

Reproduce the test's exact fixture values:

```python
# Instead of calling fixtures directly (which pytest forbids),
# manually load the state dict
state = torch.load('tests/fixtures/ts_tests/model.pt', map_location='cpu', weights_only=True)
w1 = state['layers.0.ffn.w1.weight']  # match adapter parameter names
```

Then check:
- Are the tensor shapes what the adapter signature expects?
- Is the seed/random state reproducing the same input?
- Are there any `_orig_mod.` prefix strips or key renames?

```python
# Common fixture cleanup pattern
state_dict = {k.replace('_orig_mod.', ''): v for k, v in state_dict.items()}
```

### Phase 5: Check Model Design Differences

Some model designs differ across implementations of the same name:

| Variant | Gate formula | Original source |
|---------|-------------|-----------------|
| SwiGLU (LLaMA) | `SiLU(gate_proj(x)) * up_proj(x)` | LLaMA paper |
| SwiGLU (PaLM) | `SiLU(x @ W) * (x @ V)` | Noam Shazeer 2020 |

These are mathematically equivalent up to weight name mapping. If the snapshot was generated with a different naming convention (w1=gate vs w1=up), the same math still produces the same result — but it's worth verifying the weight-to-role mapping.

## Root Causes to Suspect

| Symptom | Likely Cause |
|---------|-------------|
| 100% mismatch, wrong values | Compute logic error (Phase 1) |
| 100% mismatch, correct logic | Fixture/snapshot mismatch (Phase 2-4) |
| ~50% mismatch values close | Seed / random state divergence (Phase 4) |
| Batch-dependent mismatch | Leading-dimension broadcast issue |
| Small % mismatch within tolerance | Floating-point accumulation differences (acceptable) |

## When to Accept the Snapshot

If after Phase 1-4 the implementation is verified correct against multiple independent methods and the fixtures are consistent, the snapshot may have been generated with a different (but also correct) implementation detail — e.g., different floating-point operation ordering. In a homework context, you may need to match the snapshot exactly by adjusting implementation details.
