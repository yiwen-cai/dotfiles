# CS336 TA-Safe Tokenizer Guidance

Use this reference when helping a student work through Stanford CS336 Assignment 1 tokenizer implementation. The remote project guidance requires TA-style support: do not edit core solution files, do not provide full implementation code, and do not directly solve assignment TODOs. Guide via tests, invariants, error interpretation, and narrowly scoped conceptual hints.

## Required workflow

1. Read the remote project guidance first when working on lab:
   ```bash
   ssh lab 'cd /public/home/caiyiwen/code/cs336/assignment/assignment1-basics; for f in AGENTS.md AGENT.md CLAUDE.md .cursorrules; do [ -f "$f" ] && echo "===== $f =====" && sed -n "1,220p" "$f"; done; true'
   ```
2. If guidance forbids direct solution edits, pivot to TA mode immediately:
   - Ask the student to run commands and paste output.
   - Explain failure causes and next conceptual step.
   - Review user-written snippets for invariants and pitfalls.
   - Do not write or patch tokenizer/model/optimizer/training-loop solution code.
3. Use public tests as milestones, but avoid converting test requirements into a full pasteable solution.

## Tokenizer milestone sequence

- Stage 0: Adapter/import boundary. `tests/adapters.py::get_tokenizer` should instantiate the student's tokenizer object. A successful stage changes failure from adapter `NotImplementedError` to method-level `NotImplementedError` or behavior failure.
- Stage 1: Empty string roundtrip. `encode("") -> []`; `decode([]) -> ""`.
- Stage 2: Single ASCII character. Build `id_to_bytes: dict[int, bytes]` and `bytes_to_id: dict[bytes, int]`. Encode UTF-8 bytes as one-byte `bytes` tokens, not integer byte values.
- Stage 3: Single Unicode character roundtrip. Decode by concatenating bytes first, then UTF-8 decoding with `errors="replace"`; do not decode each token independently.
- Stage 4: Encode-time BPE merge. Build `merge_rank: dict[tuple[bytes, bytes], int]` from `merges`; repeatedly choose the valid adjacent pair with the smallest rank. Frequency and lexicographic tie-breaking belong to training-time BPE, not encode-time BPE.
- Stage 5: GPT-2 regex pre-tokenization. Split normal text into pre-tokens and apply BPE merges inside each pre-token only; do not merge across pre-token boundaries.
- Stage 6: Special tokens. Match longest-first and treat specials as hard boundaries.
- Stage 7: `encode_iterable`. Watch chunk boundaries and memory tests.
- Stage 8: `train_bpe`. Use compressed `pretoken_counts`, special-token boundaries, pair counts weighted by pre-token frequency, and training tie-breaking.

## Common pitfalls and diagnostic hints

### `KeyError: 115` during `encode("s")`

Root cause: iterating over a Python `bytes` object yields integers (`115`), but `bytes_to_id` keys should be token bytes such as `b"s"`. The fix concept is to convert each integer byte value into a length-1 `bytes` object before lookup.

### Unicode roundtrip passes but tiktoken match fails

This usually means byte-level encoding works but BPE merge is missing or wrong. Compare IDs and lengths against tiktoken, then inspect whether merged token boundaries match.

### Merge loop drops the last token

If the merge loop uses a condition like `while i < len(tokens) - 1`, an unmerged trailing token can be omitted. Suggest the invariant:

```text
b"".join(tokens_before_merge) == b"".join(tokens_after_merge)
```

Every merge changes segmentation only; it must never change the underlying byte sequence.

### Wrong merge priority

Encode-time merge priority is the smallest rank in the provided `merges` list. Do not use pair frequency or lexicographic order in encode-time merging.

## Safe review style

When reviewing a user's snippet, point out one or two specific invariants or edge cases, e.g.:

- Does the loop preserve the trailing token?
- Are pair keys `tuple[bytes, bytes]`, not `tuple[int, int]` or `tuple[str, str]`?
- Does the code re-scan adjacent pairs after each merge?
- Does pre-tokenization prevent merges across boundaries?

Avoid returning a complete corrected function. Ask the user to revise and rerun the next milestone test.
