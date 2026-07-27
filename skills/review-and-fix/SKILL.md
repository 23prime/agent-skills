---
name: review-and-fix
description: Review uncommitted changes, or a whole branch against its base, with parallel subagents and the CodeRabbit CLI, then fix each actionable issue in place, looping until clean, without committing. Use when a user wants to review and clean up their working tree changes before committing, or review a branch's full diff before opening a PR.
---

# Review and Fix

## Workflow

### 1. Collect the diff

Determine the review scope:

- **Uncommitted (default)**: capture all changes not yet committed, including untracked files.
  1. `git diff HEAD` — staged and unstaged changes to tracked files
  2. `git ls-files --others --exclude-standard` — list untracked files
  3. For each untracked file, run `git diff --no-index /dev/null <file>` to produce a diff
- **Branch** (when explicitly asked to review the whole branch, e.g. before opening a PR): diff the branch against its base instead — `git diff @{upstream}...HEAD`, or `git diff main...HEAD` if there is no upstream. If uncommitted changes also exist on top, collect those too (as above) and include them in the review target.

Combine all output as the review target. If the review target is empty, inform the user that there are no changes to review.

Then scan the collected diff for renames (`rename from` / `rename to`, usually with `similarity index 100%`) and note which files were renamed without a content change. CodeRabbit re-reviews such a file's entire pre-existing content as if it were new, and subagents do the same when the diff shows only the rename. Carry the list into steps 2 and 3.

### 2. Review the diff

First, decide which review dimensions the diff needs. Default to running all five; drop a dimension only when the diff clearly cannot exhibit that failure mode:

- Drop dimensions 1 (bugs and logic errors) and 2 (unintended behavior changes) when the diff touches no executable code — e.g. it only changes Markdown, comments, or static assets.
- Drop dimension 3 (security concerns) when the diff touches no code path that handles input, secrets, auth, network access, file access, or external processes — e.g. docs-only or comment-only changes.
- Always keep dimension 4 (obvious improvements) and dimension 5 (missed related updates); both apply to docs and config, not just code.
- If the diff mixes code and docs, touches multiple areas, or you're not sure a dimension is irrelevant, keep it — the cost of an extra subagent is far lower than the cost of a missed bug.

Then run the following concurrently:

- Dispatch one subagent (Agent tool, `general-purpose` type) per surviving dimension, in parallel. Pass each the collected diff and its dimension-specific instructions verbatim. The diff must be pasted into the prompt as literal text — the Agent tool's prompt is a plain string, not a shell command, so writing `$(cat diff.txt)` inside it does not expand; it sends those literal characters. Read the collected diff first, then paste its actual content into each prompt.
  1. **Bugs and logic errors** — Scan the diff for off-by-one errors, null/undefined access, wrong comparison operators, missing return values, infinite loops, race conditions.
  2. **Unintended behavior changes** — Scan the diff for accidental removal of logic, swapped arguments, changed defaults.
  3. **Security concerns** — Scan the diff for hardcoded secrets, injection vulnerabilities, missing input validation at system boundaries.
  4. **Obvious improvements** — Scan the diff for dead code introduced in the diff, clearly redundant operations.
  5. **Missed related updates** — Identify what the diff changes (interfaces, flags, config keys, behavior, file/directory layout) and check whether every place in the repo that depends on it was updated too: README and other docs, GitHub Actions workflows (`.github/workflows/`), other CI config, scripts, and cross-references in other skills or files. Grep the repo for the old name/value/path being changed to find anything left stale. Also check the reverse direction: if the diff removes the last usage of a dependency, import, helper, or config entry, confirm it was removed too rather than left as dead weight (e.g. a package.json/go.mod entry, an import statement, an unused env var).

  Append to dimensions 1-4's prompts: "Do not comment on style, formatting, naming, or documentation unless it directly causes a bug." Append to all surviving dimensions' prompts: "Return findings as a list grouped by file. For each finding, state the file and approximate line, describe the issue in one sentence, and suggest a fix if it is straightforward. If no issues are found, say so briefly."

  When step 1 found renamed-but-unchanged files, add to every dimension's prompt: "These files are renamed only, with content unchanged: `<list>`. Their pre-existing content is out of scope — do not report issues in it. Do report anything that depends on their old path." Dimension 5 still checks the renames themselves for stale references.
- Run CodeRabbit with a scope matching step 1, so its findings cover the same range as the subagents': `coderabbit review --agent --type uncommitted` in uncommitted mode, or `coderabbit review --agent --base <base-branch>` in branch mode. If CodeRabbit reports a rate limit, retry after the wait time it reports. If it still reports a rate limit after 3 retries, proceed using only the subagents' findings for this pass and note in the report that CodeRabbit was skipped due to rate limiting — do not block the workflow on it indefinitely.

### 3. Consolidate findings

Merge the five subagents' findings with CodeRabbit's findings into a single list, grouped by underlying issue rather than by source — the same root cause is often reported by more than one source with different wording, so match by file/line/mechanism, not literal text.

Critically evaluate every finding before accepting it, regardless of source:

- Verify it against the actual diff and surrounding code; do not take a finding at face value.
- Discard suggestions that are purely stylistic preferences, false positives, or don't hold up under verification.
- Discard findings that land on unchanged lines of a renamed-but-unchanged file from step 1 — CodeRabbit reports these every pass, so they will reappear on each re-review. Mention them once in the step 6 report as pre-existing and out of scope, rather than fixing them silently.
- Keep only actionable issues: bugs, logic errors, security concerns, and genuine convention violations backed by evidence.

### 4. Fix each issue

For each surviving actionable issue, apply the fix directly in the working tree. Do not stage or commit — the changes under review are, by definition, not yet committed, and committing them here would take that decision away from the user.

### 5. Re-review

Repeat steps 2-4 (rerun both the subagent review and CodeRabbit, with the same scope as step 2) until a full pass finds no further actionable issues. Re-derive which dimensions apply each time, since fixes may have touched code that the original diff didn't. When re-running the subagent review, dimension 5 should focus on whether the fixes from this pass introduced any new missed-update gaps.

### 6. Report

Summarize all fixes applied to the user. In branch mode, if a fix touches a line that was already part of an earlier commit on the branch (not just this pass's uncommitted changes), call that out explicitly, since it's easy to miss that already-committed code is being changed again. If no issues were found, say so briefly. Avoid filler or praise — the goal is speed and signal. Leave the fixes uncommitted; suggest the user review the result and commit when ready (e.g. with `committing-changes`).
