# Assignment 2 DDP (Distributed Data Parallel) Implementation

Use this reference when the user reaches the DDP section of Assignment 2.

## Requirements

Implement a custom DDP wrapper that:
1. Broadcasts parameters from rank 0 to all other ranks at initialization
2. Synchronizes gradients asynchronously during backward pass (overlapping communication with computation)
3. Each parameter's gradient is individually communicated as soon as it's ready

## Interface

```python
def get_ddp(module: torch.nn.Module) -> torch.nn.Module:
    """Returns a DDP-wrapped module."""
    ...

def ddp_on_after_backward(ddp_model: torch.nn.Module, optimizer: torch.optim.Optimizer):
    """Code to run after backward, before optimizer step."""
    ...
```

## Implementation Strategy

### Key Components

1. **Parameter Broadcasting**: At init, broadcast all parameters from rank 0 to other ranks using `dist.broadcast`
2. **Gradient Hook Registration**: Register post-backward hooks on each parameter to trigger all-reduce when gradient is ready
3. **Async Communication**: Use `dist.all_reduce` with `async_op=True` to overlap communication with computation
4. **Synchronization Point**: In `ddp_on_after_backward`, wait for all pending gradient synchronizations to complete

### Core Implementation Pattern

```python
import torch
import torch.distributed as dist
from torch.distributed import ReduceOp

class DDP(torch.nn.Module):
    def __init__(self, module: torch.nn.Module):
        super().__init__()
        self.module = module
        
        # Broadcast parameters from rank 0
        for param in self.module.parameters():
            dist.broadcast(param.data, src=0)
        
        # Register gradient hooks for async all-reduce
        self._hooks = []
        self._pending_ops = []
        for param in self.module.parameters():
            hook = param.register_post_accumulate_grad_hook(
                lambda p, pending=self._pending_ops: self._grad_hook(p, pending)
            )
            self._hooks.append(hook)
    
    def _grad_hook(self, param, pending_ops):
        """Called when gradient is ready."""
        if param.grad is not None:
            op = dist.all_reduce(param.grad, op=ReduceOp.AVG, async_op=True)
            pending_ops.append(op)
    
    def forward(self, *args, **kwargs):
        return self.module(*args, **kwargs)
    
    def finish_gradient_synchronization(self):
        """Wait for all pending gradient ops."""
        for op in self._pending_ops:
            op.wait()
        self._pending_ops.clear()
```

### Alternative: Using register_hook on tensor

If `register_post_accumulate_grad_hook` is not available, use `param.register_hook`:

```python
def _grad_hook(self, param, pending_ops):
    def hook(grad):
        op = dist.all_reduce(grad, op=ReduceOp.AVG, async_op=True)
        pending_ops.append(op)
        return grad
    return hook

# In __init__:
for param in self.module.parameters():
    param.register_hook(self._grad_hook(param, self._pending_ops))
```

## Critical Pitfalls

### Hook Registration Timing

- Hooks must be registered AFTER parameters are broadcast (so all ranks have the same parameter tensors)
- Hooks must be registered BEFORE any forward pass that will trigger backward

### Gradient Accumulation

If using gradient accumulation (multiple forward/backward before optimizer step), gradients will be accumulated but hooks fire on each backward. Options:
1. Only all-reduce on the final backward of the accumulation cycle
2. Accumulate locally, then all-reduce before optimizer step
3. Use `no_sync()` context manager to disable hooks during accumulation steps

### Average vs Sum

The assignment expects `ReduceOp.AVG` (average gradients across ranks), not `ReduceOp.SUM`. Using SUM would require dividing by world size manually.

### Pending Ops Cleanup

Always clear `self._pending_ops` after waiting, or you'll accumulate handles across steps and memory will grow.

## Test Expectations

Tests will likely:
1. Initialize a model on multiple ranks
2. Wrap with DDP
3. Run forward/backward
4. Verify all ranks have the same gradients
5. Run optimizer step and verify all ranks have the same parameters

## Common Debugging Patterns

```python
# Verify parameters are broadcast correctly
for name, param in model.named_parameters():
    if dist.get_rank() == 0:
        print(f"Rank 0 {name}: {param.data[0, 0]}")
    dist.barrier()
    if dist.get_rank() == 1:
        print(f"Rank 1 {name}: {param.data[0, 0]}")

# Verify gradients are synchronized
loss.backward()
ddp_on_after_backward(ddp_model, optimizer)
for name, param in model.named_parameters():
    if param.grad is not None:
        # All ranks should have identical gradients
        grad_sum = param.grad.clone()
        dist.all_reduce(grad_sum, op=ReduceOp.SUM)
        assert torch.allclose(grad_sum / dist.get_world_size(), param.grad)
```
