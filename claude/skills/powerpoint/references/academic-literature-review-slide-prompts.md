# Academic literature-review slide prompt workflow

Use this reference when the user is preparing an academic presentation with an external AI slide generator and asks for a Markdown prompt/specification rather than a finished `.pptx`.

## Preferred workflow

1. Start from the agreed outline, but do not immediately write the whole deck prompt.
2. For each part, first explain what that section should cover:
   - narrative role in the talk
   - key technical concepts
   - representative papers or methods
   - technical principle / implementation intuition
   - strengths and limitations
   - transition to the next part
3. Let the user confirm, correct, or redirect the section.
4. Only then append that section's slide specifications to the Markdown prompt file.
5. Keep writes/patches small; large one-shot `write_file` calls can time out in WebUI streams.

## Slide spec shape

For every slide include:

- page title
- recommended layout
- concise on-slide text
- required visual/diagram/chart
- takeaway
- speaker notes / talk track
- transition sentence when useful

## Literature-review structure

Avoid paper-by-paper dumping. Prefer concept-first grouping:

```text
problem / old baseline
    ↓
new technical shift
    ↓
representative paper(s)
    ↓
core mechanism
    ↓
strengths and limitations
    ↓
why the next method appears
```

## Recency-sensitive reviews

When the user asks for a recent literature review, actively check whether older foundational papers should be downgraded to background/baseline and whether newer papers should become the main body.

Recommended framing:

- foundational papers: establish vocabulary and baseline only
- recent papers: carry the main narrative and technical depth
- trend papers: use for outlook, not as unverified solved problems

For fast-moving LLM systems topics, explicitly separate:

```text
2023-2024 foundations / baselines
2025-2026 main advances
frontier trends and open questions
```

## Common pitfall

If the user says "I will use AI to generate the PPT", do not create a `.pptx` unless they ask. Create/update a Markdown slide-generation prompt instead.