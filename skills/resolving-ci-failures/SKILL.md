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

### Step 2 — Wait for checks to finish

```bash
gh pr checks <PR_NUMBER> -R <OWNER/REPO> --watch
```

### Step 3 — List failing checks and fetch their logs

```bash
gh pr checks <PR_NUMBER> -R <OWNER/REPO> --json name,bucket,link
```

For each check whose `bucket` is `fail`, extract the run ID from
`link` and fetch only the failed portion of the log:

```bash
gh run view <run-id> --log-failed
```

### Step 4 — Analyze the logs and classify each failure

Read each failed log fetched in Step 3 first — do not check out the branch
or jump to local reproduction before analyzing what the log actually says.
Classify each failure into one of three buckets:

1. **Looks transient** — network blip, infra timeout, rate limit, a flaky
   test with no logic connection to this PR's diff, "connection reset",
   etc. → handle in Step 5 (rerun), no checkout needed for it.
2. **Root cause is clear from the log alone** — a lint/type/build error with
   an explicit file:line and message, a missing secret/env var/permission
   that CI-only config would explain, etc. → form the fix directly from the
   log. Do not spend time reproducing locally just to confirm what the log
   already shows.
3. **Ambiguous** — can't tell the root cause, or can't tell whether a
   candidate fix will actually work, from the log alone → flag it for local
   reproduction in Step 7. That's the only bucket that needs it — don't
   check out the branch for buckets 1 or 2.

If a check can't even be matched to a job in `.github/workflows/*.yml`, or
depends on something local reproduction can't reach (e.g. an external
service only CI can reach), it's undiagnosable regardless of bucket: skip
it, add it to a held-back list, and continue with the rest.

### Step 5 — Rerun transient failures

For every failure classified as transient in Step 4, rerun just that job
instead of touching code:

```bash
gh run rerun <run-id> --failed
```

If a check keeps landing in the transient bucket across multiple rounds
(see Step 9's round count), stop treating it as transient — move it to the
held-back list and report it as flaky rather than rerunning indefinitely.

### Step 6 — Check out the PR branch, if needed

Skip this step entirely if this round's failures are all transient (Step 5
only, nothing to reproduce or commit). Otherwise, before reproducing
anything locally (Step 7) or committing a fix (Step 8), switch your current
working tree to the PR's branch — do not create a git worktree for this:

```bash
gh pr checkout <PR_NUMBER> -R <OWNER/REPO>
```

Check `git status` first:

- **Clean working tree** → run `gh pr checkout` directly.
- **Uncommitted changes present** (unrelated in-progress work) → do not
  silently stash, discard, or spin up a worktree on your own judgment. Stop
  and ask the user how to proceed (stash and restore afterward, commit first,
  or use a worktree in this specific case) before continuing.

Already on the PR's branch from a prior round in this same loop? No need to
check out again — just confirm `git status` is what you left it in.

### Step 7 — Reproduce ambiguous failures locally

For each failure flagged as ambiguous in Step 4:

- Match the failing check name to its job in `.github/workflows/*.yml`. Use
  the step name/order shown in the failed log to find the corresponding
  step's `run:` command (or `uses:` action) in the YAML.
- Run that exact command locally.
- **Reproduces locally** → treat as a real code/logic bug. Fix it, then
  re-run the same command locally and confirm it now passes before moving
  on.
- **Does not reproduce locally** (passes on your machine) → treat as
  CI-environment-specific. Fix directly based on what the log shows — don't
  keep iterating locally against an environment difference you can't
  reproduce.
- **Can't identify the step/command, or it can't run locally** (e.g.
  depends on an external service only CI can reach) → cannot diagnose. Skip
  this check, add it to the held-back list, and continue with the rest.

### Step 8 — Group and commit

Group failures fixed via Step 4's bucket 2 and Step 7's reproduced fixes
that share the same root cause (e.g. the same lint rule violated in
multiple files) into a single logical fix. Apply each group as one commit —
no per-round user approval is needed:

```bash
git add <changed files>
git commit -m "<what was fixed>"
git push
```

Reruns from Step 5 need no commit — they've already been triggered.

### Step 9 — Loop until green or capped

After reruns (Step 5) are triggered and any fixes (Step 8) are pushed, go
back to Step 2 and wait for checks again.

- **All checks pass** → go to Step 10.
- **5 rounds of recheck have been completed without all checks passing** →
  stop and report.
- **This round produced zero fixable failures and zero reruns** (everything
  was undiagnosable) → stop early; further looping won't help.

### Step 10 — Report results

List, one line each:

- Reruns — check name and the transient signal that prompted the rerun
- Applied fixes — commit hash, check name, what was changed
- Skipped checks — check name and why (undiagnosable, flaky, external
  service, etc.)

## Notes

- Never suppress a failure to make it pass (no disabling tests, no
  lint-ignore comments, no skipping steps) — fix the root cause. If a genuine
  suppression seems warranted, stop and ask the user instead of doing it.
- Requires `gh` CLI (`gh auth login`).
