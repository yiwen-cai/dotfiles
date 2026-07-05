# Weight Initialization & Tiny Training Sanity Run

## Weight Dict Structure (3‑layer TinyStories model)

30 keys total; d_model=64, d_ff=128, vocab_size=10000 or 256 for toys:

### Top-level (3 keys)
```
token_embeddings.weight    (vocab_size, d_model)
ln_final.weight            (d_model,)
lm_head.weight             (vocab_size, d_model)
```

### Per layer (9 keys × n_layers)
```
layers.{i}.attn.q_proj.weight       (d_model, d_model)    # fan_in = d_model
layers.{i}.attn.k_proj.weight       (d_model, d_model)
layers.{i}.attn.v_proj.weight       (d_model, d_model)
layers.{i}.attn.output_proj.weight  (d_model, d_model)
layers.{i}.ffn.w1.weight            (d_ff, d_model)       # fan_in = d_model
layers.{i}.ffn.w3.weight            (d_ff, d_model)
layers.{i}.ffn.w2.weight            (d_model, d_ff)       # fan_in = d_ff
layers.{i}.ln1.weight               (d_model,)            # RMSNorm
layers.{i}.ln2.weight               (d_model,)
```

## Weight Initialization Formulas

| Component | Initialization | std formula |
|-----------|---------------|-------------|
| RMSNorm (`ln1`, `ln2`, `ln_final`) | `torch.ones(shape)` | N/A |
| Token embedding + LM head | `randn * std` | `1 / sqrt(d_model)` |
| Q/K/V/Output proj (square) | `randn * std` | `1 / sqrt(d_model)` |
| W1/W3 (d_ff × d_model) | `randn * std` | `1 / sqrt(d_model)` |
| W2 (d_model × d_ff) | `randn * std` | `1 / sqrt(d_ff)` |

Rationale: after embedding, input vectors have expected L2 norm ~1 when
`std = 1/sqrt(d_model)`. This prevents signal explosion/shrinkage through
a few layers.

## nn.ParameterDict Limitation

`nn.ParameterDict` does NOT accept keys containing "." — PyTorch treats
"." as a parameter-path separator and raises `KeyError`.

**Workaround: `nn.ParameterList` + name list**

```python
class TinyLM(nn.Module):
    def __init__(self, weight_dict: dict):
        super().__init__()
        self.param_names = list(weight_dict.keys())
        self.params = nn.ParameterList([
            nn.Parameter(v) for v in weight_dict.values()
        ])

    def forward(self, input_ids):
        weight_dict = dict(zip(self.param_names, self.params))
        # ... pass to run_transformer_lm
```

- `model.parameters()` traverses into `nn.ParameterList` automatically
- Optimizer accepts `model.parameters()` directly — no name needed
- Forward reconstructs the weight dict via `zip(names, params)`

## Adapter Functions Used in Training

| Function | Purpose | Key parameters |
|----------|---------|----------------|
| `run_transformer_lm(weights, in_indices)` | Forward → logits | Returns `(B, S, V)` |
| `run_cross_entropy(logits, targets)` | Loss | Returns scalar, handles reshape internally |
| `get_adamw_cls()` | Optimizer class | Returns AdamW subclass |
| `run_get_lr_cosine_schedule(it, ...)` | LR for step | Returns float |
| `run_save_checkpoint(model, optimizer, it, path)` | State persistence | 3‑part: model + optimizer + iteration |
| `run_load_checkpoint(path, model, optimizer)` | State restoration | Returns iteration |

## Training Loop Shape Contract

```
x: (batch, seq_len) — token ids
y: (batch, seq_len) — next‑token targets (offset by 1)

logits = model(x)                                 # (B, S, V)
loss   = run_cross_entropy(logits, y)             # scalar
        └─ internally does logits.view(-1, V), targets.view(-1)

loss.backward()
optimizer.step()
```

## Verification Checklist (before training)

- [ ] `logits.shape == (batch, seq_len, vocab_size)`
- [ ] `torch.all(torch.isfinite(logits)).item()` → True
- [ ] Not all logits are identical (use `logits[0, 0, :5]` to spot-check)
- [ ] `loss` is finite after first forward
- [ ] At least one parameter has non‑None `.grad` after backward
- [ ] Parameter values change after `optimizer.step()`
- [ ] Checkpoint save → load → iteration matches
