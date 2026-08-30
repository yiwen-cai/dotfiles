# CS336 Spring 2026 Lecture Source Workflow

Use this reference when planning or summarizing CS336 lectures for the user.

## Durable convention

- Treat **Stanford CS336 Spring 2026** as the authoritative lecture version for future CS336 lecture explanations and plans.
- Keep Assignment 1 implementation/verification tied to the user's current lab repo and public tests; lecture version and repo test state can differ.

## Required source check before lecture notes

Before writing lecture notes or using a lecture as Day N background:

1. Fetch the current official course page: `https://cs336.stanford.edu/`.
2. Locate the lecture row in the schedule and confirm:
   - lecture number,
   - date,
   - title,
   - material link (`lecture_XX.pdf` or `lecture_XX.py`).
3. If the material is a PDF, download the official GitHub raw PDF and extract text with `pdftotext` when available.
4. Base the note outline on the official title and extracted material, not on prior-year memory or assumptions.
5. If extraction fails, state that explicitly and use the schedule title plus user-provided notes/slides instead of inventing details.

## Pitfall from a prior session

CS336 Spring 2026 Lecture 4 is **Attention alternatives and mixture of experts**, not training systems basics. The training-side Day 9 utility plan (`LR schedule -> AdamW -> checkpointing`) remains valid for Assignment 1, but it should not be attributed to Lecture 4.

## Useful command pattern

```bash
curl -L --max-time 30 -D /tmp/cs336_headers.txt -o /tmp/cs336.html https://cs336.stanford.edu/
python3 - <<'PY'
from pathlib import Path
import re
html = Path('/tmp/cs336.html').read_text(errors='replace')
for m in re.finditer(r'lecture_04|Lecture 4|Wed April 8', html, re.I):
    print(html[max(0, m.start()-600):m.end()+1000])
PY
curl -L --max-time 60 -o /tmp/cs336_lecture_04.pdf https://github.com/stanford-cs336/lectures/raw/main/lecture_04.pdf
pdftotext /tmp/cs336_lecture_04.pdf /tmp/cs336_lecture_04.txt
```
