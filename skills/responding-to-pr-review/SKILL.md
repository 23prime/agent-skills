---
name: responding-to-pr-review
description: "Fetches review comments from a GitHub Pull Request, critically evaluates each comment for correctness and best-practice alignment, then applies only valid suggestions to source code or documentation. After applying fixes, polls until the PR is approved, restarting the review cycle whenever new comments appear. Use when a user provides a PR URL and asks to apply, act on, or implement the review feedback, or wants to iterate until the PR is approved."
---

# Responding to PR Review

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

**If this returns zero comments, check the review decision before concluding
there is nothing to do:**

```bash
gh pr view <PR_NUMBER> -R <OWNER/REPO> --json reviewDecision --jq .reviewDecision
gh pr view <PR_NUMBER> -R <OWNER/REPO> --json reviews --jq '.reviews[] | "[\(.author.login) / \(.state)]\n\(.body)"'
```

When the decision is `CHANGES_REQUESTED` or `COMMENTED` but no inline threads
exist, the reviewer's inline comments failed to post — CodeRabbit says so
explicitly at the top of its review body ("Inline review comments failed to
post"), and its findings are then only in that body, including a section that
lists them per file and line. Treat those findings as the comment list and
evaluate them exactly as step 3 describes.

There are no threads to reply to in this case. Instead of the per-thread
replies in step 5, post one PR-level comment giving the verdict on every
finding:

```bash
gh pr comment <PR_NUMBER> -R <OWNER/REPO> --body-file <path>
```

Use `--body-file` rather than an inline heredoc — a long body is more likely to
collide with a shell-command guard, and it avoids heredoc quoting problems with
backticks and `$`.

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

5. Obtain the commit hash with a **separate** Bash tool call (do **not** use
   `$()` command substitution — run `git rev-parse HEAD` on its own, capture
   the output, then embed it as a literal string in the next call):

   ```bash
   git rev-parse HEAD
   ```

   Then reply to every PR comment that belongs to this commit:

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

- **`APPROVED`** — The PR is approved. This skill is done; control returns
  to the caller.
- **Otherwise** — Run the bundled polling script:

  ```bash
  # Use run_in_background: true to avoid the 10-minute Bash tool timeout
  as-poll-until-approved <PR_NUMBER> <OWNER/REPO>
  ```

  The script polls every 1 minute for up to 4 hours. Exit codes:

  - `0` — PR approved; this skill is done
  - `1` — Timed out after 4 hours; report to the user and stop
  - `2` — New unresolved comments found (never replied to); restart from Step 1
  - `3` — A thread we already replied to has stayed unresolved for 5+
    minutes (e.g. CodeRabbit didn't auto-resolve after our reply). Handle
    per below instead of restarting or waiting blindly.

  **On exit `3`:** the script prints the stuck threads (`thread_id`, `path`,
  `line`, and the latest reply's author/body). Present this to the user —
  including the latest reply content, since it may contain a new CodeRabbit
  suggestion — and propose next steps:

  - If the latest reply is just CodeRabbit acknowledging without resolving,
    propose running the `resolving-pr-conversations` skill for this PR with
    scope `[2]` (all reviewers) — our earlier reply already states the fix,
    so it will auto-resolve under that skill's rules.
  - If the latest reply raises a new, substantive point, treat it like a new
    review comment and restart from Step 1 instead.

  Wait for the user's decision before acting. After resolving (or restarting
  and re-reaching this step), resume polling with `as-poll-until-approved`.

  **`reviewDecision` stuck at `CHANGES_REQUESTED`/`COMMENTED` with all threads
  resolved and no unresolved comments left:** a bot (e.g. CodeRabbit) can
  reply accepting a rebuttal and resolve the thread without submitting a new
  review — `reviewDecision` only changes when the bot submits an actual
  review verdict, and a thread reply/resolve isn't one. Since no new commit
  was pushed, `@coderabbitai review` gets refused ("Already reviewed the last
  commit"); post `@coderabbitai full review` instead to force a fresh review
  pass, then resume polling. Don't restart from Step 1 or poll indefinitely
  in this state — there's nothing left to act on until the bot submits its
  new verdict.

## Notes

- `path` and `line` identify the exact location; read the file directly for
  surrounding context (no `diff_hunk` is provided)
- `gh pr-review review view` returns only inline review thread comments;
  PR-level discussion comments are not included
- Requires `gh` CLI (`gh auth login`) and the `gh-pr-review` extension
  (`gh extension install agynio/gh-pr-review`)
- Ensure the working branch is pushed to a remote before starting so that
  pushed commits are visible in the PR
- Requires `as-poll-until-approved` on `$PATH` — run the
  `linking-skill-scripts` skill once to set this up.
