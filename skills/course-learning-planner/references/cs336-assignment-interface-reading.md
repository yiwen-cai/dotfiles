# CS336 Assignment Interface Reading

Use this reference when helping the user study CS336 implementation-heavy assignments without violating course integrity constraints.

## Pattern

After the relevant lecture has been reviewed, read the public tests and adapter signatures before discussing implementation. The goal is to extract contracts, invariants, and edge cases, not to produce pasteable code.

Recommended order for Assignment 1 tokenizer work:

1. Read the repository guidance files first (`AGENTS.md`, `CLAUDE.md`) and follow TA-mode restrictions.
2. Read `tests/adapters.py` for the required public function signatures.
3. Read `tests/test_train_bpe.py` for training output contracts, speed expectations, special-token constraints, and reference comparison behavior.
4. Read `tests/test_tokenizer.py` for tokenizer object behavior: `encode`, `decode`, `encode_iterable`, GPT-2/tiktoken alignment, Unicode, special tokens, overlapping special tokens, and memory usage.
5. Summarize as an "implementation-before-coding checklist" instead of writing solution code.

## What to extract

For each tested component, report:

- Function or object API.
- Input and output types.
- Behavioral invariants.
- Boundary cases.
- Performance or memory expectations.
- How the assignment differs from lecture toy code.

## CS336 Assignment 1 tokenizer contracts observed

`run_train_bpe(input_path, vocab_size, special_tokens, **kwargs)` returns:

- `vocab: dict[int, bytes]`, token id to raw token bytes.
- `merges: list[tuple[bytes, bytes]]`, ordered BPE merge pairs.

Important constraints:

- `vocab_size` includes special tokens.
- `merges` order matters and is compared exactly against the reference.
- Vocabulary key and value sets are checked against the reference.
- Special tokens should be added but should not be merged into ordinary tokens; ordinary vocab entries should not be polluted by fragments such as `b"<|"`.
- Speed is part of the public tests, so lecture toy code may be too slow.

`get_tokenizer(vocab, merges, special_tokens=None)` should return an object supporting:

- `encode(text)` -> token ids.
- `decode(ids)` -> string.
- `encode_iterable(iterable)` -> streaming token ids.

Tokenizer test themes:

- Roundtrip: `decode(encode(text)) == text` for empty strings, ASCII, Unicode, emoji, and file fixtures.
- GPT-2/tiktoken alignment for token ids on many fixtures.
- Special tokens remain single tokens during encoding/decoding.
- Overlapping special tokens require careful handling, usually longest-match reasoning.
- `encode_iterable` must be memory-conscious and should not simply join a large iterable into one string.

## Response style under integrity constraints

Allowed:

- Explain concepts and test intent.
- Point to files and line-level regions.
- Give high-level non-pasteable algorithms.
- Suggest toy manual checks, assertions, and debugging questions.
- Review code the user has already written with targeted feedback.

Avoid:

- Writing assignment solution code or pseudocode.
- Editing core assignment files.
- Translating public tests directly into a finished implementation.
- Pointing to third-party solutions.
