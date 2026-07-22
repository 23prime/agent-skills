---
name: retrospective
description: Use after a GitHub Issue's PR is approved (or standalone at any time) to extract reusable knowledge from the current session — generalizable review feedback, rules that weren't followed, and friction points the agent noticed — and route each item to CLAUDE.md/AGENTS.md/.claude/rules, auto-memory, or the relevant skill's SKILL.md.
---

# Retrospective

Reflect on the current conversation for one GitHub Issue's work — from the
start of implementation through its PR being approved — and turn what was
learned into durable instructions and memory, instead of letting it evaporate
at session end.

This skill only reflects on content already present in the conversation. It
does not fetch external history (e.g. `gh api`/`gh pr-review` review
comments) — if that context matters, make sure it already surfaced in this
session (for example, via `responding-to-pr-review`, which reads and replies
to PR comments before approval).

## Workflow

### 1. Gather knowledge

Reflect over the full conversation and produce candidate findings in three
categories. Skip a category entirely if nothing qualifies — do not force
findings to hit a quota.

1. **Generalizable review feedback** — points raised by the user, a
   subagent (e.g. `review-and-fix`), or a tool (lint/CI) during this session
   that would also apply to unrelated future tasks. Exclude feedback that
   only makes sense for this specific PR's code (e.g. "rename this local
   variable").
2. **Unfollowed rules** — re-read the project's `CLAUDE.md`, `AGENTS.md`,
   and `.claude/rules/*.md` (if present) and compare against what actually
   happened in the session. Note any instance where an existing rule was
   violated or overlooked.
3. **Agent friction points** — mistakes, wrong assumptions, or debugging
   detours the agent itself hit during the session. Pay particular
   attention to friction traceable to a specific skill's instructions being
   unclear, incomplete, or missing a case that came up.

For each candidate, write down: a one-line description, why it matters (the
concrete consequence if unaddressed), and — for friction points — which
skill (if any) it traces back to.

### 2. Classify destination

Assign each candidate exactly one destination, based on its nature:

| Finding shape | Destination |
| --- | --- |
| Always-relevant project rule, not AGENTS.md-governed | `CLAUDE.md` / `.claude/rules/` |
| Always-relevant project rule that belongs in the AGENTS.md SSoT | `AGENTS.md` |
| User preference, working style, or project-specific fact (not a project-wide rule) | auto-memory |
| Gap in a specific skill's instructions | that skill's `SKILL.md` |

If a finding could plausibly fit two destinations, pick the narrower one
(e.g. prefer a specific skill's `SKILL.md` over a generic rule file when the
friction is specific to that skill's workflow).

### 3. Present for approval

Show the full candidate list in one message, grouped by destination, e.g.:

```text
## Retrospective findings

**CLAUDE.md / .claude/rules:**
1. [description] — [why it matters]

**AGENTS.md:**
(none)

**auto-memory:**
2. [description] — [why it matters]

**SKILL.md (review-and-fix):**
3. [description] — [why it matters]

Apply all? Reply with adjustments (drop an item, edit wording, change a
destination) or approve as-is.
```

Wait for the user's response. Apply any requested edits and re-confirm only
if the changes are substantial; minor wording tweaks don't need a second
round.

### 4. Apply approved items

Once approved, apply every remaining item, grouped by destination:

- **CLAUDE.md / .claude/rules items** — invoke the `organizing-claude-memory`
  skill, passing the finalized instruction text for each item.
- **AGENTS.md items** — invoke the `updating-agent-rules` skill, passing the
  finalized instruction text for each item.
- **auto-memory items** — write directly, following this environment's
  existing auto-memory format (a frontmatter Markdown file under the memory
  directory, plus a one-line pointer added to `MEMORY.md`). Use the same
  `type` classification (user/feedback/project/reference) that format
  defines. Check for an existing memory file to update before creating a
  new one.
- **SKILL.md items** — invoke the `writing-skills` skill, passing the target
  skill name and the proposed fix.

Do not commit anything. Leave all file changes (CLAUDE.md, AGENTS.md,
`.claude/rules/*.md`, `SKILL.md` files) uncommitted in the working tree —
the caller (e.g. `responding-to-pr-review`) is responsible for committing.
Auto-memory writes need no commit; they live outside the repo.

### 5. Report

Summarize what was written and where, one line per item:

```text
- CLAUDE.md: <one-line summary>
- AGENTS.md: (none)
- auto-memory: <memory file name> — <one-line summary>
- skills/review-and-fix/SKILL.md: <one-line summary>
```

## Important

- Never edit `CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`, or another
  skill's `SKILL.md` directly — always delegate to the owning skill so its
  own conventions and conflict checks apply.
- Batch approval, not per-item — ask once with the full list.
- If nothing qualifies in any category, say so and stop; do not invent
  findings to fill the report.
