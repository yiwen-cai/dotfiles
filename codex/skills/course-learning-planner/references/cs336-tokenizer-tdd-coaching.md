# CS336 Tokenizer TDD Coaching Notes

Use this reference when coaching the user through CS336 Assignment 1 tokenizer work without writing the solution for them.

## Academic-integrity boundary

CS336 repo guidance says AI assistants should act as teaching assistants, not solution generators. Do not edit graded code, paste full Python implementations, or complete tokenizer/model/optimizer/training-loop components. Coach with concepts, invariants, small tests, and code review of user-written snippets.

## TDD stages that worked well

1. Adapter/import smoke test: make `tests/adapters.py::get_tokenizer` instantiate the user tokenizer object.
2. Empty string: `encode("") -> []`; `decode([]) -> ""`.
3. Single ASCII byte: build `id_to_bytes` and `bytes_to_id`; remember iterating a `bytes` object yields `int`, so convert byte ints to length-1 `bytes` before lookup.
4. Single Unicode char: decode by concatenating all token bytes first, then UTF-8 decode with `errors="replace"`; do not decode each byte token independently.
5. Encode-time BPE merge: build `merge_rank: dict[tuple[bytes, bytes], int]`; repeatedly choose the valid adjacent pair with minimum rank, merge non-overlapping occurrences, and continue until no valid pair remains.
6. GPT-2 regex pre-tokenization: use `regex`, not stdlib `re`, for `\p{L}` / `\p{N}`. Apply BPE merges independently inside each pre-token; do not merge across pre-token boundaries.
7. Special tokens: split text into normal and special segments before regex/BPE. Special segments map directly to ids; normal segments follow regex + BPE.
8. Overlapping special tokens: match longest-first, e.g. prefer `<|endoftext|><|endoftext|>` over two shorter tokens.

## Useful invariants and debugging checks

- `encode` always returns `list[int]`, never `None`.
- `decode` always returns `str`.
- `apply_merge` always returns `list[bytes]`, even when no merge is possible.
- Merge invariant: `b"".join(before_tokens) == b"".join(after_tokens)`.
- Build `bytes_to_id` before using it to construct `special_token_to_id`.
- `self.special_tokens` should be an empty list when no special tokens are provided, not `None`.
- Avoid using `bytes` as a variable name because it shadows the built-in.

## Common failure patterns

- `KeyError: 115`: using an integer byte value as a key into `bytes_to_id`; wrap as a single-byte `bytes` object.
- `AttributeError: no attribute 'bytes_to_id'`: constructing special token ids before initializing `bytes_to_id`.
- LSP says function might return `None`: add a return annotation and an explicit fallback return, and remove caller-side `None` checks if `None` is not part of the function contract.
- `TypeError: 'NoneType' object is not iterable`: usually `encode` or `apply_merge` fell off the end without returning a list, or an empty-string branch used bare `return`.

## Stage 9: train_bpe implementation guidance

When coaching the training side, guide the user through these conceptual steps without writing the full implementation:

1. **Corpus reading**: read the input file as bytes; split on special tokens using `regex.split` with escaped special tokens; each segment is either a special token (pass through) or raw text (pre-tokenize).
2. **Pre-tokenization**: apply the GPT-2 regex to each raw-text segment to get pre-tokens; encode each pre-token as UTF-8 bytes; store as `tuple[bytes, ...]` for hashability.
3. **pretoken_counts**: build `dict[tuple[bytes, ...], int]` counting frequencies of each unique pre-token byte sequence. This compresses the corpus and avoids O(corpus_size) memory.
4. **Merge loop**: while `len(vocab) < vocab_size`:
   - Compute `pair_counts` from `pretoken_counts` by iterating each pre-token tuple and summing adjacent pair frequencies.
   - Select highest-frequency pair; tie-break by lexicographically greater pair.
   - Add merged token to vocab; record merge in `merges` list.
   - Update all pre-token tuples in `pretoken_counts`: replace every non-overlapping occurrence of the pair with the merged token.
5. **Return**: `(vocab: dict[int, bytes], merges: list[tuple[bytes, bytes]])`.

Key invariants to verify with the user:
- `vocab_size` includes the initial 256 byte tokens plus any special tokens; `merge_count = vocab_size - 256 - len(special_tokens)`.
- Special tokens are never split and never appear inside merged tokens; they are hard boundaries in both training and encoding.
- The tie-breaking rule (lexicographically greater on frequency ties) must match the handout specification exactly.
- `pretoken_counts` must be updated in-place; creating a new dict each iteration is acceptable but slower.
