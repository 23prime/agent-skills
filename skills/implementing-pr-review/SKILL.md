---
name: implementing-pr-review
description: "Fetches review comments from a GitHub Pull Request, critically evaluates each comment for correctness and best-practice alignment, then applies only valid suggestions to source code or documentation. Use when a user provides a PR URL and asks to apply, act on, or implement the review feedback."
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
comments by iterating `reviews[].comments[]`. Each comment has these fields:

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

## Notes

- `path` and `line` identify the exact location; read the file directly for
  surrounding context (no `diff_hunk` is provided)
- `gh pr-review review view` returns only inline review thread comments;
  PR-level discussion comments are not included
- Requires `gh` CLI (`gh auth login`) and the `gh-pr-review` extension
  (`gh extension install agynio/gh-pr-review`)
- Ensure the working branch is pushed to a remote before starting so that
  pushed commits are visible in the PR
