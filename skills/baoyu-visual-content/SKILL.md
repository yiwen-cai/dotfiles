---
name: baoyu-visual-content
description: Generate visual content with Baoyu skills — article illustrations, knowledge comics, and infographics using Type
  × Style × Palette consistency.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Baoyu Visual Content Generator

Generate visual content using the Baoyu skill ecosystem. Covers article illustrations, knowledge comics, and infographics with consistent Type × Style × Palette dimensions.

## When to Use

- User asks to illustrate an article or add images to content
- User wants to create a knowledge/educational comic
- User asks for an infographic or visual summary
- User mentions "为文章配图", "知识漫画", "信息图", or similar terms

## Three Visual Formats

| Format | Purpose | Key Dimensions |
|--------|---------|----------------|
| **Article Illustrations** | Add images to articles/blog posts | Type × Style × Palette |
| **Knowledge Comics** | Educational/biography/tutorial comics | Art × Tone × Layout |
| **Infographics** | Data visualization, information graphics | Layout × Style |

## Shared Principles

All three formats follow these core principles:
- **Visualize concepts, not metaphors** — illustrate the underlying idea, not literal metaphors
- **Labels use actual data** — real numbers, terms, quotes from source content
- **Prompt files are mandatory** — every image must have a saved prompt file before generation
- **Strip secrets** — scan source content for API keys/tokens before writing output
- **Download images locally** — `image_generate` returns URLs; always `curl` to local files

## Article Illustrations

### Three Dimensions

| Dimension | Controls | Examples |
|-----------|----------|----------|
| **Type** | Information structure | infographic, scene, flowchart, comparison, framework, timeline |
| **Style** | Rendering approach | notion, warm, minimal, blueprint, watercolor, elegant |
| **Palette** | Color scheme | macaron, warm, neon |

### Workflow
1. Detect reference images (if provided)
2. Analyze content (type, purpose, core arguments)
3. Confirm settings via `clarify` (preset, density, style, palette)
4. Generate outline → `outline.md`
5. Generate prompts → `prompts/NN-{type}-{slug}.md`
6. Generate images via `image_generate`
7. Download images and insert into article

### Output Structure
```
{output-dir}/
├── source-{slug}.{ext}
├── outline.md
├── prompts/
│   └── NN-{type}-{slug}.md
└── NN-{type}-{slug}.png
```

## Knowledge Comics

### Visual Dimensions

| Option | Values |
|--------|--------|
| **Art** | ligne-claire, manga, realistic, ink-brush, chalk, minimalist |
| **Tone** | neutral, warm, dramatic, romantic, energetic, vintage, action |
| **Layout** | standard, cinematic, dense, splash, mixed, webtoon, four-panel |
| **Aspect** | 3:4 (portrait), 4:3 (landscape), 16:9 (widescreen) |

### Presets

| Preset | Equivalent | Special Rules |
|--------|-----------|---------------|
| `ohmsha` | manga + neutral | Visual metaphors, no talking heads, gadget reveals |
| `wuxia` | ink-brush + action | Qi effects, combat visuals, atmospheric |
| `shoujo` | manga + romantic | Decorative elements, eye details, romantic beats |
| `concept-story` | manga + warm | Visual symbol system, growth arc |
| `four-panel` | minimalist + neutral + four-panel | 起承转合 structure, B&W + spot color |

### Workflow
1. Analyze content → `analysis.md`, `source-{slug}.md`
2. Confirm style, focus, audience via `clarify`
3. Generate storyboard + characters → `storyboard.md`, `characters/`
4. Generate prompts → `prompts/*.md`
5. Generate character sheet (if multi-page)
6. Generate pages via `image_generate`
7. Download images to output directory

### File Structure
```
comic/{topic-slug}/
├── source-{slug}.md
├── analysis.md
├── storyboard.md
├── characters/
│   ├── characters.md
│   └── characters.png
├── prompts/
│   └── NN-{cover|page}-{slug}.md
├── NN-{cover|page}-{slug}.png
└── refs/ (optional reference images)
```

## Infographics

### Layout Gallery (21 options)

| Layout | Best For |
|--------|----------|
| `bento-grid` | Multiple topics, overview (default) |
| `linear-progression` | Timelines, processes |
| `binary-comparison` | A vs B, before-after |
| `hierarchical-layers` | Pyramids, priorities |
| `hub-spoke` | Central concept with related items |
| `funnel` | Conversion, filtering |
| `dashboard` | Metrics, KPIs |
| `dense-modules` | High-density data guides |

### Style Gallery (21 options)

| Style | Description |
|-------|-------------|
| `craft-handmade` | Hand-drawn, paper craft (default) |
| `cyberpunk-neon` | Neon glow, futuristic |
| `technical-schematic` | Blueprint, engineering |
| `pixel-art` | Retro 8-bit |
| `pop-laboratory` | Blueprint grid, lab precision |
| `morandi-journal` | Hand-drawn doodle, warm tones |

### Workflow
1. Analyze content → `analysis.md`
2. Generate structured content → `structured-content.md`
3. Recommend layout × style combinations
4. Confirm via `clarify`
5. Generate prompt → `prompts/infographic.md`
6. Generate image via `image_generate`
7. Download and report

### Output Structure
```
infographic/{topic-slug}/
├── source-{slug}.{ext}
├── analysis.md
├── structured-content.md
├── prompts/infographic.md
└── infographic.png
```

## Common Pitfalls

1. **Data integrity** — never alter source statistics
2. **Strip secrets** — scan for API keys before output
3. **Prompt files mandatory** — no image without saved prompt
4. **Absolute paths for curl** — never rely on shell CWD
5. **Aspect ratio mapping** — map custom ratios to nearest named option
6. **No backend selection** — `image_generate` uses user-configured model
7. **Download images** — URLs are ephemeral; save locally

## Related Skills

- `image-gen` — For direct image generation
- `comfyui` — For ComfyUI-based generation
- `apikey-image-gen` — For API-key based generation