---
name: merge-bot-prs
description: Use when bot-created PRs (e.g. mise-upgrade-bot, renovate) have accumulated in GitHub notifications and need batch CI verification and merging.
---

# merge-bot-prs

Batch review and merge bot PRs from GitHub notifications: filter by author, verify all CI checks passed, confirm with the user, then approve and squash-merge.

## Workflow

1. Run `check.sh` — fetches notifications, filters by bot author, checks CI status
2. Present a structured report to the user and wait for explicit confirmation
3. Run `merge.sh` — approves (with "LGTM") and squash-merges each OK PR

## Scripts

### check.sh

```sh
# Default: BOT_USER=mise-upgrade-bot[bot], OUTPUT_FILE=/tmp/merge-bot-ok-prs.txt
./skills/merge-bot-prs/scripts/check.sh

# Override bot user
BOT_USER=renovate[bot] ./skills/merge-bot-prs/scripts/check.sh
```

A PR is **OK** when: author matches `BOT_USER`, PR is open and unmerged, all check runs completed, none failed (skipped/neutral allowed).

### merge.sh

```sh
./skills/merge-bot-prs/scripts/merge.sh
```

## User Confirmation Step

After `check.sh`, present this report format and ask before running `merge.sh`:

```text
Check results: 24 PRs found — 22 OK / 2 NG

OK (to be merged):
  Repository           | PR   | Title
  23prime/foo          | #12  | deps: Upgrade node to 26.2.0
  ...

NG (skipped):
  Repository           | PR   | Title                    | Reason
  23prime/bar          | #34  | deps: Upgrade lefthook   | CI failed=1
  ...

Proceed to approve and merge the 22 OK PRs?
```

Only proceed after the user explicitly confirms.
