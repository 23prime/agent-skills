---
name: auditing-auto-memory
description: Use when the user wants to review, clean up, or prune the current project's auto-memory files — checking for stale, contradicted, or superseded entries.
---

# Auditing Auto Memory

Review the current project's auto-memory directory and flag entries that no
longer hold, so the user can clean them up before they mislead a future
session. This skill only audits the current project's own memory — it never
touches another project's memory directory.

## Workflow

### 1. Locate the memory directory

1. If `autoMemoryDirectory` is set in any applicable `settings.json` scope,
   use that.
2. Otherwise, resolve it the same way Claude Code does: derived from the
   current git repository, under `~/.claude/projects/<project>/memory/` (or
   the active profile's equivalent config directory).

If the directory doesn't exist or contains no memory files, tell the user
there is nothing to audit and stop.

### 2. Collect

Read every memory file in the directory, plus `MEMORY.md`. Each file's
frontmatter declares its `type`: `user`, `feedback`, `project`, or
`reference`.

### 3. Verify, by type

**`project`** — review every one, every run:

- Extract concrete, checkable references from the body — file paths,
  symbols, branch names, command names — and check each with `grep`/`fd`/
  `git log` as appropriate.
- Flag hedged or point-in-time language (e.g. "investigating", "for now",
  "temporarily", "currently") as needing a fresh look, regardless of
  whether its references still resolve.
- A reference that no longer resolves (deleted file, renamed symbol,
  vanished branch) is flagged as contradicted — never drop it silently.

**`user`, `feedback`, `reference`** — trusted by default, not re-verified
wholesale. Flag only when:

- **Superseded** — the memory's content has since been formalized in
  `SKILL.md`, `CLAUDE.md`, `AGENTS.md`, or `.claude/rules/*.md`, making the
  memory redundant.
- **Contradicted** — it disagrees with another memory file in this same
  directory.

Do not investigate whether a `user`/`feedback`/`reference` claim is still
true beyond these two checks — that's out of scope for this skill.

### 4. Present findings

Show the full candidate list in one batch — only flagged entries, not every
file checked. For each: the file, the reason (contradicted / superseded /
stale-language / duplicate), the evidence found, and a proposed action
(delete, update content, merge into another entry, or keep as-is).

```text
## Auto-memory audit

Checked N files, M flagged.

1. project_sync_template_mise_lock.md — stale-language ("investigating")
   Proposed: ask user for current status, update or delete.

2. project_resolving_issue_model_split.md — superseded
   Now documented in skills/resolving-github-issue/SKILL.md.
   Proposed: delete.

Apply all? Reply with adjustments (keep an item, edit the action, override
the reason) or approve as-is.
```

Wait for the user's response before applying anything.

### 5. Apply

For each approved action:

- **Delete** — remove the memory file; remove its pointer line from
  `MEMORY.md`.
- **Update content** — edit the memory file's body (and its `description`
  in frontmatter if it changed); update the corresponding `MEMORY.md` line
  if the one-line summary changed.
- **Merge** — fold the content into the target entry, then delete the
  merged-away file and its `MEMORY.md` line.
- **Keep as-is** — no change.

No commit step: auto memory lives outside the git repository.

### 6. Report

Summarize: files checked, files flagged, actions taken — one line per
action.

## Important

- `project`-type memories are checked in full every run; `user`/`feedback`/
  `reference` are only flagged for contradiction or supersession, never
  re-litigated for correctness.
- Batch approval, not per-item — present the full candidate list once.
- Never silently delete or edit a memory file without the user's approval
  from step 4.
