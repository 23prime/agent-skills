---
name: coderabbit
description: Review uncommitted changes using the CodeRabbit CLI, fix each reported issue, and commit each fix individually. This skill should be used when the user wants an AI-powered code review of their changes before committing.
---

# CodeRabbit

Run CodeRabbit CLI to review current changes, fix reported issues one by one, and commit each fix individually.

## Workflow

### 1. Run review

Execute CodeRabbit in prompt-only mode to get review feedback:

```bash
coderabbit review --prompt-only
```

### 2. Evaluate feedback

Read the output and identify actionable issues (bugs, logic errors, security concerns, style violations).

Ignore suggestions that are purely stylistic preferences or false positives.

### 3. Fix and commit each issue

For each actionable issue:

1. Apply the fix
2. Stage the changed files with `git add <file>...`
3. Commit with a message describing the fix (follow project commit conventions)

### 4. Re-review

Run `coderabbit review --prompt-only` again to verify fixes and check for remaining issues.

Repeat steps 2-4 until no further actionable issues are reported.

### 5. Report

Summarize all commits made to the user.
