# Assignment 2 FSDP (Fully Sharded Data Parallel) Implementation

Use this reference when the user reaches the FSDP section of Assignment 2.

## Requirements

Implement a custom FSDP wrapper that:
1. Shards parameters across ranks (each rank holds 1/world_size of each parameter)
2. All-gathers full parameters for forward and backward passes
3. Reduces and scatters gradients during backward
4. Optionally casts to compute_dtype for communication efficiency

## Interface

```python
def get_fsdp(module: torch.nn.Module, compute_dtype: torch.dtype | None = None) -> torch.nn.Module:
    """Returns an FSDP-wrapped module."""
    ...

def fsdp_on_after_backward(fsdp_model: torch.nn.Module, optimizer: torch.optim.Optimizer):
    """Code to run after backward, before optimizer step."""
    ...

def fsdp_gather_full_params(fsdp_model: torch.nn.Module) -> dict[str, torch.Tensor]:
    """All-gather full parameters for checkpointing or evaluation."""
    ...
```

## Implementation Strategy

### Key Components

1. **Parameter Sharding**: At init, shard each parameter tensor along dimension 0 across ranks
2. **All-Gather for Forward**: Before forward, all-gather full parameters from shards
3. **All-Gather for Backward**: During backward, all-gather full parameters again (or cache from forward)
4. **Reduce-Scatter for Gradients**: After backward, reduce-scatter gradients to match parameter sharding
5. **Compute Dtype**: If provided, cast to compute_dtype before communication, keep master weights in fp32

### Core Implementation Pattern

```python
import torch
import torch.distributed as dist
from torch.distributed import ReduceOp

class FSDP(torch.nn.Module):
    def __init__(self, module: torch.nn.Module, compute_dtype: torch.dtype | None = None):
        super().__init__()
        self.module = module
        self.compute_dtype = compute_dtype
        self.world_size = dist.get_world_size()
        self.rank = dist.get_rank()
        
        # Shard parameters: each rank gets 1/world_size slice
        self._shard_params()
        
        # Register backward hooks for reduce-scatter
        self._register_grad_hooks()
    
    def _shard_params(self):
        """Shard each parameter along dim 0."""
        for name, param in self.module.named_parameters():
            # Flatten parameter
            flat_param = param.data.view(-1)
            
            # Calculate shard size
            total_size = flat_param.numel()
            shard_size = total_size // self.world_size
            start = self.rank * shard_size
            end = start + shard_size if self.rank < self.world_size - 1 else total_size
            
            # Create shard
            shard = flat_param[start:end].clone()
            
            # Replace parameter with shard
            param.data = shard
            
            # Store metadata for all-gather
            param._fsdp_shape = param.shape
            param._fsdp_numel = total_size
    
    def _all_gather_param(self, param):
        """All-gather full parameter from shards."""
        # Calculate sizes for each rank
        total_size = param._fsdp_numel
        shard_size = total_size // self.world_size
        sizes = [shard_size] * (self.world_size - 1) + [
            total_size - shard_size * (self.world_size - 1)
        ]
        
        # All-gather
        gathered = [torch.empty(size, device=param.device, dtype=param.dtype) 
                    for size in sizes]
        dist.all_gather(gathered, param.data)
        
        # Concatenate
        full = torch.cat(gathered)
        return full.view(param._fsdp_shape)
    
    def _register_grad_hooks(self):
        """Register hooks for reduce-scatter gradients."""
        for param in self.module.parameters():
            param.register_post_accumulate_grad_hook(self._grad_hook)
    
    def _grad_hook(self, param):
        """Reduce-scatter gradient."""
        if param.grad is not None:
            # Flatten gradient
            flat_grad = param.grad.view(-1)
            total_size = flat_grad.numel()
            shard_size = total_size // self.world_size
            
            # Reduce-scatter: all ranks contribute full grad, each receives shard
            recv_buffer = torch.empty(shard_size, device=param.device, dtype=param.grad.dtype)
            dist.reduce_scatter_tensor(recv_buffer, flat_grad, op=ReduceOp.AVG)
            
            # Replace gradient with shard
            param.grad = recv_buffer
    
    def forward(self, *args, **kwargs):
        # All-gather full parameters before forward
        for param in self.module.parameters():
            full_param = self._all_gather_param(param)
            param.data = full_param
        
        return self.module(*args, **kwargs)
    
    def finish_gradient_synchronization(self):
        """Wait for any pending ops and clean up."""
        pass  # Hooks are synchronous in this implementation
```

## Critical Pitfalls

### Sharding Dimension

The simplest approach is to flatten each parameter and shard along the flattened dimension. This works for any parameter shape but may not be optimal for communication.

Alternative: Shard along the first dimension for 2D parameters (e.g., shard rows of weight matrices). This preserves more structure but requires per-parameter logic.

### Parameter Restoration After Forward

After forward, parameters are in full form. Before the next forward or for gradient computation, you need to decide:
1. Keep full parameters (more memory, less communication)
2. Re-shard after forward (less memory, more communication)

The assignment likely expects option 2 (re-shard) for true FSDP memory savings.

### Compute Dtype Handling

If `compute_dtype` is provided (e.g., `torch.bfloat16`):
1. Keep master weights in fp32
2. Cast to compute_dtype before all-gather
3. All-gather in compute_dtype (saves bandwidth)
4. Compute in compute_dtype
5. Cast gradients back to fp32 for optimizer

```python
if self.compute_dtype is not None:
    # Cast shard to compute_dtype for communication
    shard = param.data.to(self.compute_dtype)
    # All-gather in compute_dtype
    gathered = [torch.empty(size, device=param.device, dtype=self.compute_dtype) 
                for size in sizes]
    dist.all_gather(gathered, shard)
    full = torch.cat(gathered)
    # Cast back to fp32 for computation
    param.data = full.to(torch.float32)
```

### Gradient Accumulation with Sharded Parameters

If parameters are re-sharded after forward, gradients computed during backward will be for the full parameter. The reduce-scatter in the hook will shard them appropriately.

### Memory Management

FSDP's main benefit is reducing peak memory. Ensure:
1. Parameters are sharded when not in use
2. Full parameters are freed after forward/backward
3. Gradient shards are freed after optimizer step

## Test Expectations

Tests will likely:
1. Initialize a model on multiple ranks
2. Wrap with FSDP
3. Verify each rank has only 1/world_size of each parameter
4. Run forward and verify output is correct
5. Run backward and verify gradients are sharded correctly
6. Run optimizer step and verify parameters are updated
7. Test `gather_full_params` returns full parameters

## Common Debugging Patterns

```python
# Verify parameter sharding
for name, param in model.named_parameters():
    print(f"Rank {dist.get_rank()} {name}: {param.shape} (expected shard)")

# Verify all-gather works
full_params = fsdp_gather_full_params(fsdp_model)
for name, param in full_params.items():
    print(f"Full {name}: {param.shape}")

# Verify gradient sharding
loss.backward()
for name, param in model.named_parameters():
    if param.grad is not None:
        print(f"Rank {dist.get_rank()} {name} grad: {param.grad.shape}")
```
