---
name: creating-branch
description: Use when starting work on a GitHub Issue or a new feature and a topic branch needs to be created before implementation begins.
---

# Creating a Branch

Create a topic branch following the repository's naming conventions,
then push it to the remote with upstream tracking set.

## Workflow

### 1. Detect naming conventions

Look for branch naming rules in this order:

1. Search for branch naming rules in instruction and contribution files:

   ```bash
   fd -e md --max-depth 3 | rg -i 'CLAUDE|AGENTS|CONTRIBUTING'
   ```

   Read any files found and look for branch naming conventions.
2. Existing remote branches — infer the pattern from names already in use:

   ```bash
   git branch -r --format '%(refname:short)' | grep -v 'HEAD\|main\|master\|develop'
   ```

If no rules are found, use the common default:

| Type | Prefix |
| ---- | ------ |
| New feature | `feature/` |
| Bug fix | `fix/` |
| Hotfix | `hotfix/` |
| Chore / maintenance | `chore/` |
| Documentation | `docs/` |
| Refactoring | `refactor/` |

### 2. Derive the branch name

Build the branch name from the Issue number and title (or the task description):

- Convert the title to lowercase kebab-case
- Strip special characters, keep letters, digits, and hyphens
- Truncate to keep the name readable (≤ 50 chars total including prefix)
- Include the Issue number when one is provided

Examples:

| Input | Branch name |
| ----- | ----------- |
| Issue #42 "Add OAuth login" | `feature/42-add-oauth-login` |
| Issue #7 "Fix null pointer on startup" | `fix/7-null-pointer-on-startup` |
| "Upgrade dependencies" | `chore/upgrade-dependencies` |

### 3. Sync the default branch

Identify the default branch and pull the latest changes:

```bash
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
git switch <default-branch>
git pull
```

### 4. Create and push the branch

```bash
git switch -c <branch-name>
git push -u origin <branch-name>
```

Report the created branch name to the user.

## Important

- Always branch off the default branch (detected via `gh repo view`), not from another topic branch, unless the user explicitly asks otherwise.
- Do not ask the user to confirm the branch name — create it immediately.
- Do not start implementation after creating the branch; wait for the user's instruction.
