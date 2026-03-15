---
name: implementing-pr-review
description: "Fetches review comments from a GitHub Pull Request, critically evaluates each comment for correctness and best-practice alignment, then applies only valid suggestions to source code or documentation. After applying fixes, polls until the PR is approved, restarting the review cycle whenever new comments appear. Use when a user provides a PR URL and asks to apply, act on, or implement the review feedback, or wants to iterate until the PR is approved."
---

# Implementing PR Review

This skill fetches GitHub PR review comments, judges each one for validity,
applies the valid ones to the codebase, and replies to each comment with the
fix commit hash. Comments may be incorrect or reflect outdated practices —
always evaluate before changing code.

## Workflow

### Step 1 — Fetch PR comments

Determine `OWNER/REPO` and `PR_NUMBER` as follows:

- **If a PR URL is given** — parse `OWNER/REPO` and `PR_NUMBER` from the URL.
- **If `OWNER/REPO` and `PR_NUMBER` are given explicitly** — use them as-is.
- **Otherwise** — detect automatically from the current working directory:

  ```bash
  gh repo view --json nameWithOwner --jq .nameWithOwner  # OWNER/REPO
  gh pr view --json number --jq .number                  # PR_NUMBER
  ```

  If `gh pr view` fails (no PR found for the current branch), ask the user to provide the PR URL or number.

Then run:

```bash
gh pr-review review view <PR_NUMBER> -R <OWNER/REPO>
```

This outputs a JSON object with a `reviews` array. Flatten all inline review
comments with:

```bash
gh pr-review review view <PR_NUMBER> -R <OWNER/REPO> | jq '[.reviews[]?.comments[]?]'
```

Each comment has these fields:

- `thread_id` — GraphQL thread node ID (`PRRT_...`), used when replying
- `path`, `line` — file and line number of the inline comment
- `author_login` — reviewer's GitHub login
- `body` — comment text
- `is_resolved` — `true` when the thread has been resolved on GitHub
- `is_outdated` — `true` when the diff has moved past this comment
- `thread_comments` — array of replies already posted in this thread

### Step 2 — Skip already-handled comments

Before evaluating content, skip any comment that meets any of these conditions:

- **Resolved** (`is_resolved: true`) — thread marked resolved on GitHub
- **Outdated** (`is_outdated: true`) — the diff has moved past this comment
- **Has replies** (`thread_comments` array is non-empty) — already responded to

Log skipped-as-handled comments in the final summary but do not reply to them.

### Step 3 — Evaluate and group remaining comments

For every remaining comment, read the referenced file at `path`:`line` and
surrounding context, then:

**Accept if ALL of the following are true:**

- The suggestion is technically correct for the language/framework in use
- It follows current best practices (not deprecated patterns)
- It is consistent with the existing code style and project conventions
- It improves correctness, clarity, performance, or security — not just personal
  preference

**Skip and explain if ANY of the following are true:**

- The suggestion contains a factual error (wrong API, wrong behaviour)
- It recommends a deprecated or outdated approach
- It conflicts with existing project conventions without a clear benefit
- It is purely stylistic with no objective improvement

**Group related comments before applying:**

Comments that raise the same issue across multiple locations (e.g. "use
`pathlib` instead of `os.path`" mentioned in three files) count as one logical
fix. Group them into a single commit. Apply all locations in one pass, then
commit and reply to each grouped comment.

### Step 4 — Confirm plan with user

Before making any changes, present the full plan and wait for approval:

```text
## Review plan

**Will apply (N comments/groups):**
- [group] src/foo.py:42, src/bar.py:17 — Replace `os.path` with `pathlib.Path`
- src/baz.py:10 — Add missing null check

**Will skip — no change (N comments):**
- docs/api.md:7 — Suggestion uses a removed API (`v1/endpoint`)

**Already handled — no action (N comments):**
- src/qux.py:5 — Has existing replies

Proceed?
```

Do not apply any changes until the user confirms. If the user requests adjustments
(e.g. skip a specific comment, reconsider a verdict), revise the plan and ask again.

### Step 5 — Apply, commit, push, and reply — one commit per (group of) comment(s)

For each accepted comment or group:

1. Read the full target file(s) to understand context
2. Apply the minimal change that satisfies the feedback — do not refactor
   surrounding code beyond the comment's scope
3. Commit with a concise message that references the PR comment content:

   ```bash
   git add <changed files>
   git commit -m "<what was done>" -m "Addresses review comment: <short quote>"
   ```

4. Push immediately after each commit:

   ```bash
   git push
   ```

5. Reply to every PR comment that belongs to this commit using the full commit
   hash obtained from `git rev-parse HEAD`:

   ```bash
   gh pr-review comments reply <PR_NUMBER> -R <OWNER/REPO> \
     --thread-id <thread_id> --body "fixed by <commit_hash>"
   ```

Repeat this loop — apply → commit → push → reply — for each independent
comment or group before moving to the next.

For each **skipped** comment, reply immediately with the reason:

```bash
gh pr-review comments reply <PR_NUMBER> -R <OWNER/REPO> \
  --thread-id <thread_id> --body "No change: <one-sentence reason>"
```

### Step 6 — Report summary

After all comments are processed, output one line per comment:

- Applied (commit `abc1234`): `src/foo.py:42` — Replaced `os.path` with `pathlib.Path`
- Applied (commit `abc1234`): `src/bar.py:17` — Same fix, grouped with above
- Skipped (no change): `docs/api.md:7` — Suggestion uses a removed API (`v1/endpoint`)
- Already handled: `src/baz.py:5` — Has existing replies (not touched)

### Step 7 — Resolve GitHub Copilot review threads

After the summary, invoke the `resolving-pr-conversations` skill for the same
PR, targeting GitHub Copilot only (scope `[1]`). Pass the already-known
`OWNER/REPO` and `PR_NUMBER` so the skill skips PR detection. Skip the scope
prompt by defaulting to `[1]`.

### Step 8 — Check approval and loop

After resolving conversations, check the PR's review decision:

```bash
gh pr view <PR_NUMBER> -R <OWNER/REPO> --json reviewDecision --jq .reviewDecision
```

- **`APPROVED`** — The PR is approved. Proceed to Step 9.
- **Otherwise** — Run the bundled polling script:

  ```bash
  "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/implementing-pr-review/scripts/poll_until_approved.sh" <PR_NUMBER> <OWNER/REPO>
  ```

  The script polls every 5 minutes for up to 4 hours. On timeout, it posts
  a single `` `@coderabbitai` resolve `` comment before exiting. Exit codes:

  - `0` — PR approved; proceed to Step 9
  - `1` — Timed out after 4 hours; report to the user and stop
  - `2` — New unresolved comments found; restart from Step 1

### Step 9 — Merge the PR

After the PR is approved, wait for all required checks to pass:

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

### Step 10 — Clean up topic branch

After merging, clean up the topic branch locally and remotely:

```bash
"${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/implementing-pr-review/scripts/clean_topic_branch.sh"
```

The script switches to the default branch, pulls the latest changes, and
deletes the topic branch both locally and from the remote.

## Notes

- `path` and `line` identify the exact location; read the file directly for
  surrounding context (no `diff_hunk` is provided)
- `gh pr-review review view` returns only inline review thread comments;
  PR-level discussion comments are not included
- Requires `gh` CLI (`gh auth login`) and the `gh-pr-review` extension
  (`gh extension install agynio/gh-pr-review`)
- Ensure the working branch is pushed to a remote before starting so that
  pushed commits are visible in the PR
