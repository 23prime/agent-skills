---
name: resolving-github-issue
description: Use when the user wants to work through a GitHub Issue end-to-end, from clarifying requirements to getting the PR merged.
---

# Resolving a GitHub Issue

Orchestrate the full lifecycle of a GitHub Issue: clarify → plan → implement → review → merge.
Each step delegates to a dedicated skill; this skill defines the order and decision points.

## Workflow

### 1. Refine the Issue

Invoke `refining-github-issue` with the Issue number or URL.
Clarify intent, scope, and acceptance criteria before any code is written.

### 2. Decide whether to decompose

Invoke `decomposing-github-issue`.
If the Issue is small enough for a single PR, skip decomposition and proceed.
If decomposition is needed, complete each sub-issue independently from step 3 onward.

### 3. Create a branch

Invoke `creating-branch` with the Issue number and title.
The skill detects naming conventions and syncs the default branch automatically.

### 4. Implement

Work through the acceptance criteria. The implementation method depends on the project:
run tests, apply configuration, edit code — whatever the Issue requires.

### 5. Commit

Invoke `committing-changes` when a logical unit of work is complete.
Repeat steps 4–5 as needed until all acceptance criteria are met.

### 6. Self-review

Invoke `reviewing-changes` before opening the PR.
Fix any issues found, then commit the fixes (`committing-changes`).

### 7. Open a PR

Invoke `creating-pull-request`.

### 8. Respond to review

Invoke `responding-to-pr-review` and iterate until the PR is merged.

## Sub-skills

| Step | Skill |
| ---- | ----- |
| 1 | `refining-github-issue` |
| 2 | `decomposing-github-issue` |
| 3 | `creating-branch` |
| 5 | `committing-changes` |
| 6 | `reviewing-changes` |
| 7 | `creating-pull-request` |
| 8 | `responding-to-pr-review` |

## Important

- Complete step 1 before writing any code — implementation without clear acceptance criteria wastes effort.
- Step 2 is always invoked, even for small Issues; the skill decides whether decomposition is needed.
- Steps 4–5 may repeat multiple times before moving to step 6.
- If the PR review reveals scope creep or new requirements, return to step 1.
