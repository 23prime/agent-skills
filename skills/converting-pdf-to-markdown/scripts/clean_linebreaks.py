#!/usr/bin/env python3
"""Remove unnecessary line breaks from converted Markdown.

PDFs often insert line breaks for display purposes that don't represent
actual paragraph breaks. This script joins continuation lines while
preserving intentional structure (headings, lists, code blocks, blank lines).

Handles two common patterns:
1. Direct continuation: text line immediately followed by another text line.
2. Single-blank-line continuation: PDF text where every line is separated
   by a blank line. Distinguishes mid-sentence breaks from true paragraph
   breaks by checking whether the preceding line ends mid-sentence.
"""

import argparse
import re
import sys
from pathlib import Path


def is_structural_line(line: str) -> bool:
    """Check if a line is a Markdown structural element that should not be joined."""
    stripped = line.strip()
    if not stripped:
        return True  # blank line (paragraph separator)
    if stripped.startswith("#"):
        return True  # heading
    if re.match(r"^[-*+]\s", stripped):
        return True  # unordered list item
    if re.match(r"^\d+\.\s", stripped):
        return True  # ordered list item
    if stripped.startswith(("```", "~~~")):
        return True  # code fence
    if stripped.startswith("|"):
        return True  # table row
    if stripped.startswith(">"):
        return True  # blockquote
    if re.match(r"^-{3,}$|^\*{3,}$|^_{3,}$", stripped):
        return True  # horizontal rule
    return False


def _is_page_number(line: str) -> bool:
    """Check if a line is just a page number."""
    return bool(re.match(r"^\s*\d{1,4}\s*$", line))


def _looks_like_continuation(prev: str, curr: str) -> bool:
    """Determine if curr is a continuation of prev (mid-sentence break).

    Returns True when prev appears to end mid-sentence, meaning the blank
    line between them was just a PDF display artifact, not a paragraph break.
    """
    prev_stripped = prev.rstrip()
    curr_stripped = curr.strip()

    if not prev_stripped or not curr_stripped:
        return False

    # Previous line ends with a sentence-ending punctuation → paragraph break
    if re.search(r"[。．.！!？?）\)」』】〉》\]:]$", prev_stripped):
        return False

    # Previous line looks like a short heading/title (no sentence-ending punct,
    # relatively short, and not ending with a particle or connective)
    # e.g. "（１）本ガイドラインの目的", "①対象範囲", "第１章 概要"
    if len(prev_stripped) <= 60 and re.match(
        r"^[（(①-⑳❶-❿第０-９0-9]", prev_stripped
    ):
        return False

    # Current line starts with a structural/new-paragraph marker
    if re.match(r"^[（(「『【〈《①-⑳❶-❿※◆●▶■□▸◇★☆]", curr_stripped):
        return False

    # Current line starts with a heading-like pattern (e.g. "第１章", "１．")
    if re.match(r"^(第[０-９一-九]+|[０-９]+[．.]|[0-9]+[．.])", curr_stripped):
        return False

    # Current line looks like a figure/table caption
    if re.match(r"^(図表|図|表)\s*\d", curr_stripped):
        return False

    # Otherwise, prev ended mid-sentence → join
    return True


def clean(text: str) -> str:
    lines = text.split("\n")
    result: list[str] = []
    in_code_block = False
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Toggle code block state
        if stripped.startswith(("```", "~~~")):
            in_code_block = not in_code_block
            result.append(line)
            i += 1
            continue

        # Never modify lines inside code blocks
        if in_code_block:
            result.append(line)
            i += 1
            continue

        # Remove standalone page numbers
        if _is_page_number(line):
            i += 1
            continue

        # Blank line: check if it's a mid-sentence break or real paragraph break
        if not stripped:
            # Look ahead: blank line followed by a text line
            if (
                i + 1 < n
                and lines[i + 1].strip()
                and not is_structural_line(lines[i + 1])
                and not _is_page_number(lines[i + 1])
                and result
                and result[-1].strip()
                and not is_structural_line(result[-1])
            ):
                # Decide based on whether previous line ended mid-sentence
                if _looks_like_continuation(result[-1], lines[i + 1]):
                    # Skip this blank line — next iteration will join the text
                    i += 1
                    continue

            result.append(line)
            i += 1
            continue

        # Structural lines are kept as-is
        if is_structural_line(line):
            result.append(line)
            i += 1
            continue

        # Text line: join to previous if it's a continuation
        if result and result[-1].strip() and not is_structural_line(result[-1]):
            if _looks_like_continuation(result[-1], stripped):
                result[-1] = result[-1].rstrip() + stripped
            else:
                result.append(line)
        else:
            result.append(line)

        i += 1

    return "\n".join(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove unnecessary line breaks from Markdown converted from PDF"
    )
    parser.add_argument("file", help="Markdown file to clean")
    parser.add_argument("-o", "--output", help="Output file (default: overwrite input)")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    cleaned = clean(text)

    out = Path(args.output) if args.output else path
    out.write_text(cleaned, encoding="utf-8")

    if args.output:
        print(f"Cleaned: {path} -> {out}")
    else:
        print(f"Cleaned: {path} (in-place)")


if __name__ == "__main__":
    main()
