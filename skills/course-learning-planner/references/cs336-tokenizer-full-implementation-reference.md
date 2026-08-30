# CS336 Tokenizer Full Implementation Reference

This reference captures the complete tokenizer implementation state from Week 3, when all tokenizer-related tests (encode/decode/encode_iterable/train_bpe) passed. It serves as a concrete reference for understanding the full data flow, key design decisions, and common pitfalls without providing a pasteable solution template.

## Final Test Status

```
tests/test_tokenizer.py:  24 passed, 1 xfailed
tests/test_train_bpe.py:   3 passed
Total: 27 passed, 1 xfailed in ~23s
```

The 1 xfailed is `test_encode_memory_usage`, marked by the test framework (not a regression).

## File Locations

- Implementation: `cs336_basics/tokenizer.py` (227 lines at completion)
- Adapter wiring: `tests/adapters.py` (`get_tokenizer` returns `BPETokenizer`, `run_train_bpe` delegates to `train_bpe`)

## Key Data Structures

### Encoding side (BPETokenizer class)

| Field | Type | Purpose |
|-------|------|---------|
| `id_to_bytes` | `dict[int, bytes]` | decode lookup: token ID → byte string |
| `bytes_to_id` | `dict[bytes, int]` | encode lookup: byte string → token ID |
| `merge_rank` | `dict[tuple[bytes, bytes], int]` | merge priority (lower rank = earlier merge) |
| `special_token_to_id` | `dict[str, int]` | special token → ID mapping |

### Training side (train_bpe function)

| Structure | Type | Purpose |
|-----------|------|---------|
| `vocab` | `dict[int, bytes]` | initial 256 byte tokens + special tokens + merge tokens |
| `merges` | `list[tuple[bytes, bytes]]` | ordered merge rules |
| `counter` | `dict[tuple[bytes, ...], int]` | pretoken_counts: compressed corpus frequencies |
| `pair_count` | `dict[tuple[bytes, bytes], int]` | dynamic pair frequency map |

## Critical Design Decisions

1. **GPT-2 regex as compiled module-level constant**
   - Pattern: `'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+`
   - Must use `regex` package (not `re`) for `\p{L}` / `\p{N}` Unicode properties
   - Compiled once at module level for reuse

2. **BYTE_CACHE for zero-allocation byte lookups**
   - `BYTE_CACHE = [bytes([i]) for i in range(256)]`
   - Avoids repeatedly creating `bytes([byte])` during encoding and training

3. **Special token splitting: longest-first + regex.escape**
   - Sort special tokens by length descending, deduplicate
   - Escape each token before joining with `|` for regex compilation
   - This handles overlapping special tokens correctly (e.g., `<|endoftext|>` vs `<|endoftext|><|endoftext|>`)

4. **Merge loop: O(1) rank lookup with min()**
   - `merge_pair = min(valid_pairs, key=lambda k: self.merge_rank[k])`
   - Avoids scanning the full merge list; only considers pairs actually present in the sequence

5. **Training: incremental pair_count updates**
   - Instead of rebuilding `pair_count` from scratch after each merge, only update affected pre-tokens
   - For each pre-token containing the merged pair: subtract old pair frequencies, merge the pair, add new pair frequencies
   - This reduces time complexity from O(N * V) to O(N_affected * L_avg)
   - Essential for passing `test_train_bpe_speed`

## Tie-Breaking Rule

When multiple pairs have equal frequency, select the lexicographically greater pair:

```python
best_pair, _ = max(pair_count.items(), key=lambda item: (item[1], item[0]))
```

This matches the handout requirement and reference implementation.

## Common Pitfalls Observed

- **Unused imports**: `from ast import Dict` and `from torch import Value` were auto-imported by IDE but never used. Should be removed in cleanup.
- **List vs tuple keys**: `counter` keys must be `tuple[bytes, ...]`, not `list[bytes]`. Lists are unhashable.
- **Special token boundary handling**: In training, special tokens split the corpus but their content is excluded from pair statistics. In encoding, they are preserved as atomic units.
- **UTF-8 byte-level encoding**: Multi-byte Unicode characters (e.g., emoji) are split into individual UTF-8 bytes before merge. The merge loop operates on bytes, not characters.

## Adapter Integration

`tests/adapters.py` modifications:
- Import `BPETokenizer` from `cs336_basics`
- `get_tokenizer(vocab, merges, special_tokens)` returns `BPETokenizer(vocab, merges, special_tokens or [])`
- `run_train_bpe(input_path, vocab_size, special_tokens, **kwargs)` delegates to `train_bpe()`

## Next Module Transition

After tokenizer completion, Assignment 1 remaining tests (20 failed):
- `test_data.py` — DataLoader, get_batch
- `test_model.py` — Linear, Embedding, SwiGLU, Attention, Transformer LM, RMSNorm, RoPE
- `test_nn_utils.py` — Softmax, CrossEntropy, Gradient Clipping
- `test_optimizer.py` — AdamW, Cosine LR Schedule
- `test_serialization.py` — Checkpointing

See `references/cs336-model-components-tdd-coaching.md` for the post-tokenizer transition plan.
