---
name: creating-pull-request
description: "Creates a GitHub Pull Request for the current branch using the gh CLI. Inspects git status, diffs, and commit history to compose a concise PR title and body, then pushes the branch and opens the PR. Use when the user asks to create a PR, open a pull request, or submit changes for review on GitHub."
---

# Creating Pull Request

Workflow for creating a GitHub Pull Request from the current branch.

## Base branch

Use `main` as the base branch unless the user explicitly specifies another one.
Referred to as `BASE` below.

## Workflow

### Step 1: Gather branch information

Run the following commands in parallel:

```bash
git status
git diff HEAD
git log BASE...HEAD --oneline
git diff BASE...HEAD
```

Use these to understand:

- What files have changed (staged and unstaged)
- All commits on this branch since diverging from BASE
- The full diff against the base branch

### Step 2: Determine if a push is needed

Check whether the current branch tracks a remote and is up to date:

```bash
git status -sb
```

If the branch has no upstream or is ahead of remote, push it:

```bash
git push -u origin HEAD
```

### Step 3: Compose the PR title and body

**Title**: One concise sentence (under 70 chars) summarising the change.
Prefix with a type if the project uses conventional commits (`feat:`,
`fix:`, `chore:`, etc.).

**Closing keyword**: If this PR resolves a GitHub Issue, include a closing
keyword (`Closes #<N>`, `Fixes #<N>`, or `Resolves #<N>`) in the body so
merging the PR auto-closes the Issue. Determine the Issue number from the
branch name (e.g. `feature/42-add-oauth-login` → `#42`) or from context
already established earlier in the conversation (e.g. the Issue this PR's
work was scoped from). Do not guess an Issue number with no such evidence.

**Body**: Check for a PR template first:

```bash
cat .github/pull_request_template.md 2>/dev/null || cat .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null
```

- If a template exists, fill in every section of that template. Do not omit
  any section.
- If no template exists, use this fallback:

```markdown
## Checklist

- [ ] Status checks are passing
- [ ] Target branch is correct

## Summary

Closes #<N>

## Reason for change

## Changes

## Notes
```

Omit the `Closes #<N>` line entirely (not just leave it blank) when no Issue applies. When a repo's own PR template is used instead of this fallback, add the closing keyword as its own line near the top of the `## Summary`-equivalent section (or wherever the template's own conventions put issue references) rather than skipping it.

### Step 4: Create the PR

Pass the body via a heredoc to preserve formatting:

```bash
gh pr create --base BASE --title "..." --body "$(cat <<'EOF'
<filled body here>
EOF
)"
```

Return the PR URL to the user when done.

## Notes

- Always analyze **all** commits on the branch, not just the latest one.
- Do not force-push unless the user explicitly requests it.
