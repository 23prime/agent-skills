---
name: resolving-ci-failures
description: Use when a pull request has failing CI checks — lint, format, type-check, test, or build failures — that need to be diagnosed and fixed to get CI green.
---

# Resolving CI Failures

Diagnose failing CI checks on a pull request, fix them, and push — looping until
all checks pass or a retry limit is reached. Applies fixes without asking for
per-round approval; only the final summary requires review.

## Workflow

### Step 1 — Determine PR and repository

Same detection as `responding-to-pr-review`:

- **If a PR URL is given** — parse `OWNER/REPO` and `PR_NUMBER` from the URL.
- **If `OWNER/REPO` and `PR_NUMBER` are given explicitly** — use them as-is.
- **Otherwise** — detect automatically:

  ```bash
  gh repo view --json nameWithOwner --jq .nameWithOwner  # OWNER/REPO
  gh pr view --json number --jq .number                  # PR_NUMBER
  ```

  If `gh pr view` fails, ask the user for the PR URL or number.

### Step 2 — Check out the PR branch

Switch your current working tree to the PR's branch — do not create a git
worktree for this:

```bash
gh pr checkout <PR_NUMBER> -R <OWNER/REPO>
```

Check `git status` first:

- **Clean working tree** → run `gh pr checkout` directly.
- **Uncommitted changes present** (unrelated in-progress work) → do not
  silently stash, discard, or spin up a worktree on your own judgment. Stop
  and ask the user how to proceed (stash and restore afterward, commit first,
  or use a worktree in this specific case) before continuing.

### Step 3 — Wait for checks to finish

```bash
gh pr checks <PR_NUMBER> -R <OWNER/REPO> --watch
```

### Step 4 — List failing checks and fetch their logs

```bash
gh pr checks <PR_NUMBER> -R <OWNER/REPO> --json name,bucket,link
```

For each check whose `bucket` is `fail`, extract the run ID from
`link` and fetch only the failed portion of the log:

```bash
gh run view <run-id> --log-failed
```

### Step 5 — Reproduce locally first, then classify

For each failure, **always attempt local reproduction before guessing at a
cause**. Do not classify from log content alone — decide based on whether the
failure actually reproduces.

1. Match the failing check name to its job in `.github/workflows/*.yml`. Use
   the step name/order shown in the failed log to find the corresponding
   step's `run:` command (or `uses:` action) in the YAML.
2. Run that exact command locally.
3. Branch on the result:
   - **Reproduces locally** → treat as a real code/logic bug. Fix it, then
     re-run the same command locally and confirm it now passes before moving on.
   - **Does not reproduce locally** (passes on your machine) → treat as
     CI-environment-specific (missing secret, OS/path difference, permissions,
     cache, network access, etc.). Fix directly based on what the log shows —
     there is nothing to run locally to confirm.
   - **Can't identify the step/command, or it can't run locally** (e.g.
     depends on an external service only CI can reach) → cannot diagnose.
     Skip this check, add it to a held-back list, and continue with the rest.

### Step 6 — Group and commit

Group failures that share the same root cause (e.g. the same lint rule
violated in multiple files) into a single logical fix. Apply each group as one
commit — no per-round user approval is needed:

```bash
git add <changed files>
git commit -m "<what was fixed>"
git push
```

### Step 7 — Loop until green or capped

After pushing, go back to Step 3 and wait for checks again.

- **All checks pass** → go to Step 8.
- **5 rounds of push-and-recheck have been completed without all checks
  passing** → stop and report.
- **This round produced zero fixable failures** (everything was
  undiagnosable) → stop early; further looping won't help.

### Step 8 — Report results

List, one line each:

- Applied fixes — commit hash, check name, what was changed
- Skipped checks — check name and why (undiagnosable, flaky, external
  service, etc.)

## Notes

- Never suppress a failure to make it pass (no disabling tests, no
  lint-ignore comments, no skipping steps) — fix the root cause. If a genuine
  suppression seems warranted, stop and ask the user instead of doing it.
- Requires `gh` CLI (`gh auth login`).
