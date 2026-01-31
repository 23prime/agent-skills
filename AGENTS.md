# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project Overview

A toolkit for creating and managing Agent Skills — reusable skill packages that extend Claude's capabilities with specialized workflows, tool integrations, and domain expertise. See [Anthropic official docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

## Setup

Requires [mise](https://mise.jdx.dev).

```sh
mise trust -q && mise install
mise setup
```

## Skill Structure

Each skill lives under `skills/<skill-name>/` and follows this layout:

```txt
skill-name/
├── SKILL.md          # Required: YAML frontmatter (name, description) + instructions
├── scripts/          # Optional: executable code (Python/Bash)
├── references/       # Optional: documentation loaded as needed
└── assets/           # Optional: templates, icons, fonts
```

Skills use progressive disclosure: metadata → SKILL.md body → bundled resources, to manage token usage.

## Common Commands

- **Markdown lint check**: `mise run check-md`
- **Markdown lint fix**: `mise run fix-md`
- **Link skills globally**: `mise run link` — creates a symlink to `~/.claude-23prime/skills`

## Skill Workflow

- **Create**: `uv run python skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-dir>`
- **Validate**: `uv run python skills/skill-creator/scripts/quick_validate.py <path/to/skill-folder>`

## Validation Rules

- Skill name: lowercase, digits, hyphens only (hyphen-case), max 40 chars, no leading/trailing/consecutive hyphens
- SKILL.md must have valid YAML frontmatter with `name` and `description` fields
- Description must not contain angle brackets

## Code Style

- UTF-8, LF line endings, trailing whitespace trimmed, final newline required
- 2-space indentation for YAML, JSON, and Markdown
- Markdown: unordered lists with dashes, emphasis/strong with asterisks, `<br>` is the only allowed HTML element
- Python 3.14+

## Shell Rules

- Always use `rm -f` (never bare `rm`)
- Run `git` commands in the current directory (do not use the `-C` option)
