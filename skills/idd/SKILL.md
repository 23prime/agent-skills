---
name: idd
description: Use when the user wants to work through a GitHub Issue end-to-end, from clarifying requirements to getting the PR merged.
---

# Issue Driven Development

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

### 4. Decide whether to split into multiple commits

Before writing any code, decide whether the acceptance criteria break down into multiple
independent logical units (distinct concerns, layers, or files that make sense as separate
commits) or form a single unit. This is a different axis from step 2: step 2 decides whether
the Issue needs separate PRs, this decides whether a single PR needs separate commits. Note
the planned units, in order, or the decision not to split. This decision is made once, here;
steps 5–7 then work through the planned units in order without re-deciding.

Per-commit build/lint/test correctness does not need to be separately verified here or in
step 6's review — if the project has pre-commit hooks for build, static analysis, or unit
tests, step 7 (`committing-changes`) already runs them on every commit and fixes-and-recommits
on failure. Rely on that instead of adding redundant checks.

### 5. Implement

Work through the acceptance criteria for the current unit. The implementation method depends
on the project: run tests, apply configuration, edit code — whatever the Issue requires.
Check whether the project has its own implementation-related skills (e.g. for DB schema
changes or API spec updates) and use them when relevant.

### 6. Review

When a logical unit of work is complete, invoke `review-and-fix` in uncommitted scope to catch issues before they're committed. Use light depth when step 4 planned multiple units (a later full review in step 8 covers the cross-cutting dimensions); use full depth when step 4 did not split the work, since no later full review is planned.

### 7. Commit

Invoke `committing-changes`.
Repeat steps 5–7 as needed until all acceptance criteria are met.

### 8. Final self-review

Invoke `review-and-fix` at full depth, in branch mode (diff against the base branch): steps 5–7 already committed the implementation incrementally, so there is nothing uncommitted left for the default scope to review. It fixes any issues found but does not commit — it leaves the fixes in the working tree.

Skip this step only when the branch diff is identical to what step 6 already reviewed at full depth — that is, steps 5–7 ran once, step 6 used full depth (step 4 did not split the work), and the single commit was made straight after that review, with no edits since. Re-running would review the same diff a second time. Say that this is why it was skipped, and confirm the equivalence (e.g. `git diff main...HEAD --stat` against the reviewed set) rather than asserting it. Never skip when step 6 ran at light depth — dimensions 4-6 and CodeRabbit have not run on that diff yet.

### 9. Commit the fixes

Invoke `committing-changes` to commit whatever `review-and-fix` changed. Skip this step if step 8 found nothing to fix.

### 10. Open a PR

Invoke `creating-pull-request`.

### 11. Respond to review

Invoke `responding-to-pr-review` and iterate until the PR is approved.

### 12. Run retrospective

Once the PR reaches `APPROVED`, invoke the `retrospective` skill.

1. If it left any file changes uncommitted, invoke `committing-changes` to
   commit and push them.
2. Re-check the review decision:

   ```bash
   gh pr view <PR_NUMBER> -R <OWNER/REPO> --json reviewDecision --jq .reviewDecision
   ```

   If it is no longer `APPROVED` (the push dismissed the approval, on
   repos configured that way), go back to step 11 to handle the PR as if
   new review activity occurred. Otherwise proceed to step 13.
3. If `retrospective` made no changes, proceed directly to step 13.

### 13. Finish the PR

Invoke `finishing-pull-request` to merge the PR and clean up the topic branch.

## Sub-skills

| Step | Skill |
| ---- | ----- |
| 1 | `refining-github-issue` |
| 2 | `decomposing-github-issue` |
| 3 | `creating-branch` |
| 6 | `review-and-fix` (light depth if split, full otherwise) |
| 7 | `committing-changes` |
| 8 | `review-and-fix` (full depth) |
| 9 | `committing-changes` |
| 10 | `creating-pull-request` |
| 11 | `responding-to-pr-review` |
| 12 | `retrospective` |
| 13 | `finishing-pull-request` |

## Important

- Complete step 1 before writing any code — implementation without clear acceptance criteria wastes effort.
- Step 2 is always invoked, even for small Issues; the skill decides whether decomposition is needed.
- Steps 5–7 may repeat multiple times before moving to step 8. If step 4 planned multiple
  logical units, run steps 5–7 once per unit, in the planned order, producing one commit per
  unit.
- If the PR review reveals scope creep or new requirements, return to step 1.
- The user's request to run this skill is standing authorization for the whole
  lifecycle, including pushing branches/commits and opening the PR. Move from
  step to step without adding your own extra check-in before those actions.
  The only stops are the confirmation points each sub-skill already defines
  (e.g. decomposition breakdown, commit message, PR review plan, merge) —
  do not add another one on top.
