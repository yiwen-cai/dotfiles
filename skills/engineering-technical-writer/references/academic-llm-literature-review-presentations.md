# Academic LLM Literature Review Presentation Workflow

Use this reference when helping the user prepare a technical academic sharing/report, especially an LLM systems or ML paper survey with slides.

## Deliverable shape

Prefer a two-track document structure per section/part:

- `partN_explanation.md`: speaker preparation notes.
- `partN_ppt.md`: slide-generation instructions.
- Optional final merged file such as `complete_ppt_description.md` that concatenates all PPT descriptions and adds global design rules.

The explanation file should help the user understand and speak. The PPT file should help an AI/deck tool generate slides.

## Per-paper explanation standard

For every important paper, introduce it in this order:

1. Core technical implementation principle
   - What problem the paper solves.
   - What observation or assumption it uses.
   - How the method works step by step.
   - Include formulas, module diagrams, or execution flow only when they clarify the mechanism.
2. Main advantages
   - What it improves over baselines.
   - Why it fits the target workload.
   - System, efficiency, quality, or deployability value.
3. Limitations / applicability boundaries
   - Required assumptions.
   - Failure cases or workloads where benefits may shrink.
   - Engineering cost, kernel dependency, training/conversion requirements, or benchmark caveats.

Adjust detail by paper importance: spend more detail on core papers, summarize trend papers more compactly.

## Part-level workflow

1. Start from the talk goal, audience, and time budget.
2. Build a section outline first; do not jump directly to slide prose.
3. For each part, explain the narrative purpose and transition to adjacent parts.
4. After the user approves a part, write/update both the explanation md and PPT md.
5. At the end, merge all `part*_ppt.md` files into one complete PPT description md and verify slide count/headings.

## PPT description structure

Each slide entry should include:

- Page title.
- Page layout.
- Main content bullets.
- Figure/table/diagram requirements.
- Takeaway sentence.
- Speaker notes.

For technical survey decks, favor visual structures over dense text: timelines, taxonomy trees, method comparison tables, tensor-shape diagrams, system pipeline diagrams, and trade-off matrices.

## Survey narrative guidance

For fast-moving LLM systems topics:

- Keep foundational papers as background/baselines rather than over-centering them.
- Put the newest 2025-2026 work in the main narrative when the user asks for recent progress.
- Explicitly explain how each new paper critiques or extends the baseline.
- End each technical section with trade-offs, not just method advantages.

## Quality checks

Before reporting completion:

- Verify that every requested part has both explanation and PPT files.
- Verify merged PPT description contains all slide headings.
- Check that paper claims are grounded in downloaded papers, abstracts, or extracted text when available.
- Keep file names predictable and part-indexed.
