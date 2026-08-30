# Assignment 2 Sharded Optimizer Implementation

Use this reference when the user reaches the sharded optimizer section of Assignment 2.

## Requirements

Implement a sharded optimizer that:
1. Shards optimizer state across ranks (each rank manages 1/world_size of parameters)
2. Works with FSDP-sharded parameters
3. Supports any base optimizer class (AdamW, SGD, etc.)

## Interface

```python
def get_sharded_optimizer(params, optimizer_cls: type[torch.optim.Optimizer], **kwargs) -> torch.optim.Optimizer:
    """Returns a sharded optimizer wrapping optimizer_cls."""
    ...
```

## Implementation Strategy

### Key Components

1. **Parameter Sharding**: Same as FSDP — each rank gets 1/world_size of each parameter
2. **Optimizer State Sharding**: Each rank only maintains optimizer state for its local shards
3. **State Dict Handling**: `state_dict()` and `load_state_dict()` must handle sharded state
4. **Step Synchronization**: All ranks must step together (barrier or implicit sync via all-reduce)

### Core Implementation Pattern

```python
import torch
import torch.distributed as dist

class ShardedOptimizer(torch.optim.Optimizer):
    def __init__(self, params, optimizer_cls, **kwargs):
        # Shard parameters across ranks
        self.world_size = dist.get_world_size()
        self.rank = dist.get_rank()
        
        # Flatten all parameters
        self.param_groups = []
        self._param_to_shard = {}
        
        for param in params:
            if param is None:
                continue
            
            # Flatten and shard
            flat_param = param.view(-1)
            total_size = flat_param.numel()
            shard_size = total_size // self.world_size
            start = self.rank * shard_size
            end = start + shard_size if self.rank < self.world_size - 1 else total_size
            
            shard = flat_param[start:end]
            
            # Create a new parameter for the shard
            shard_param = torch.nn.Parameter(shard)
            shard_param.grad = param.grad[start:end] if param.grad is not None else None
            
            self._param_to_shard[param] = shard_param
            self.param_groups.append({'params': [shard_param]})
        
        # Initialize base optimizer with sharded parameters
        self.base_optimizer = optimizer_cls(
            [p for group in self.param_groups for p in group['params']],
            **kwargs
        )
    
    def step(self, closure=None):
        """Perform a single optimization step."""
        # Update sharded parameters
        loss = self.base_optimizer.step(closure)
        
        # Synchronize: all-gather updated parameters back to full parameters
        for param, shard_param in self._param_to_shard.items():
            # All-gather shard to full parameter
            flat_shard = shard_param.view(-1)
            total_size = param.numel()
            shard_size = total_size // self.world_size
            
            # Gather from all ranks
            gathered = [torch.empty(shard_size, device=param.device, dtype=param.dtype) 
                        for _ in range(self.world_size)]
            gathered[self.rank] = flat_shard
            dist.all_gather(gathered, flat_shard)
            
            # Update full parameter
            param.data = torch.cat(gathered).view(param.shape)
        
        return loss
    
    def zero_grad(self, set_to_none=False):
        """Zero gradients."""
        self.base_optimizer.zero_grad(set_to_none)
    
    def state_dict(self):
        """Return optimizer state dict (sharded)."""
        return self.base_optimizer.state_dict()
    
    def load_state_dict(self, state_dict):
        """Load optimizer state dict (sharded)."""
        self.base_optimizer.load_state_dict(state_dict)
```

## Critical Pitfalls

### Parameter-Shard Mapping

Maintain a clear mapping between original parameters and their shards. This is needed for:
1. `step()`: updating full parameters after shard optimization
2. `zero_grad()`: clearing gradients on the right tensors
3. `state_dict()`: saving/loading sharded state

### Gradient Sharding

Gradients must be sharded consistently with parameters. If FSDP already shards gradients, the sharded optimizer should use those sharded gradients directly.

### All-Gather After Step

After each optimizer step, updated shards must be all-gathered back to full parameters before the next forward pass. This can be done:
1. Explicitly in `step()`
2. Lazily before next forward
3. Via hooks

### Memory Efficiency

The main benefit of sharded optimizer is reducing optimizer state memory (e.g., Adam's momentum and variance buffers). Ensure:
1. Each rank only stores state for its shards
2. Full parameters are not kept in optimizer state
3. Temporary all-gather buffers are freed promptly

### Compatibility with FSDP

Sharded optimizer is designed to work with FSDP. The typical flow:
1. FSDP shards parameters and all-gathers for forward
2. Backward computes full gradients
3. FSDP reduce-scatters gradients to shards
4. Sharded optimizer updates shard parameters
5. FSDP all-gathers updated parameters for next forward

## Test Expectations

Tests will likely:
1. Initialize a model with FSDP
2. Create a sharded optimizer wrapping AdamW
3. Run a training step
4. Verify optimizer state is sharded (each rank has 1/world_size of state)
5. Verify parameters are updated correctly after step
6. Test state_dict/load_state_dict round-trip

## Common Debugging Patterns

```python
# Verify optimizer state sharding
for group in optimizer.param_groups:
    for p in group['params']:
        state = optimizer.state[p]
        print(f"Rank {dist.get_rank()} param shape: {p.shape}")
        if 'exp_avg' in state:
            print(f"  exp_avg shape: {state['exp_avg'].shape}")

# Verify all ranks have consistent parameters after step
dist.barrier()
for name, param in model.named_parameters():
    param_sum = param.data.clone()
    dist.all_reduce(param_sum, op=dist.ReduceOp.SUM)
    if dist.get_rank() == 0:
        print(f"{name} consistent: {torch.allclose(param_sum / dist.get_world_size(), param.data)}")
```
