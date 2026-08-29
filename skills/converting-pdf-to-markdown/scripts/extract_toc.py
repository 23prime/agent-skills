#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pymupdf",
# ]
# ///
"""Extract TOC (bookmarks) and page count from a PDF file."""

import argparse
import json
import sys
from pathlib import Path

try:
    import pymupdf
except ImportError:
    print("Error: pymupdf is not installed. Run: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


def extract_toc(pdf_path: str) -> None:
    pdf = Path(pdf_path)
    if not pdf.exists():
        print(f"Error: File not found: {pdf}", file=sys.stderr)
        sys.exit(1)

    doc = pymupdf.open(str(pdf))
    page_count = doc.page_count
    toc = doc.get_toc()  # [[level, title, page], ...]
    doc.close()

    result = {
        "file": str(pdf),
        "page_count": page_count,
        "toc": [{"level": level, "title": title, "page": page} for level, title, page in toc],
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract TOC and page count from PDF")
    parser.add_argument("pdf", help="Path to the PDF file")
    args = parser.parse_args()
    extract_toc(args.pdf)


if __name__ == "__main__":
    main()
