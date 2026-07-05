#!/usr/bin/env python3
"""
Paper Note Helper Script

Extracts text, metadata, and renders key pages from a paper PDF.
Outputs a JSON manifest entry to stdout for consumption by the LLM agent.

Usage:
    python3 generate_paper_note.py --pdf paper.pdf --output ./paper_notes --slug my_slug

Requires: pdftotext, pdftoppm, pdfinfo (from poppler-utils)
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

METHOD_KEYWORDS = [
    "method", "approach", "algorithm", "architecture", "framework",
    "design", "overview", "system", "implementation", "attention",
    "quantization", "compression", "eviction", "pipeline", "workflow",
    "mechanism", "formulation", "proposed", "our model", "our method",
]

EXPERIMENT_KEYWORDS = [
    "experiment", "evaluation", "benchmark", "results", "ablation",
    "analysis", "throughput", "latency", "speedup", "perplexity",
    "accuracy", "performance", "memory", "compression ratio",
    "table", "figure", "dataset", "setup", "main results",
]

VENUE_PATTERNS = [
    r"Published as .*? at .*?(?:\n|$)",
    r"Proceedings of .*?(?:\n|$)",
    r"In .*?(?:Conference|Symposium|Workshop).*?(?:\n|$)",
    r"(?:ICLR|ICML|NeurIPS|ACL|EMNLP|NAACL|SOSP|OSDI|MLSys|COLM|ICML)\s*20\d{2}",
    r"arXiv:\d{4}\.\d{4,5}v?\d*\s*\[[^\]]+\]\s*\d{1,2}\s+\w+\s+20\d{2}",
]

NOT_FOUND = "未在 PDF 中明确标注"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class ExtractionResult:
    slug: str
    title: str
    authors: str
    venue: str
    arxiv_id: str | None
    page_count: int
    pdf_path: str
    text_path: str
    method_pages: list[int]
    experiment_pages: list[int]
    method_images: list[str]
    experiment_images: list[str]
    output_dir: str
    assets_dir: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_command(args: list[str], timeout: int = 180) -> str:
    """Run a subprocess and return stdout. Raises on non-zero exit."""
    completed = subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, timeout=timeout,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(args)}\n{completed.stderr.strip()}"
        )
    return completed.stdout


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_pages(text: str) -> list[str]:
    return text.split("\f")


def get_page_count(pdf_path: Path) -> int:
    info = run_command(["pdfinfo", str(pdf_path)], timeout=60)
    match = re.search(r"^Pages:\s*(\d+)", info, flags=re.MULTILINE)
    return int(match.group(1)) if match else 0


def extract_arxiv_id(text: str, filename: str) -> str | None:
    match = re.search(r"arXiv:\s*(\d{4}\.\d{4,5})", text, flags=re.I)
    if match:
        return match.group(1)
    match = re.search(r"(\d{4}\.\d{4,5})", filename)
    return match.group(1) if match else None


def extract_venue(text: str) -> str:
    head = text[:15000]
    for pattern in VENUE_PATTERNS:
        match = re.search(pattern, head, flags=re.I | re.S)
        if match:
            return normalize_space(match.group(0))
    arxiv = re.search(
        r"arXiv:\s*\d{4}\.\d{4,5}v?\d*\s*\[[^\]]+\]\s*\d{1,2}\s+\w+\s+20\d{2}",
        head, flags=re.I,
    )
    if arxiv:
        return normalize_space(arxiv.group(0))
    return NOT_FOUND


def extract_title_and_authors(first_page: str, fallback: str) -> tuple[str, str]:
    """Heuristic extraction of title and authors from first page text."""
    lines = [normalize_space(l) for l in first_page.splitlines()]
    lines = [
        l for l in lines
        if l and not l.lower().startswith(("arxiv:", "http", "www.", "preprint"))
    ]

    # Title
    title = ""
    for idx, line in enumerate(lines[:20]):
        if len(line) >= 12 and not re.search(
            r"@|copyright|abstract|proceedings|published as", line, re.I
        ):
            if (
                idx + 1 < len(lines)
                and len(lines[idx + 1]) >= 12
                and not re.search(
                    r"abstract|authors?|university|institute|school|department|lab",
                    lines[idx + 1], re.I,
                )
            ):
                combined = f"{line} {lines[idx + 1]}"
                if len(combined) <= 180:
                    title = combined
                    break
            title = line
            break
    if not title:
        title = fallback.replace("_", " ")

    title = re.sub(r"\s+", " ", title).strip()

    # Authors
    authors = NOT_FOUND
    candidate_lines = lines[1:18]
    for line in candidate_lines:
        if line == title or line in title:
            continue
        if re.search(
            r"@|http|abstract|arxiv|university|institute|school|department|laboratory|lab|preprint|copyright",
            line, re.I,
        ):
            continue
        if re.search(r"[A-Z][a-z]+", line) and len(line) < 260:
            authors = line
            break

    return title, authors


def extract_pdf_text(pdf_path: Path, output_txt: Path) -> str:
    """Extract text from PDF using pdftotext with layout preservation."""
    run_command(["pdftotext", "-layout", str(pdf_path), str(output_txt)], timeout=300)
    return output_txt.read_text(errors="ignore")


def top_pages_by_keywords(
    pages: list[str],
    keywords: list[str],
    exclude: set[int],
    count: int,
) -> list[int]:
    """Score pages by keyword occurrence and return top-N page numbers."""
    scored = []
    for idx, page in enumerate(pages, start=1):
        if idx in exclude or len(page.strip()) < 200:
            continue
        low = page.lower()
        score = sum(low.count(k.lower()) for k in keywords)
        figure_bonus = len(re.findall(r"\b(?:figure|fig\.|table)\s*\d+", low))
        if figure_bonus:
            score += figure_bonus * 3
        if score > 0:
            scored.append((score, idx))
    scored.sort(reverse=True)
    return [idx for _, idx in scored[:count]]


def render_page_image(pdf_path: Path, page_num: int, out_dir: Path, prefix: str) -> str:
    """Render a PDF page as a PNG image using pdftoppm."""
    out_base = out_dir / f"{prefix}_p{page_num:02d}"
    run_command([
        "pdftoppm", "-f", str(page_num), "-l", str(page_num),
        "-png", "-r", "150", str(pdf_path), str(out_base),
    ], timeout=120)
    # pdftoppm appends -<page_num>.png; find it
    generated = out_dir / f"{out_base.name}-{page_num}.png"
    if not generated.exists():
        candidates = sorted(out_dir.glob(f"{out_base.name}-*.png"))
        if not candidates:
            raise FileNotFoundError(
                f"No image generated for {pdf_path} page {page_num}"
            )
        generated = candidates[0]
    final = out_dir / f"{prefix}_p{page_num:02d}.png"
    if generated != final:
        generated.replace(final)
    return final.name


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Extract paper PDF content for note generation")
    parser.add_argument("--pdf", required=True, help="Path to the PDF file")
    parser.add_argument("--output", required=True, help="Output directory (e.g., ./paper_notes)")
    parser.add_argument("--slug", required=True, help="Slug identifier (e.g., 01_pagedattention_vllm_2309.06180)")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(json.dumps({"error": f"PDF not found: {pdf_path}"}))
        sys.exit(1)

    output_dir = Path(args.output).resolve() / args.slug
    assets_dir = output_dir / "assets"
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    text_path = output_dir / "paper.txt"

    # --- Extract text ---
    try:
        text = extract_pdf_text(pdf_path, text_path)
    except Exception as e:
        print(json.dumps({"error": f"Text extraction failed: {e}"}))
        sys.exit(1)

    pages = split_pages(text)

    # --- Metadata ---
    first_page = pages[0] if pages else text[:3000]
    title, authors = extract_title_and_authors(first_page, args.slug)
    venue = extract_venue(text)
    arxiv_id = extract_arxiv_id(text, pdf_path.name)
    page_count = get_page_count(pdf_path)

    # --- Rank pages ---
    if pages:
        # Method pages: top 2 from first 20 pages (exclude page 1)
        method_pages = top_pages_by_keywords(pages[:30], METHOD_KEYWORDS, exclude={1}, count=2)
        if not method_pages and page_count:
            method_pages = [min(3, page_count)]

        # Experiment pages: top 3 from whole PDF (exclude method pages and page 1)
        experiment_pages = top_pages_by_keywords(
            pages, EXPERIMENT_KEYWORDS,
            exclude=set(method_pages) | {1}, count=3,
        )
        if not experiment_pages and page_count:
            experiment_pages = [max(1, page_count - 2)]
    else:
        method_pages = []
        experiment_pages = []

    method_pages = method_pages[:2]
    experiment_pages = experiment_pages[:3]

    # --- Render images ---
    method_images = []
    for page_num in method_pages:
        try:
            method_images.append(render_page_image(pdf_path, page_num, assets_dir, "method"))
        except Exception as e:
            print(f"WARN method image failed p{page_num}: {e}", file=sys.stderr)

    experiment_images = []
    for page_num in experiment_pages:
        try:
            experiment_images.append(render_page_image(pdf_path, page_num, assets_dir, "experiment"))
        except Exception as e:
            print(f"WARN experiment image failed p{page_num}: {e}", file=sys.stderr)

    # --- Build result ---
    result = ExtractionResult(
        slug=args.slug,
        title=title,
        authors=authors,
        venue=venue,
        arxiv_id=arxiv_id,
        page_count=page_count,
        pdf_path=str(pdf_path),
        text_path=str(text_path),
        method_pages=method_pages[:len(method_images)],
        experiment_pages=experiment_pages[:len(experiment_images)],
        method_images=method_images,
        experiment_images=experiment_images,
        output_dir=str(output_dir),
        assets_dir=str(assets_dir),
    )

    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
