# Triton Kernel Numerical Harness Template

Use this as a copy-and-adapt starting point for focused Triton kernel checks. Keep it outside the project source tree for review-only/coursework contexts.

```python
import math
import torch


def cdiv(a, b):
    return (a + b - 1) // b


def reference(*inputs):
    # Build an independent PyTorch/autograd reference, not a rewrite of the Triton kernel.
    raise NotImplementedError


def launch_kernel(*inputs, meta):
    # Allocate outputs, call kernel[(grid, ...)](..., **meta), synchronize, and return outputs.
    raise NotImplementedError


def check_case(name, shape, meta, atol=1e-2, rtol=1e-2):
    torch.manual_seed(abs(hash((name, shape, tuple(sorted(meta.items()))))) % (2**31))
    # Create tensors for the target shape.
    # expected = reference(...)
    # actual = launch_kernel(..., meta=meta)
    # For each output tensor:
    #   diff = (actual - expected).abs()
    #   print max_abs, mean_abs, torch.allclose(...)
    #   raise AssertionError(name) on failure.
    raise NotImplementedError


def main():
    cases = [
        ("single_token", ...),
        ("default_shape", ...),
        ("q_shorter_than_k", ...),
        ("q_longer_than_k", ...),
        ("q_tail_only", ...),
        ("k_tail_only", ...),
        ("both_tail", ...),
    ]
    for is_causal in (False, True):
        for name, shape in cases:
            check_case(name, shape, {"is_causal": is_causal})
    print("SUMMARY: all focused Triton kernel tests passed")


if __name__ == "__main__":
    main()
```

Notes:
- Test at least one nonstandard but legal tile configuration.
- For `tl.dot`, keep the reduction dimension at least 16 unless the target backend explicitly supports smaller values.
- Report the first real compiler/runtime error separately from numerical mismatches.
