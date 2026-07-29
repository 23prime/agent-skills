# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## General agent rules

- When users ask questions, answer them instead of doing the work.

### Shell Rules

- Always use `rm -f` (never bare `rm`)
- Run `git` commands in the current directory (do not use the `-C` option)

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

Bundled scripts under `scripts/` use kebab-case filenames (e.g.
`poll-until-approved.sh`). Any `scripts/*.sh` file that a `SKILL.md`
workflow invokes directly (not merely reads or references as a path) must
be exposed on `$PATH` rather than called via
`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/...` expansion. Name it
`as-<script-basename-without-extension>` (flat namespace, no per-skill
prefix) and reference it that way in `SKILL.md`. Use the
`linking-skill-scripts` skill to place the symlink.

## Agent Structure

Custom subagents live under `agents/<name>.md` — one flat markdown file per
agent (no per-agent subdirectory), matching Claude Code's own subagent
layout (`~/.claude/agents/*.md`). Frontmatter fields (`name`, `description`,
`model`, `effort`, `color`, `skills`, `tools`) follow Claude Code's subagent
spec. Prefer the `skills:` frontmatter field to preload an existing skill's
content into an agent rather than duplicating its workflow inline, so the
agent stays in sync when the skill changes.

## Common Commands

- **Markdown lint check**: `mise run md-check`
- **Markdown lint fix**: `mise run md-fix`
- **Link skills globally**: `mise run link` — creates a symlink to `~/.claude/skills`

## Validation Rules

- Skill name: lowercase, digits, hyphens only (hyphen-case), max 40 chars, no leading/trailing/consecutive hyphens
- SKILL.md must have valid YAML frontmatter with `name` and `description` fields
- Description must not contain angle brackets

## Code Style

- UTF-8, LF line endings, trailing whitespace trimmed, final newline required
- 2-space indentation for YAML, JSON, and Markdown
- Markdown: unordered lists with dashes, emphasis/strong with asterisks, `<br>` is the only allowed HTML element
- Python 3.14+
