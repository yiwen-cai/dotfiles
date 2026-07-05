# Handout-to-Test-to-TDD Workflow

Use this workflow when a course assignment provides both a **handout PDF** and a **public test suite**. The goal is to produce a structured TDD development order before writing any implementation code — avoiding the common mistake of reading tests in isolation and missing handout-specified constraints, or reading the handout in isolation and missing test-level interface details.

## Workflow Steps

### Step 1: Extract Handout PDF → Text

If the handout is a PDF, extract text to enable grep-based search:

```bash
# Preferred: pdftotext (pre-installed on most Linux / lab servers)
pdftotext -layout handout.pdf /tmp/handout.txt

# Fallback: pymupdf
python3 -c "import pymupdf; doc = pymupdf.open('handout.pdf'); [print(p.get_text()) for p in doc]" > /tmp/handout.txt
```

### Step 2: Identify Key Section via Grep

Grep for terms that map to the specific component you are about to implement:

```bash
grep -n -i -E "tokenizer|bpe|vocab|merge|special token|pretoken|regex|tie|deliverable" /tmp/handout.txt
```

Read the surrounding sections (typically 10-30 lines around each match) to capture the full specification.

**Extract these specifics:**
- Input/output types and field definitions
- Tie-breaking rules (e.g., lexicographically greater on tie)
- Boundary rules (e.g., no cross-pre-token merging)
- Performance constraints (e.g., speed tests)
- Special-case handling (special tokens as hard boundaries)
- Decode error handling (e.g., `errors='replace'`)
- Recommended libraries (e.g., `regex` package, not `re`)
- Toy example outputs and intermediate states

### Step 3: Read Public Tests

Read the test files that exercise the same component. Extract:

- Interface signatures (from adapter files)
- Test categories (roundtrip, alignment, edge cases, performance)
- Expected invariants (e.g., `merges == reference_merges`)
- Boundary inputs (empty, Unicode, special tokens, overlapping tokens, real text)
- Memory/performance requirements (e.g., <1.5s speed tests, 1MB memory limit)
- Snapshot comparison patterns (pytest-snapshot, npz files)

### Step 4: Align Handout Rules with Test Expectations

Create a table mapping handout requirements to test assertions:

| Handout rule | Test file | Test assertion | What it means for impl |
|---|---|---|---|
| ... | ... | ... | ... |

This alignment catches mismatches early — handout says one thing, test checks another, and the implementation must satisfy both. If the handout toy example uses simplified rules (whitespace split) but the actual test uses GPT-2 regex, note the gap explicitly.

### Step 5: Design Core Data Structures

Before writing TDD stages, sketch the internal data structures. This is the bridge between "I know the contracts" and "I know what to test first." Example for a tokenizer:

| Data structure | Type | Purpose |
|---|---|---|
| `id_to_bytes` | `dict[int, bytes]` | decode lookup |
| `bytes_to_id` | `dict[bytes, int]` | encode lookup |
| `merge_rank` | `dict[tuple[bytes, bytes], int]` | merge priority |
| `special_token_to_id` | `dict[str, int]` | special token IDs |
| `pretoken_counts` | `dict[tuple[bytes, ...], int]` | compressed corpus frequency |
| `pair_counts` | `dict[tuple[bytes, bytes], int]` | running pair frequency table |

### Step 6: Build TDD Stages

Design a stage plan where each stage isolates exactly ONE concern:

| Stage | Test | Milestone | What can fail |
|---|---|---|---|
| 0 | Any test | adapter returns non-NotImplementedError | Import path, class not found |
| 1 | simplest roundtrip | empty / single char roundtrip | decode plumbing, id_to_bytes |
| 2 | Unicode roundtrip | multi-byte UTF-8 roundtrip (emoji) | byte-level handling |
| 3 | pre-tokenization alignment | GPT-2 regex splits match expected | regex package usage |
| 4 | special token handling | single special token preserved | longest-first matching |
| 5 | overlapping special tokens | multi-token overlapping | token splitting logic |
| 6 | real text roundtrip | address/german/tinystories files | whitespace/newline/unicode |
| 7 | streaming encode | encode_iterable memory test | chunk boundary handling |
| 8 | training | merges == reference | tie-breaking, pre-token, special boundary |

Principles:
- **One variable per stage** — only add one new concern at a time.
- **Earlier stages are narrower** — start with the smallest possible input.
- **Training comes last** — train_bpe failures are hard to debug if encode/decode are also wrong.
- **Performance comes after correctness** — make it right, then make it fast.

### Step 7: Create Dual-Format Notes

After the TDD plan is complete, produce two output files:

1. **Agent-readable Markdown** (`notes/<component-name>.md`) — for the AI assistant to load in future sessions. Structured sections, tables, code blocks. Self-contained context.

2. **Human-readable HTML** (`notes/<component-name>.html`) — for the user to browse directly. Dark-themed, syntax-highlighted, well-formatted. One-page reference that does not require loading a markdown viewer.

The MD version should contain:
- Key data structures and their types
- Flow diagrams (text-based)
- Handout rules table
- Test expectations table
- TDD stage table
- Command cheat sheet

The HTML version should contain the same information with:
- Visual hierarchy (headings, colors, tags)
- Tables with alternating row colors
- Info/warning callout boxes with emoji indicators
- Code blocks with file-type labels
- Responsive layout for mobile viewing

### Step 8: Record Workspace Path

After creating files, confirm the exact workspace directory with the user. If they correct you, save it to memory and update any file paths. CS336 example: user's actual workspace was `/Users/yiwencai/Documents/code/cs336`, not `/Users/yiwencai/code/cs336`.

## When to Use

- Any course assignment that has both a handout (PDF/markdown) and a public test suite.
- Any implementation-heavy task where understanding the *contract* before writing code would save debugging time.
- When the user has finished the foundational lecture(s) and is about to start implementation.

## Pitfalls

- **Skipping Step 2 (by title only):** Handout sections can span multiple pages; a single keyword search may miss important context. Always read ~30 lines around each match.
- **Skipping Step 4 (cross-referencing):** Reading tests and handout separately can miss mismatches between handout terminology and test assertions.
- **Inverted TDD order:** Starting with train_bpe (which has the most failure modes) instead of encode/decode (fewer variables).
- **Memory blowup:** Using `re.findall` instead of `re.finditer` for large corpora.
- **Wrong Unicode handling:** Treating characters as base unit instead of UTF-8 bytes in a byte-level tokenizer.
- **Short-first special tokens:** Forgetting longest-first for overlapping special tokens.
- **Wrong workspace directory:** Assuming default `~/code/` without verifying. Always confirm with the user.
