---
name: update-agent-rules
description: Update AGENTS.md based on the current state of the repository. This skill should be used when repository configuration, structure, or tooling has changed and AGENTS.md needs to reflect those changes.
---

# Update Agent Rules

## Overview

This skill updates AGENTS.md — the single source of truth (SSoT) for AI coding agent instructions in the repository. Other agent rule files (CLAUDE.md, .github/copilot-instructions.md) reference AGENTS.md via directives like `@AGENTS.md`, so keeping AGENTS.md accurate is sufficient to keep all agents in sync.

## Workflow

### 1. Gather current state

Read the following files to understand what has changed:

- `AGENTS.md` — current agent rules
- `pyproject.toml` — project metadata, dependencies, Python version
- `mise.toml` — tools and tasks
- `lefthook.yml` — git hooks
- `.editorconfig` — code style settings
- `.markdownlint-cli2.jsonc` — markdown lint rules
- `README.md` — project description and setup instructions

Also scan `skills/` for any new or removed skills that affect the Skill Workflow section.

### 2. Identify deltas

Compare the current AGENTS.md content against the gathered state. Focus on:

- **Project Overview** — description, links
- **Setup** — prerequisites, commands
- **Skill Structure** — directory layout conventions
- **Skill Workflow** — create/validate/package commands
- **Validation Rules** — naming, frontmatter requirements
- **Code Style** — formatting, indentation, linting rules

### 3. Apply updates

Edit AGENTS.md to reflect the current state. Follow these principles:

- Keep it concise — only information that is non-obvious and useful to AI agents
- Do not repeat information that can be easily discovered by reading individual files
- Do not add generic development advice
- Preserve the existing section structure unless a structural change is warranted
- Use the same code style as the rest of the repository (dashes for lists, asterisks for emphasis)

### 4. Verify references

Confirm that files referencing AGENTS.md still work correctly:

- `CLAUDE.md` should contain `@AGENTS.md`
- `.github/copilot-instructions.md` should contain `@AGENTS.md`

If these files do not exist or have stale content, update them.
