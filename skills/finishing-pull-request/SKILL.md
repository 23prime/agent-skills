---
name: finishing-pull-request
description: Use when a Pull Request has been approved and all required checks are expected to pass, to merge it and clean up the topic branch afterward.
---

# Finishing a Pull Request

Merge an approved PR and clean up its topic branch. This skill assumes the
PR is already `APPROVED` — it does not fetch or evaluate review comments.

## Workflow

### Step 1 — Merge the PR

Wait for all required checks to pass:

```bash
gh pr checks <PR_NUMBER> -R <OWNER/REPO> --watch
```

If checks fail, report to the user and stop.

If checks pass, ask the user for confirmation before merging:

```text
All checks passed. Merge PR #<PR_NUMBER>? [y/N]
```

On confirmation, run:

```bash
gh pr merge <PR_NUMBER> -R <OWNER/REPO> --merge
```

### Step 2 — Clean up the topic branch

After merging, clean up the topic branch locally and remotely:

```bash
as-clean-topic-branch
```

The script switches to the default branch, pulls the latest changes, and
deletes the topic branch both locally and from the remote.

## Notes

- Requires `as-clean-topic-branch` on `$PATH` — run the
  `linking-skill-scripts` skill once to set this up.
