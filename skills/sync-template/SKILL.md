---
name: sync-template
description: Sync template-derived repositories by running `git sync-upstream --push` on each. Use when the user asks to sync template repos, run sync-upstream across multiple repos, or sync upstream changes to derived repos.
---

# Sync Template

Iterate over each template-derived repository, run `git sync-upstream --push`, skip failures, and report results.

## Workflow

### 1. Read sync targets

Read the list of repository names from `skills/sync-template/sync_targets.txt` (one name per line, `#` comments and blank lines ignored).

If `sync_targets.txt` does not exist, tell the user to copy `skills/sync-template/sync_targets.example.txt` to `skills/sync-template/sync_targets.txt` and edit it, then stop.

### 2. Run sync on each repository

For each repo name, run the bundled sync script:

```bash
./skills/sync-template/scripts/sync-upstream.sh ~/develop/<repo-name>
```

Run repos **sequentially** (not in parallel) to avoid interleaved output and conflicting git operations.

Capture output and exit code without piping through grep — piping loses the script's exit code:

```bash
output=$(./skills/sync-template/scripts/sync-upstream.sh ~/develop/<repo-name> 2>&1)
exit_code=$?
```

### 3. Report results

After all repos are processed, report a summary table:

| Repository | Result      | Notes                    |
|------------|-------------|--------------------------|
| repo-name  | OK / FAILED | error message if failed  |

For each failed repo, add a recommended action based on the error output:

- Merge conflict → "Resolve conflicts manually in `~/develop/<repo>`, then push"
- Auth/SSH error → "Check SSH key access to the remote"
- Diverged history → "Check `git log` and consider `git reset` or manual rebase"
- Other → quote the last error line from the output

## Notes

- `scripts/sync-upstream.sh` pulls from `upstream/main`, merges, pushes to `origin/main`, deletes `sync-upstream-*` branches (local and remote), and runs `git fetch --prune`
- A non-zero exit code from the script means the repo failed; continue to the next
- Do not abort the loop on failure
