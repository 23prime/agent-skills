---
name: resolving-pr-conversations
description: "Resolve GitHub PR review conversations by analyzing reply content. Leaves unanswered threads untouched; for threads with replies, resolves automatically when a fix or intentional-skip is indicated, and asks the user for ambiguous cases. Use when a user wants to clean up PR review threads (e.g. after GitHub Copilot review)."
---

# Resolving PR Conversations

This skill inspects GitHub PR review threads and resolves the ones that are
clearly handled, leaving unanswered threads untouched.

## Workflow

### Step 1 — Identify the PR

Determine `OWNER/REPO` and `PR_NUMBER`:

- **If a PR URL is given** — parse them from the URL.
- **If given explicitly** — use as-is.
- **Otherwise** — detect automatically:

  ```bash
  gh repo view --json nameWithOwner --jq .nameWithOwner  # OWNER/REPO
  gh pr view --json number --jq .number                  # PR_NUMBER
  ```

  If `gh pr view` fails, ask the user to supply a PR URL or number.

### Step 2 — Fetch all review threads

```bash
gh pr-review review view <PR_NUMBER> -R <OWNER/REPO> \
  | jq '[.reviews[]?.comments[]? | {thread_id, path, line, author_login, body, is_resolved, is_outdated, thread_comments}]'
```

This flattens all threads across all reviews into a single array. Each element has:

- `thread_id` — GraphQL node ID (`PRRT_…`), required for resolving
- `path`, `line` — file and line of the inline comment
- `author_login` — reviewer's GitHub login
- `body` — original comment text
- `is_resolved` — `true` when already resolved on GitHub
- `is_outdated` — diff has moved past this comment
- `thread_comments` — array of replies in this thread

### Step 3 — Classify all threads

Apply the following decision rules to every thread (regardless of reviewer):

| Condition | Classification |
| --------- | -------------- |
| `is_resolved: true` | **Already resolved** — skip |
| `thread_comments` is empty | **No reply** — skip (leave untouched) |
| Reply clearly indicates a fix (e.g. "fixed in \<commit\>", "addressed", "修正しました") | **Auto-resolve** |
| Reply clearly indicates intentional skip (e.g. "won't fix", "by design", "意図的です", "対応しません") | **Auto-resolve** |
| Reply is ambiguous or unclear | **Ask user** |

"Clearly indicates" means the reply body contains unambiguous intent. When in
doubt, classify as **Ask user**.

### Step 4 — Present summary, confirm scope and plan in one interaction

Show everything the user needs to decide in a single message, then wait for one
reply:

```text
Unresolved threads by reviewer:

copilot-pull-request-reviewer (1):
  - src/main.rs:73 — "`--json` flag duplication between parent and subcommand"  [No reply]

coderabbitai (2):
  - src/cmd/space.rs:175 — "Consider testing the project fallback..."  [Auto-resolve: "fixed in abc1234"]
  - docs/api.md:7         — "Consider using pathlib here."             [Ask: reply "ok" is ambiguous]

---
Target reviewer: [1] GitHub Copilot only (default) / [2] All reviewers

For ambiguous threads, resolve? (listed below)
  - docs/api.md:7  Copilot: "Consider using pathlib here." / Reply: "ok"  [y/n]
```

Wait for the user to answer all questions in one reply (e.g. "1, y"). Parse:

- Scope selection (1 or 2; default 1 if omitted)
- y/n for each **Ask user** thread

If the user requests changes to the plan, revise and re-present.

After parsing, filter threads by the chosen scope and apply the **Ask user**
answers to form the final list of threads to resolve.

### Step 5 — Resolve approved threads

For each thread approved for resolution, run:

```bash
gh pr-review threads resolve <PR_NUMBER> -R <OWNER/REPO> --thread-id <thread_id>
```

If the command exits with a non-zero status, report the failure and continue
with the remaining threads.

### Step 6 — Report summary

After processing all threads, output one line per thread:

- Resolved: `src/foo.py:42` — "fixed in abc1234"
- Resolved: `src/bar.py:17` — "won't fix: intentional behaviour"
- Skipped (no reply): `src/qux.py:5`
- Already resolved: `src/baz.py:10`
- User declined to resolve: `docs/api.md:7`

## Notes

- Requires `gh` CLI (`gh auth login`) and the `gh-pr-review` extension
  (`gh extension install agynio/gh-pr-review`)
- Only inline review thread comments are fetched; PR-level discussion comments
  are not included
- This skill never posts new replies — it only resolves existing threads
- Resolving threads requires write access to the repository
