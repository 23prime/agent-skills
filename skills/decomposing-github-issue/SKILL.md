---
name: decomposing-github-issue
description: Use when a GitHub Issue spans multiple independent concerns and feels too large to implement in a single PR.
---

# Decomposing a GitHub Issue

Analyze a large GitHub Issue and break it down into appropriately sized sub-issues,
then create them on GitHub with the parent Issue linked via GitHub's Sub-issues feature.

## Workflow

### 1. Fetch the Issue

```bash
gh issue view <number> --json number,title,body,labels,assignees,comments
```

If no repository is specified, use the remote origin of the current directory.

### 2. Assess whether decomposition is needed

Read the Issue and judge whether it is large enough to warrant decomposition.
A well-scoped Issue does NOT need decomposition if it:

- Addresses a single concern (one feature, one fix, one area of the codebase)
- Can be reviewed in a single PR session without overwhelming the reviewer

If decomposition is not needed, tell the user why and stop. For example:

> This Issue addresses a single feature with three acceptance criteria — no decomposition needed.

Only proceed to the next step if the Issue is genuinely large or spans multiple independent concerns.

### 3. Propose a breakdown

Analyze the Issue and propose a list of sub-issues. Each sub-issue should be:

- **Independent**: implementable without depending on other sub-issues in the list
- **Small**: completable in a single PR
- **Concrete**: has a clear title and a brief description of what to implement

Present the breakdown to the user in this format:

```markdown
## Proposed Sub-issues for #<number>

1. **<title>** — <one-line description>
2. **<title>** — <one-line description>
...
```

### 4. Refine with the user

Ask the user if they want to adjust the breakdown:

- Add, remove, or merge sub-issues
- Change titles or descriptions

Wait for explicit approval before proceeding.

### 5. Create sub-issues

For each approved sub-issue, create it with `--parent` to link it to the parent Issue:

```bash
gh issue create \
  --title "<title>" \
  --body "<description>" \
  --parent <parent-number>
```

Report the URL of each created Issue after creation.

## Output Format

After all sub-issues are created, output a summary:

```markdown
## Sub-issues created for #<number>

- #<n> <title> — <url>
- #<n> <title> — <url>
...
```

## Important

- Do not create any sub-issues until the user approves the full breakdown.
- Use `--parent` on `gh issue create` — this is the only supported way to link Sub-issues via CLI.
- Do not start implementation of any sub-issue unless the user explicitly asks.
