---
name: reviewing-changes
description: Quick review of uncommitted changes (staged and unstaged) focusing on bugs and logic mistakes. Use when a user wants a fast, high-level code review of their current working tree changes before committing.
---

# Reviewing Changes

## Workflow

### 1. Collect the diff

Run the following to capture all changes including untracked files:

1. `git diff HEAD` — staged and unstaged changes to tracked files
2. `git ls-files --others --exclude-standard` — list untracked files
3. For each untracked file, run `git diff --no-index /dev/null <file>` to produce a diff

Combine all output as the review target. If both the diff and untracked file list are empty, inform the user that there are no changes to review.

### 2. Review the diff

Scan the diff with the following priorities (highest first):

1. **Bugs and logic errors** — off-by-one, null/undefined access, wrong comparison operators, missing return values, infinite loops, race conditions
2. **Unintended behavior changes** — accidental removal of logic, swapped arguments, changed defaults
3. **Security concerns** — hardcoded secrets, injection vulnerabilities, missing input validation at system boundaries
4. **Obvious improvements** — dead code introduced in the diff, clearly redundant operations

Do not comment on style, formatting, naming, or documentation unless it directly causes a bug.

### 3. Report findings

Present findings as a concise list grouped by file. For each finding:

- State the file and approximate line in the diff
- Describe the issue in one sentence
- Suggest a fix if it is straightforward

If no issues are found, say so briefly. Avoid filler or praise — the goal is speed and signal.
