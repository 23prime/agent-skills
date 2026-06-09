---
name: sync-template
description: Sync template-derived repositories by running `git sync-upstream --push` on each. Use when the user asks to sync template repos, run sync-upstream across multiple repos, or sync upstream changes to derived repos.
---

# Sync Template

Iterate over each template-derived repository, run `git sync-upstream --push`, skip failures, and report results.

## Workflow

### 1. Check sync targets

Check that `skills/sync-template/sync_targets.txt` exists.

If it does not exist, tell the user to copy `skills/sync-template/sync_targets.example.txt` to `skills/sync-template/sync_targets.txt` and edit it, then stop.

### 2. Run sync-all script

Run the bundled wrapper script **once** — it handles the loop internally:

```bash
./skills/sync-template/scripts/sync-all.sh ./skills/sync-template/sync_targets.txt
```

The script streams progress to stderr and prints a `---RESULTS---` block to stdout with tab-separated lines: `<repo>\t<OK|FAILED>\t<notes>`.

### 3. Report results

Parse the `---RESULTS---` block and render a summary table:

| Repository | Result      | Notes                    |
|------------|-------------|--------------------------|
| repo-name  | OK / FAILED | error message if failed  |

For each failed repo, add a recommended action:

- Merge conflict → "Resolve conflicts manually in `~/develop/<repo>`, then push"
- Auth/SSH error → "Check SSH key access to the remote"
- Diverged history → "Check `git log` and consider `git reset` or manual rebase"
- pre-push hook tool missing → "Install the missing tool or run sync in an environment where it is available"
- Other → quote the notes field from the output

## Notes

- `scripts/sync-upstream.sh` pulls from `upstream/main`, merges, runs `mise run setup` (if `mise.toml` exists) to install any updated tools, pushes to `origin/main`, deletes `sync-upstream-*` branches (local and remote), and runs `git fetch --prune`
- `scripts/sync-all.sh` runs repos sequentially to avoid conflicting git operations and never aborts on failure
