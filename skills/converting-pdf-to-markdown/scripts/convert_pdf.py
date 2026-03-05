#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "markitdown[all]",
#   "pymupdf",
# ]
# ///
"""Convert a PDF file to Markdown using markitdown.

Uses markitdown for text extraction and pymupdf for TOC-based heading injection.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError:
    print("Error: markitdown is not installed. Run: pip install 'markitdown[all]'", file=sys.stderr)
    sys.exit(1)

try:
    import pymupdf
except ImportError:
    pymupdf = None


def _get_toc_headings(pdf_path: str) -> list[tuple[int, str, int]]:
    """Extract TOC entries from a PDF using pymupdf.

    Returns list of (level, title, page_number) tuples.
    Page numbers are 1-based.
    """
    if pymupdf is None:
        return []
    doc = pymupdf.open(pdf_path)
    toc = doc.get_toc()  # [[level, title, page], ...]
    doc.close()
    return [(level, title, page) for level, title, page in toc]


def _find_toc_title_in_text(text: str, title: str, search_start: int = 0) -> int:
    """Find the position of a TOC title in the converted text.

    Tries exact match first, then a normalized match (ignoring whitespace
    differences).
    """
    # Exact match
    pos = text.find(title, search_start)
    if pos != -1:
        return pos

    # Normalized match: collapse whitespace in both
    pattern = r"\s*".join(re.escape(ch) for ch in title if not ch.isspace())
    match = re.search(pattern, text[search_start:])
    if match:
        return search_start + match.start()

    return -1


def inject_headings(text: str, toc: list[tuple[int, str, int]]) -> str:
    """Inject Markdown headings from TOC entries into the converted text.

    For each TOC entry, finds the corresponding text in the document and
    ensures it has the proper Markdown heading prefix.
    """
    if not toc:
        return text

    lines = text.split("\n")
    result_lines = list(lines)

    # Build a set of insertions: (line_index, heading_prefix)
    for level, title, _page in toc:
        heading_prefix = "#" * level + " "

        # Find the title in the text
        for i, line in enumerate(result_lines):
            stripped = line.strip()

            # Skip if already a heading
            if stripped.startswith("#"):
                continue

            # Check if this line starts with or is the title
            if stripped == title or stripped.startswith(title):
                if stripped == title:
                    # Exact match: replace with heading
                    result_lines[i] = heading_prefix + title
                elif stripped.startswith(title):
                    # Title is prefix of a longer line (title got merged with body text)
                    # Split into heading + body
                    rest = stripped[len(title):].strip()
                    result_lines[i] = heading_prefix + title + "\n\n" + rest
                break

            # Also check for normalized match (whitespace differences)
            normalized_line = re.sub(r"\s+", "", stripped)
            normalized_title = re.sub(r"\s+", "", title)
            if normalized_line == normalized_title:
                result_lines[i] = heading_prefix + title
                break
            if normalized_line.startswith(normalized_title) and len(normalized_title) > 5:
                rest = stripped
                # Try to find where the title ends in the original line
                # Use character-by-character matching ignoring spaces
                ti = 0
                li = 0
                while ti < len(normalized_title) and li < len(stripped):
                    if stripped[li].isspace():
                        li += 1
                        continue
                    if stripped[li] == title[ti] if ti < len(title) else False:
                        ti += 1
                        li += 1
                    else:
                        break
                if ti >= len(normalized_title):
                    rest = stripped[li:].strip()
                    result_lines[i] = heading_prefix + title + "\n\n" + rest
                break

    return "\n".join(result_lines)


def _remove_duplicate_headings(text: str) -> str:
    """Remove plain-text lines that duplicate an immediately preceding Markdown heading.

    Pattern: a `# Heading` line followed (possibly with blank lines) by
    the same text without the `#` prefix.
    """
    lines = text.split("\n")
    result: list[str] = []
    last_heading_text = None

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("#"):
            # Extract heading text
            last_heading_text = stripped.lstrip("#").strip()
            result.append(line)
            continue

        if not stripped:
            result.append(line)
            continue

        # Check if this line duplicates the last heading
        if last_heading_text:
            normalized_line = re.sub(r"\s+", "", stripped)
            normalized_heading = re.sub(r"\s+", "", last_heading_text)
            if normalized_line == normalized_heading:
                # Skip this duplicate line
                continue

        last_heading_text = None
        result.append(line)

    return "\n".join(result)


def convert(pdf_path: str, output_path: str | None = None) -> None:
    pdf = Path(pdf_path)
    if not pdf.exists():
        print(f"Error: File not found: {pdf}", file=sys.stderr)
        sys.exit(1)
    if not pdf.suffix.lower() == ".pdf":
        print(f"Error: Not a PDF file: {pdf}", file=sys.stderr)
        sys.exit(1)

    # Extract text with markitdown
    md = MarkItDown()
    result = md.convert(str(pdf))
    text = result.text_content

    # Inject TOC headings using pymupdf
    toc = _get_toc_headings(str(pdf))
    if toc:
        text = inject_headings(text, toc)
        text = _remove_duplicate_headings(text)

    if output_path:
        out = Path(output_path)
    else:
        out = pdf.with_suffix(".md")

    out.write_text(text, encoding="utf-8")
    print(f"Converted: {pdf} -> {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Output Markdown file path (default: same name with .md)")
    args = parser.parse_args()
    convert(args.pdf, args.output)


if __name__ == "__main__":
    main()
