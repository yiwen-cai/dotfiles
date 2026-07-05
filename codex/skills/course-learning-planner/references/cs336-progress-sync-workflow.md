# CS336 Progress Sync Workflow

Use this when the user asks to "同步进展", "更新笔记", "记录今天进展", or similar for CS336 learning work.

## Required outputs

Update all three surfaces together:

1. **Markdown notes** under `/Users/yiwencai/Documents/code/cs336/notes/` or the relevant project Markdown file.
2. **HTML companion** for human-readable browsing. Do not leave HTML stale when Markdown changes.
3. **llm_wiki** so future agents can retrieve the same progress/context from the knowledge base.

## Workflow

1. Inspect the current Markdown and HTML files before editing.
2. Update the Markdown with:
   - completed milestones,
   - tests or verification commands,
   - key conceptual takeaways,
   - pitfalls/debugging lessons,
   - next-day plan.
3. Update the HTML companion with matching content and an updated timestamp/footer.
4. Sync the same progress summary into llm_wiki using the available wiki/notes workflow.
5. Verify:
   - file timestamps changed,
   - key headings appear in Markdown and HTML,
   - llm_wiki entry/page was updated.

## CS336-specific notes

- Keep coding work on lab and note/wiki work locally unless the user says otherwise.
- Preserve TA-style boundaries for assignment code: guide, review snippets, explain errors, and suggest tests/invariants rather than writing complete graded solutions.
- For tokenizer progress, include both implementation milestones and debugging lessons, e.g. byte int vs `bytes`, BPE merge rank, pre-token boundaries, special token longest-first, `encode_iterable` yielding flat token ids, and train_bpe pair-count/tie-breaking lessons.
