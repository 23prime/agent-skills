---
name: converting-pdf-to-markdown
description: Convert PDF files to Markdown using markitdown. Use when users want to convert a PDF to Markdown, extract text from PDFs, or transform PDF documents into readable Markdown format.
---

# Converting PDF to Markdown

Lightweight PDF-to-Markdown conversion using Microsoft's markitdown library.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) must be installed.

Scripts declare their own dependencies via PEP 723 inline metadata and are run with
`uv run`, so no manual package installation is needed.

## Workflow

### Step 1: Check page count and TOC

Before converting, run the TOC extraction script:

```bash
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/extract_toc.py" input.pdf
```

Output is JSON with `page_count` and `toc` (bookmark entries with level, title, page).

### Step 2: Decide whether to split

- **100 pages or fewer**: Convert the entire file. Go to Step 3.
- **Over 100 pages with TOC**: Present the TOC structure to the user and recommend splitting by top-level headings. After user confirmation, split with:

```bash
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/split_pdf.py" input.pdf
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/split_pdf.py" input.pdf -o output_dir/
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/split_pdf.py" input.pdf -l 2  # split on level-2 headings
```

This creates numbered PDF files (e.g., `01-introduction.pdf`) in a subdirectory. Convert each part separately with Step 3.

- **Over 100 pages without TOC**: Inform the user that there are no bookmarks for automatic splitting. Suggest converting as-is or ask for manual page ranges.

### Step 3: Convert

```bash
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/convert_pdf.py" input.pdf
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/convert_pdf.py" input.pdf -o output.md
```

Default output is `input.md` in the same directory. Use `-o` to specify a custom path.

### Step 4: Clean up line breaks

PDF text wraps at display boundaries, leaving unnecessary line breaks in the Markdown. Always run the cleanup script after conversion:

```bash
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/clean_linebreaks.py" output.md
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/clean_linebreaks.py" output.md -o cleaned.md
```

Without `-o`, the file is overwritten in-place. The script joins continuation lines while preserving headings, lists, code blocks, tables, and paragraph separators.

### Step 5: Review

Check the output for remaining issues:

- Broken headings or formatting artifacts
- Unwanted page numbers or headers/footers
- Table formatting issues
