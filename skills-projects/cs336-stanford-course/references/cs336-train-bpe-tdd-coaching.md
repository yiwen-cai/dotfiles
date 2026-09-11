# CS336 `train_bpe` TDD Coaching Reference

Use this reference when guiding CS336 Assignment 1 BPE training implementation under TA-style constraints. It captures durable debugging checkpoints and self-check outputs from the Day 4 workflow without providing a full pasteable solution.

## Scope and Boundary

- Applies to `run_train_bpe` / `train_bpe` in CS336 Assignment 1.
- Keep TA-safe: explain concepts, suggest invariants, review user snippets, and ask the user to run tests. Do not edit graded solution code or provide a complete implementation.
- Public tests/adapters may be read; core implementation should be written by the user.

## Milestone Sequence

1. **Adapter接通**
   - `run_train_bpe` should call the user's training function.
   - Expected RED changes from `NotImplementedError` to vocab/merges mismatch.

2. **Initial vocab**
   - Verify `0..255 -> bytes([i])`.
   - Append special tokens as UTF-8 bytes starting at id `256`.
   - With `vocab_size=256 + len(special_tokens)`, expect `merges == []`.

3. **`pretoken_counts`**
   - Read corpus, split on special tokens as hard boundaries, discard special-token segments for training statistics.
   - GPT-2 regex pre-tokenize ordinary segments.
   - Key invariant: `Counter[tuple[bytes, ...]]`, not `bytes` or `tuple[str, ...]`.
   - GPT-2 regex includes a leading optional space, so toy text may produce keys like `(b" ", b"l", b"o", b"w")`.

4. **`pair_counts`**
   - Derive from `pretoken_counts`.
   - Each adjacent pair contributes the pre-token frequency, not just `1`.
   - Single-token pre-tokens contribute no pairs.

5. **Best-pair selection**
   - Rule: highest count; ties choose lexicographically greater pair.
   - Debug by comparing `(count, pair)` rather than relying on `Counter.most_common` tie order.

6. **Single merge update**
   - Replace all non-overlapping occurrences of the best pair inside each pre-token.
   - Build a fresh `Counter`; if different old pre-token tuples merge into the same tuple, frequencies must be summed.
   - Key invariant: after merging a pre-token, `b"".join(old_tokens) == b"".join(new_tokens)`.
   - Store `tuple(new_tokens)` as the counter key; list keys are unhashable.
   - Update both `merges` and `vocab` each round.

7. **Full tests**
   - Run `test_train_bpe` first for strict reference `merges` equality.
   - Then run special-token snapshot: ordinary vocab values must not contain `b"<|"`.
   - Then run speed test; optimize only after correctness.

## Useful Debug Outputs

For `pair_counts` after construction:

```text
num pair types: <len(pair_count)>
top 10 pairs:
  <pair> <count>
best_pair: <pair>
best_count: <count>
```

For the classic toy corpus with GPT-2 regex, the first best pair should be:

```text
best_pair: (b's', b't')
best_count: 9
```

After one merge with `vocab_size=258` and one special token:

```text
last vocab: b'st'
merges: [(b's', b't')]
```

After two merges with `vocab_size=259`:

```text
last vocab: b'est'
merges: [(b's', b't'), (b'e', b'st')]
```

## Common Snippet Review Pitfalls

- `counter[key] += 1` on a plain `dict` raises `KeyError`; use `Counter`, `defaultdict(int)`, or explicit default handling.
- `new_pre_token.append(new_pre_token[i])` is wrong in a merge scan; the non-matching branch must preserve the original current token.
- `new_counter[new_pre_token] += frequency` is wrong if `new_pre_token` is a list; convert to tuple before using it as a key.
- Forgetting to append special tokens to vocab causes reference vocab mismatch even though special tokens are discarded from pair statistics.
- `Counter.most_common()` is useful for observation but not sufficient for BPE tie-breaking.
