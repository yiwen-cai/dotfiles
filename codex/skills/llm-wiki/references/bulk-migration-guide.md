# Bulk Migration Guide

Migrating an existing organized research collection into an llm-wiki.

## When to Use

User has a folder like `~/Documents/study/第一次汇报分享/` with:
- 10+ papers (PDFs)
- Paper notes (extracted text, HTML, assets)
- Speech drafts / PPT descriptions
- Scripts or tools

## User Preference: Physical Migration

Default to **copying files into wiki/raw/**, not referencing external paths. The user explicitly prefers this:
> "所有文件我都希望直接迁移，不用复制也不用引用" (migrate directly, don't reference externally)

Only use external path references when the user explicitly requests it.

## 5-Phase Migration Workflow

### Phase 1: Migrate Raw Materials

```bash
mkdir -p wiki/raw/papers wiki/raw/paper_notes wiki/study_archive/pptx wiki/study_archive/speech wiki/study_archive/scripts
cp study_folder/paper/*.pdf wiki/raw/papers/
cp -R study_folder/paper_notes/* wiki/raw/paper_notes/
cp study_folder/*.pptx wiki/study_archive/pptx/
cp study_folder/*.md wiki/study_archive/speech/
cp study_folder/*.py wiki/study_archive/scripts/
```

**Critical:** Always `mkdir -p` before `cp`. Writing to `raw/papers/file.md` fails if `raw/papers/` doesn't exist yet.

### Phase 2: Create Concept Skeleton

Create 4-6 concept pages covering the domain taxonomy. Example for AI/ML inference:

- `concepts/kv-cache-optimization-survey.md` — Top-level overview
- `concepts/kv-cache-system-management.md`
- `concepts/kv-cache-compression.md`
- `concepts/kv-cache-architecture-co-design.md`
- `concepts/sparse-attention.md`
- `concepts/kv-cache-frontier-trends.md`

Each concept page should have:
- YAML frontmatter with taxonomy tags
- A summary of that sub-field
- A table of relevant papers (with `[[wikilinks]]` to entity pages)
- Links to related concept pages

### Phase 3: Create Core Entity Pages (5-10 most important)

For each key paper, create `entities/<slug>.md` with:
- Frontmatter: title, tags, sources (pointing to `raw/papers/` and `raw/paper_notes/`)
- One-sentence summary (extracted from paper_notes or speech)
- Method, results, relations, personal notes sections
- Cross-links to 2+ other pages

**Batch creation:** Use `execute_code` to generate stubs for all papers at once, then fill summaries from `paper_notes/*/paper.txt` or speech content.

### Phase 4: Convert Speech/Report to Survey Report

If the user has a speech draft or report:

1. Convert plain-text paper mentions to `[[wikilinks]]` using regex:
   ```python
   # Replace "PaperName" with "[[slug|PaperName]]" if not already in a link
   ```
2. Create `queries/<topic>-survey-report.md` with:
   - Frontmatter
   - Executive summary
   - Sections matching the speech structure
   - Tables of papers with wikilinks
   - Personal insights / takeaways

### Phase 5: Update Navigation

1. Update `index.md`:
   - Add all new entities, concepts, queries
   - Remove domain-irrelevant entries (e.g., karpathy, wiki-methodology if not research-focused)
   - Update page count
2. Append to `log.md` with migration summary
3. Run lint: check for orphans, broken links, missing index entries

## Handling Duplicate Entity Files

When both `entities/pagedattention.md` and `entities/pagedattention-vllm.md` exist:
- Check which one has content vs which is a stub
- Delete the stub, keep the filled one
- Update all wikilinks to point to the kept file
- Common pattern: hyphenated vs underscore variants of the same slug

## PDF Preservation

When user asks to keep original PDFs:
- Download PDF alongside extracted markdown
- Add `pdf:` field to raw frontmatter
- Example:
  ```yaml
  ---
  source_url: https://arxiv.org/abs/2605.17170
  ingested: 2026-06-18
  sha256: <hex digest>
  pdf: raw/papers/2605.17170.pdf
  ---
  ```

## Speech-to-Wikilinks Conversion

Speech drafts often mention papers in plain text. Convert to wikilinks:

```python
paper_name_to_slug = {
    'PagedAttention': 'pagedattention',
    'KIVI': 'kivi',
    'DeepSeek-V2': 'deepseek_v2_mla',
    # ... etc
}

for name, slug in paper_name_to_slug.items():
    pattern = r'(?<!\[)\b' + re.escape(name) + r'\b(?!\])'
    speech = re.sub(pattern, f'[[{slug}|{name}]]', speech)
```

## Post-Migration Cleanup

1. Remove source folder after migration (if user confirms)
2. Verify `raw/` structure is clean (no .DS_Store, no stray files)
3. Check that all `sources:` frontmatter fields point to valid paths
4. Ensure no duplicate slugs (hyphen vs underscore variants)
