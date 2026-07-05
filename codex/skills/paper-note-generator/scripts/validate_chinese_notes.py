#!/usr/bin/env python3
"""Validate paper-note HTML files for Chinese-only note quality.

Checks that generated note pages keep required sections, reference existing
images, and do not contain long copied English body paragraphs. Metadata such
as paper titles, authors, URLs, arXiv IDs, method names, dataset names, and
metrics may still contain English.

Usage:
    python3 validate_chinese_notes.py /path/to/paper_notes
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REQUIRED_SECTIONS = [
    "论文概括",
    "核心技术原理讲解",
    "实验分析",
    "局限性和展望",
]


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.texts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"style", "script"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"style", "script"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        text = re.sub(r"\s+", " ", data).strip()
        if text:
            self.texts.append(text)


def looks_like_metadata_or_allowed_english(text: str) -> bool:
    allowed_markers = [
        "/",
        "http",
        "arXiv",
        "PDF",
        "Figure",
        "Table",
        "KV",
        "LLM",
    ]
    return any(marker in text for marker in allowed_markers)


def looks_like_long_english_body(text: str) -> bool:
    if looks_like_metadata_or_allowed_english(text):
        return False
    ascii_letters = sum(char.isascii() and char.isalpha() for char in text)
    cjk_chars = sum("\u4e00" <= char <= "\u9fff" for char in text)
    english_words = re.findall(r"[A-Za-z]{3,}", text)
    return (
        len(text) >= 120
        and ascii_letters > max(cjk_chars * 2, 60)
        and len(english_words) >= 18
    )


def validate_note(path: Path) -> dict[str, object]:
    html = path.read_text(encoding="utf-8")
    missing_sections = [section for section in REQUIRED_SECTIONS if section not in html]
    image_refs = re.findall(r"<img src=['\"]([^'\"]+)['\"]", html)
    missing_images = [src for src in image_refs if not (path.parent / src).exists()]

    parser = VisibleTextParser()
    parser.feed(html)
    long_english = [text for text in parser.texts if looks_like_long_english_body(text)]

    return {
        "slug": path.parent.name,
        "path": str(path),
        "image_count": len(image_refs),
        "missing_sections": missing_sections,
        "missing_images": missing_images,
        "long_english_count": len(long_english),
        "long_english_examples": [text[:240] for text in long_english[:3]],
        "ok": not missing_sections and not missing_images and not long_english,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Chinese paper note HTML files")
    parser.add_argument("paper_notes_dir", help="Directory containing paper_notes/*/index.html")
    args = parser.parse_args()

    base = Path(args.paper_notes_dir).expanduser().resolve()
    notes = sorted(
        path for path in base.glob("*/index.html") if path.parent.name[:2].isdigit()
    )
    results = [validate_note(path) for path in notes]
    problems = [result for result in results if not result["ok"]]

    summary = {
        "notes": len(notes),
        "total_images": sum(int(result["image_count"]) for result in results),
        "problems": len(problems),
        "problem_details": problems,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
