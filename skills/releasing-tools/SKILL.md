---
name: releasing-tools
description: Release multiple tool repositories by running each repository's project-local `release` skill. Use when the user asks to release, cut a release, or ship new versions of the tools listed in release_targets.txt.
---

# Releasing Tools

Iterate over each tool repository that has a project-local `release` skill, follow that skill, skip failures, and report results.

## Workflow

### 1. Check release targets

Check that `skills/releasing-tools/release_targets.txt` exists.

If it does not exist, tell the user to copy `skills/releasing-tools/release_targets.example.txt` to `skills/releasing-tools/release_targets.txt` and edit it, then stop.

Each line is a repository name under `~/develop/`. Ignore blank lines and lines starting with `#`. If a repository lacks `.claude/skills/release/SKILL.md`, report it as `SKIPPED` and continue.

### 2. Propose bump levels

For each repository, run the following in `~/develop/<repo>`:

```bash
git fetch origin main --tags --force
git describe --tags --abbrev=0 --match 'v[0-9]*' origin/main
```

Take the tag printed above and list commits since it, substituting the literal value in place of `<latest_tag>`:

```bash
git log <latest_tag>..origin/main --oneline --no-merges
```

Skip repositories with no new commits since the latest tag (`SKIPPED: no changes`).

Propose a level per repository following the table in that repository's `release` skill, present all proposals in one table with reasoning, and get the user's confirmation (or their own choices) **once** for all repositories.

| Repository | Latest tag | Commits | Proposed level |
|------------|------------|---------|----------------|
| repo-name  | v0.1.0     | 3       | minor          |

### 3. Release each repository

Sequentially, for each confirmed repository:

1. Read `~/develop/<repo>/.claude/skills/release/SKILL.md`.
2. Follow its steps with `~/develop/<repo>` as the working directory, using the confirmed level. Do not ask for confirmation again.
3. On any failure, stop that repository, record the error, and continue with the next.

### 4. Report results

| Repository | Result                | Notes                          |
|------------|-----------------------|--------------------------------|
| repo-name  | OK / FAILED / SKIPPED | run URL, or error / reason     |

## Notes

- Repositories run sequentially to avoid conflicting git and `gh` operations.
- Each repository's `release` skill is the source of truth for its steps; this skill only coordinates them.
