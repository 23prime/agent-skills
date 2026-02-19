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

Run the bundled `fetch_pr_comments.py` script with the PR URL or `OWNER/REPO PR_NUMBER`:

```bash
uv run python fetch_pr_comments.py <PR_URL>
# or
uv run python fetch_pr_comments.py owner/repo 42
```

The script outputs JSON with three sections:

- `pr` — title, URL, body
- `review_comments` — inline code comments (file + line + diff hunk)
- `issue_comments` — general discussion comments

### Step 2 — Skip already-handled comments

Before evaluating content, skip any comment that meets any of these conditions:

- **Resolved** (`resolved: true`) — the thread has been marked resolved on GitHub
- **Has replies** (`replies` array is non-empty) — someone has already responded,
  treating it as handled regardless of reply content
- **Outdated** (`outdated: true`) — the diff has moved past this comment; the
  code it referenced no longer exists at that position

Log skipped-as-handled comments in the final summary but do not reply to them.

### Step 3 — Evaluate and group remaining comments

For every remaining comment, read the referenced file and surrounding context, then:

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
   uv run python reply_review_comment.py \
     <owner/repo> <comment_id> "fixed by <commit_hash>"
   ```

   For `issue_comments`, the GitHub API has no threaded-reply endpoint.
   Post a new PR comment that quotes the original instead:

   ```bash
   uv run python post_pr_comment.py \
     <owner/repo> <pr_number> "> @<author>: <original comment body>\n\nfixed by <commit_hash>"
   ```

Repeat this loop — apply → commit → push → reply — for each independent
comment or group before moving to the next.

For each **skipped** comment, reply immediately with the reason:

```bash
uv run python reply_review_comment.py \
  <owner/repo> <comment_id> "No change: <one-sentence reason>"
```

For `issue_comments`, post a new PR comment quoting the original:

```bash
uv run python post_pr_comment.py \
  <owner/repo> <pr_number> "> @<author>: <original comment body>\n\nNo change: <one-sentence reason>"
```

### Step 6 — Report summary

After all comments are processed, output one line per comment:

- Applied (commit `abc1234`): `src/foo.py:42` — Replaced `os.path` with `pathlib.Path`
- Applied (commit `abc1234`): `src/bar.py:17` — Same fix, grouped with above
- Skipped (no change): `docs/api.md:7` — Suggestion uses a removed API (`v1/endpoint`)
- Already handled: `src/baz.py:5` — Has existing replies (not touched)

## Notes

- `review_comments` (inline) include `diff_hunk`, `path`, and `line` for
  locating the exact location in the file
- `issue_comments` are general discussion; only act on them if they contain a
  clear, actionable code/doc change request
- Requires `gh` CLI (`gh auth login`) and `uv`
- Ensure the working branch is pushed to a remote before starting so that
  pushed commits are visible in the PR
