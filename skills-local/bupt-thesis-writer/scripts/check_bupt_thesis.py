#!/usr/bin/env python3
"""Lightweight checks for the BUPTBachelorThesis LaTeX template."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


YEAR_RE = re.compile(r"year\s*=\s*[{\"](\d{4})[}\"]", re.IGNORECASE)
ENTRY_RE = re.compile(r"@\w+\s*{", re.IGNORECASE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def strip_latex_comment_lines(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("%"))


def check_required_files(root: Path) -> list[str]:
    issues: list[str] = []
    required = [
        "main.tex",
        "BUPTBachelorThesis.sty",
        "BUPTBachelor.bst",
        ".latexmkrc",
        "chapters/abstract.tex",
        "chapters/acknowledgment.tex",
        "ref.bib",
    ]
    for rel in required:
        if not (root / rel).exists():
            issues.append(f"missing required file: {rel}")
    if (root / "main.tex").exists():
        main = strip_latex_comment_lines(read(root / "main.tex"))
        if "docs/statement.pdf" in main and not (root / "docs/statement.pdf").exists():
            issues.append("main.tex includes docs/statement.pdf but the file is missing")
        if "docs/cover.pdf" in main and not (root / "docs/cover.pdf").exists():
            issues.append("main.tex references docs/cover.pdf; ensure it exists if that line is active")
        if "\\bibliographystyle{BUPTBachelor}" not in main:
            issues.append("main.tex does not use \\bibliographystyle{BUPTBachelor}")
        if "\\bibliography{ref}" not in main:
            issues.append("main.tex does not use \\bibliography{ref}")
    return issues


def check_chapters(root: Path) -> list[str]:
    issues: list[str] = []
    chapter_dir = root / "chapters"
    if not chapter_dir.exists():
        return ["missing chapters/ directory"]
    for tex in sorted(chapter_dir.glob("chapter*.tex")):
        text = read(tex)
        if "\\documentclass[../main.tex]{subfiles}" not in text:
            issues.append(f"{tex.relative_to(root)} is not a standard subfiles chapter")
        if "\\begin{document}" not in text or "\\end{document}" not in text:
            issues.append(f"{tex.relative_to(root)} is missing document boundaries")
    return issues


def check_bib(root: Path, min_refs: int, recent_ratio: float, recent_start: int) -> list[str]:
    issues: list[str] = []
    bib = root / "ref.bib"
    if not bib.exists():
        return ["missing ref.bib"]
    text = read(bib)
    entries = ENTRY_RE.findall(text)
    if len(entries) < min_refs:
        issues.append(f"ref.bib has {len(entries)} entries; expected at least {min_refs}")
    years = [int(m.group(1)) for m in YEAR_RE.finditer(text)]
    if years:
        recent = sum(1 for y in years if y >= recent_start)
        ratio = recent / len(years)
        if ratio < recent_ratio:
            issues.append(
                f"recent reference ratio is {ratio:.1%} ({recent}/{len(years)}); "
                f"expected at least {recent_ratio:.0%} from {recent_start}+"
            )
    else:
        issues.append("ref.bib has no parseable year fields")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="BUPTBachelorThesis project root")
    parser.add_argument("--min-refs", type=int, default=20)
    parser.add_argument("--recent-ratio", type=float, default=0.30)
    parser.add_argument("--recent-start", type=int, default=2024)
    args = parser.parse_args()

    root = args.root.resolve()
    issues: list[str] = []
    issues.extend(check_required_files(root))
    issues.extend(check_chapters(root))
    issues.extend(check_bib(root, args.min_refs, args.recent_ratio, args.recent_start))

    if issues:
        print("BUPT thesis checks found issues:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("BUPT thesis checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
