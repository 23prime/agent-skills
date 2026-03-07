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
gh pr-review review view <PR_NUMBER> -R <OWNER/REPO>
```

Flatten every thread by iterating `reviews[].comments[]`. Each comment has:

- `thread_id` — GraphQL node ID (`PRRT_…`), required for resolving
- `path`, `line` — file and line of the inline comment
- `author_login` — reviewer's GitHub login
- `body` — original comment text
- `is_resolved` — `true` when already resolved on GitHub
- `is_outdated` — diff has moved past this comment
- `thread_comments` — array of replies in this thread

Then display a summary of unresolved threads grouped by reviewer, for example:

```text
Unresolved threads:

copilot-pull-request-reviewer (1):
  - src/main.rs:73 — "`--json` flag duplication between parent and subcommand"

coderabbitai (2):
  - src/cmd/space.rs:175 — "Consider testing the project fallback explicitly."
  - .cspell/dicts/project.txt:15 — "Typo: emptively → preemptively"
```

### Step 3 — Confirm reviewer scope

After showing the summary, ask the user:

```text
Target reviewer: [1] GitHub Copilot only (default) / [2] All reviewers
```

If the user selects 1 or presses Enter without input, restrict to threads where
`author_login` is `copilot-pull-request-reviewer[bot]` and skip all others
silently. If the user selects 2, process threads from all reviewers.

### Step 4 — Classify each thread

For every thread in scope, apply the following decision rules in order:

| Condition | Classification |
| --------- | -------------- |
| `is_resolved: true` | **Already resolved** — skip |
| `thread_comments` is empty | **No reply** — skip (leave untouched) |
| Reply clearly indicates a fix (e.g. "fixed in \<commit\>", "addressed", "修正しました") | **Auto-resolve** |
| Reply clearly indicates intentional skip (e.g. "won't fix", "by design", "意図的です", "対応しません") | **Auto-resolve** |
| Reply is ambiguous or unclear | **Ask user** |

"Clearly indicates" means the reply body contains unambiguous intent. When in
doubt, classify as **Ask user**.

### Step 5 — Present plan and confirm

Before taking any action, show a plan grouped by classification:

```text
## Resolution plan

**Will resolve automatically (N threads):**
- src/foo.py:42 — Reply: "fixed in abc1234"
- src/bar.py:17 — Reply: "won't fix: intentional behaviour"

**Will ask you about (N threads):**
- docs/api.md:7 — Reply: "ok" (ambiguous)

**No reply — leaving untouched (N threads):**
- src/qux.py:5

**Already resolved — skipping (N threads):**
- src/baz.py:10

Proceed?
```

Wait for the user to confirm. If the user requests changes to the plan (e.g.
skip a specific thread, reclassify something), revise and ask again.

For threads classified as **Ask user**, show the original comment and reply
side by side and ask:

```text
Thread: src/api.md:7
  Copilot: "Consider using pathlib here."
  Reply:   "ok"

Resolve this thread? [y/n]
```

Process all **Ask user** threads as a batch before resolving, to minimise
back-and-forth.

### Step 6 — Resolve approved threads

For each thread approved for resolution, run:

```bash
gh pr-review threads resolve <PR_NUMBER> -R <OWNER/REPO> --thread-id <thread_id>
```

If the command exits with a non-zero status, report the failure and continue
with the remaining threads.

### Step 7 — Report summary

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
