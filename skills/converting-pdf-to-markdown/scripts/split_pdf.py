#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pymupdf",
# ]
# ///
"""Split a PDF into multiple files based on TOC top-level headings."""

import argparse
import re
import sys
from pathlib import Path

try:
    import pymupdf
except ImportError:
    print("Error: pymupdf is not installed. Run: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


def sanitize_filename(title: str) -> str:
    """Convert a TOC title to a safe filename."""
    name = re.sub(r"[^\w\s-]", "", title)
    name = re.sub(r"[\s]+", "-", name.strip())
    return name.lower()[:80]


def split_by_toc(pdf_path: str, output_dir: str | None = None, level: int = 1) -> None:
    pdf = Path(pdf_path)
    if not pdf.exists():
        print(f"Error: File not found: {pdf}", file=sys.stderr)
        sys.exit(1)

    doc = pymupdf.open(str(pdf))
    toc = doc.get_toc()

    # Filter entries at the specified level
    entries = [(title, page) for lvl, title, page in toc if lvl == level]

    if not entries:
        print(f"Error: No TOC entries found at level {level}.", file=sys.stderr)
        print("The PDF may not contain bookmarks. Consider converting the entire file.", file=sys.stderr)
        doc.close()
        sys.exit(1)

    out_dir = Path(output_dir) if output_dir else pdf.parent / pdf.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    total_pages = doc.page_count

    for i, (title, start_page) in enumerate(entries):
        # Determine end page (exclusive, 0-indexed)
        if i + 1 < len(entries):
            end_page = entries[i + 1][1] - 2  # 0-indexed inclusive, last page before next section
        else:
            end_page = total_pages - 1  # last page, 0-indexed

        start_idx = start_page - 1  # TOC pages are 1-indexed

        part = pymupdf.open()
        part.insert_pdf(doc, from_page=start_idx, to_page=end_page)

        # Re-map and embed TOC entries that fall within this page range
        page_offset = start_idx  # original 0-indexed start
        part_toc = []
        for lvl, t, pg in toc:
            # pg is 1-indexed in the original document
            if start_page <= pg <= end_page + 1:
                new_pg = pg - start_page + 1  # 1-indexed in the part
                part_toc.append([lvl, t, new_pg])
        if part_toc:
            part.set_toc(part_toc)

        idx = str(i + 1).zfill(2)
        safe_title = sanitize_filename(title)
        out_file = out_dir / f"{idx}-{safe_title}.pdf"
        part.save(str(out_file))
        part.close()

        page_count = end_page - start_idx + 1
        print(f"  {out_file.name} ({page_count} pages)")

    doc.close()
    print(f"\nSplit into {len(entries)} files in {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Split PDF by TOC headings")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("-o", "--output-dir", help="Output directory (default: <pdf-stem>/)")
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        default=1,
        help="TOC heading level to split on (default: 1)",
    )
    args = parser.parse_args()
    split_by_toc(args.pdf, args.output_dir, args.level)


if __name__ == "__main__":
    main()
