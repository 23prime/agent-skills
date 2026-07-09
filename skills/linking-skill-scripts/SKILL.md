---
name: linking-skill-scripts
description: Symlinks this repo's skills/*/scripts/*.sh files onto PATH as as-<name> commands, so skills can invoke their bundled scripts directly instead of expanding ${CLAUDE_CONFIG_DIR:-$HOME/.claude} paths (which triggers repeated permission prompts). Use when setting up this repo for the first time, after pulling changes that add, rename, or remove bundled scripts, or when a skill reports its as-* command is not found.
---

# Linking Skill Scripts

Symlinks every `skills/*/scripts/*.sh` in this repo into a directory on
`$PATH`, named `as-<script-basename>` (no `.sh` suffix, flat namespace).
Bundled script filenames are kebab-case, matching the `as-` link name
exactly (aside from the prefix). Re-running is safe: it updates existing
links and removes stale ones that point back into this repo but whose
source script no longer exists. It never touches `as-*` entries that point
elsewhere.

## Workflow

### 1. Determine the target directory

Ask the user where to place the symlinks. Default: `~/.local/bin`.

### 2. Run the script

```bash
skills/linking-skill-scripts/scripts/link-scripts.sh <target_dir>
```

Omit `<target_dir>` to use the default (`~/.local/bin`).

### 3. Report results

Summarize what was linked and removed from the script's output. If it
printed a `warning: ... is not on your PATH ...` line, tell the user to add
the target directory to their shell profile, for example:

```bash
export PATH="<target_dir>:$PATH"
```

## Notes

- Re-run this skill any time `skills/*/scripts/*.sh` changes (new scripts,
  renames, removals) — it is idempotent.
- Only symlinks resolving into this repo are ever created or removed;
  unrelated `as-*` commands already on the target directory are left alone.
