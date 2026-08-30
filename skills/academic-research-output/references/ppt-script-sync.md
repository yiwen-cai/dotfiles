# Synchronizing Speaker Scripts from an Edited PPT

Use this when the user has edited a `.pptx` and asks to update the speaking script or related markdown materials to match the current deck.

## Workflow

1. **Read the actual PPT first**
   - Do not rely on older slide briefs or previous scripts.
   - Extract the current `.pptx` slide text and notes with `python-pptx`.
   - Record the actual slide count from `Presentation.slides`, not from visual footer text.

2. **Create a slide extraction artifact**
   - Save a markdown extraction such as `ppt_current_extracted.md` with:
     - source PPT path
     - actual slide count
     - each slide number, title, text blocks, and speaker notes if present
   - This gives the user and future agent a concrete basis for comparison.

3. **Rewrite the script to the actual deck**
   - Align script headings exactly as `[Slide N]` for the actual `1..N` slide count.
   - Preserve the deck’s current sequence even if it differs from prior plans.
   - Merge or remove script sections for slides the user deleted/combined.
   - Keep technical nuance from prior research only where the current PPT still has a corresponding slide.

4. **Preserve the old script**
   - Before overwriting `kv_cache_speech_script.md` or equivalent, save a timestamped backup.
   - Also create a clearly named current version such as `kv_cache_speech_script_current_ppt.md`.

5. **Verify alignment**
   - Check script slide headings form a continuous sequence matching the PPT’s actual slide count.
   - Check key terms from the deck are present in the script.
   - If PPT visual footers still show an old total page count, report it separately instead of changing the script to match the stale footer.

## Pitfalls

- **Stale footer trap**: A modified PPT may have 35 actual slides but page footers still say `/38`. Use the extracted slide count for the script and flag the footer mismatch.
- **Old plan drift**: Do not keep earlier script slides just because they were in a generated brief; if the current PPT removed them, the script should remove or merge them too.
- **Notes absence**: If speaker notes are empty, generate remarks from visible slide text and known narrative context, but clearly align them to the current slide titles/content.

## Minimal `python-pptx` extraction pattern

```python
from pathlib import Path
from pptx import Presentation

ppt = Path("/path/to/deck.pptx")
prs = Presentation(str(ppt))

for i, slide in enumerate(prs.slides, start=1):
    texts = []
    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text.strip():
            texts.append("\n".join(line.strip() for line in shape.text.splitlines() if line.strip()))
    title = texts[0].split("\n")[0] if texts else f"Slide {i}"
    print(i, title)
```
