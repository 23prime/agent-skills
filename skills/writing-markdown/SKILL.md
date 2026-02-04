---
name: writing-markdown
description: Write Markdown files that comply with the project's markdownlint rules and editorconfig settings. Use when creating or editing Markdown files (.md) to ensure they pass linting without errors.
---

# Writing Markdown

Write Markdown that passes `markdownlint-cli2` with zero errors, based on the project's configured rules.

## Rules

### Formatting

- Use dashes (`-`) for unordered lists, not asterisks or plus signs (MD004)
- Use asterisks (`*`) for emphasis and strong emphasis, not underscores (MD049, MD050)
- No line length limit (MD013 is disabled)
- UTF-8 encoding, LF line endings, trailing whitespace trimmed, final newline required
- 2-space indentation for Markdown files

### HTML

- `<br>` is the only allowed inline HTML element (MD033)
- All other HTML tags are prohibited

### Tables

- Use consistent spacing around pipes in table columns (MD060)
- Separator rows must have spaces around dashes: `| --- |`, not `|---|`

### General

- Ensure consistent heading levels — do not skip levels (e.g., `##` to `####`)
- Use blank lines before and after headings, code blocks, and lists
- Do not use trailing punctuation in headings
- Fenced code blocks must specify a language identifier

## Verification

After writing or editing Markdown files, run:

```bash
mise run fix-md
mise run check-md
```

If errors remain after auto-fix, manually correct them until `check-md` passes with zero errors.
