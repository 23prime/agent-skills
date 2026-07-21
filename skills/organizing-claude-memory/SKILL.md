---
name: organizing-claude-memory
description: Use when the user wants to add a new instruction to CLAUDE.md or .claude/rules/, or when CLAUDE.md has grown large and needs to be reorganized into topic-scoped rules.
---

# Organizing CLAUDE.md and .claude/rules/

Decide where a project instruction belongs — `CLAUDE.md` or a topic-scoped file
under `.claude/rules/` — and keep the two in sync as the project's instructions
grow. Scope is project-level only: `./CLAUDE.md` (or `./.claude/CLAUDE.md`) and
`./.claude/rules/`. See the [official memory docs](https://code.claude.com/docs/en/memory)
for the underlying mechanics (load order, `paths` frontmatter, size limits).

## Workflow

### 1. Inspect the current state and determine the mode

- Read `./CLAUDE.md` and `./.claude/CLAUDE.md` if either exists.
- List `./.claude/rules/*.md` (recursive) and read each file's frontmatter and content.
- Note each file's line count — `CLAUDE.md` over ~200 lines is a signal it should shed content into rules.
- **Adding a new instruction** — go to step 2.
- **Reorganizing an already-bloated `CLAUDE.md`**, either because the user asked or because it's over ~200 lines with multiple distinct topics — go to step 3.

### 2. Place a new instruction

For each new instruction, decide where it belongs:

- **Always relevant, project-wide** (build commands, architecture, naming conventions) → append to `CLAUDE.md`.
- **Relevant only for specific files or directories** (e.g., API handler conventions, test conventions) → new or existing file under `.claude/rules/<topic>.md` with a `paths` frontmatter glob scoping it.
- **A cohesive topic worth its own file even without path-scoping** (e.g., security requirements that apply everywhere but are long) → new file under `.claude/rules/<topic>.md` with no `paths` field, so it loads unconditionally like `CLAUDE.md`.

### 3. Propose a reorganization

Group `CLAUDE.md`'s content by topic. For each group that is self-contained and either large or scoped to specific file types, propose extracting it into `.claude/rules/<topic>.md`, adding `paths` frontmatter when the content only applies to matching files. Keep in `CLAUDE.md` only what must be visible unconditionally in every session (short, high-level rules).

### 4. Check for conflicts and duplication

Before finalizing, compare the proposed content against every existing `CLAUDE.md` and `.claude/rules/*.md` file. Flag contradictions or duplicated rules and confirm with the user which version should win.

### 5. Tighten the wording

Before presenting the plan, rewrite any vague instruction into something concrete enough to verify — e.g. "Use 2-space indentation" instead of "Format code properly", "Run `npm test` before committing" instead of "Test your changes". Group related instructions under markdown headers and bullets rather than dense paragraphs.

### 6. Present the plan and confirm

Show the proposed changes as a diff (new file contents, or the specific addition/edit) and wait for user approval before touching any file.

### 7. Apply changes

After approval, create or edit the files. If the project has a Markdown lint task (e.g. `mise run md-fix`), run it and fix any issues before reporting completion.

## Important

- Never write to `CLAUDE.md` or `.claude/rules/` without explicit user approval of the proposed diff.
- Don't move content into `.claude/rules/` just because it *could* be there — only when it's topic-scoped, path-scoped, or needed to bring `CLAUDE.md` back under the size guideline.
- Rules without `paths` frontmatter load every session, same as `CLAUDE.md` — don't scope-narrow content that's genuinely needed everywhere just to make it a "rule".
