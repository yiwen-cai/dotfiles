# Tiny Training Sanity Run for CS336 Assignment 1

Use this when the user has completed Assignment 1 model/training utilities and wants to verify that the pieces form a runnable training path. This is a learning/debugging sanity script, not necessarily part of the official submission.

## Goal

Verify the end-to-end chain:

```text
weight init -> registered parameters -> TransformerLM forward -> cross entropy -> backward -> optimizer step -> multi-step finite check -> checkpoint round-trip
```

## Adapter Key Pitfall

CS336 adapters expect dotted keys such as:

```text
layers.0.attn.q_proj.weight
layers.0.ffn.w1.weight
token_embeddings.weight
ln_final.weight
lm_head.weight
```

Do not put these keys directly into `nn.ParameterDict`: PyTorch parameter names cannot contain `.`.

Recommended pattern for a lightweight sanity model:

```python
raw = init_weight(n_layers, vocab_size, d_model, d_ff)
self.param_names = list(raw.keys())
self.params = torch.nn.ParameterList(
    [torch.nn.Parameter(value) for value in raw.values()]
)
```

Then reconstruct the adapter weight dict in `forward`:

```python
weights = dict(zip(self.param_names, self.params))
```

`model.parameters()` still works because `nn.ParameterList` registers all contained parameters. Optimizers do not need semantic names; they hold references to the actual parameter objects and read gradients from each object's `.grad` field after `loss.backward()`.

## Prefix Pitfall

If using a layer prefix, avoid double dots:

```python
layer_prefix = f"layers.{i}"
state_dict[f"{layer_prefix}.attn.q_proj.weight"] = ...
```

This is correct. The following creates keys like `layers.0..attn.q_proj.weight` and causes `KeyError: 'attn.q_proj.weight'` inside `run_transformer_block`:

```python
layer_prefix = f"layers.{i}."
state_dict[f"{layer_prefix}.attn.q_proj.weight"] = ...
```

## Minimal Verification Sequence

1. Forward shape and finite logits:

```text
logits.shape == (batch_size, sequence_length, vocab_size)
torch.isfinite(logits).all() == True
```

2. Loss/backward:

```text
loss finite == True
params with grad == total params
```

3. Optimizer step:

```text
optimizer.step() does not error
at least one parameter changes; for the assignment tiny setup, 30/30 changed
next forward remains finite
```

4. Multi-step sanity train:

```text
Run 1-5 random-token steps and check every loss is finite.
Random inputs/targets do not need monotonic loss decrease.
```

5. Checkpoint round-trip:

```text
train one step -> save checkpoint -> create fresh model/optimizer -> load checkpoint
restored_iteration == saved_iteration
all corresponding parameters are torch.allclose
```

## Notes for TA-Style Guidance

For CS336 coursework, guide the user step by step. Ask them to run the smallest next verification and report real output. Avoid dumping a full graded solution; give focused snippets for debugging the current failure and explain shape/key contracts explicitly.
