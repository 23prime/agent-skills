---
name: idd
description: Use when the user wants to work through a GitHub Issue end-to-end, from clarifying requirements to getting the PR merged.
---

# Issue Driven Development

Orchestrate the full lifecycle of a GitHub Issue: clarify → plan → implement → review → merge.
Each step delegates to a dedicated skill; this skill defines the order and decision points.

## Workflow

### 1. Refine the Issue

1. Fetch the Issue yourself first (`gh issue view <number> --json number,title,body,labels,assignees,comments`) so you have independent context for the matching check below. Dispatch the `issue-refiner` agent (foreground, `run_in_background: false`) with the Issue number or URL, to run the interview at higher reasoning effort than the rest of this workflow needs. Subagent dispatch is a hard context boundary — it starts cold and only its final report comes back — so relay every turn of its interview, with one exception:

   When its question includes a proposed default (per `refining-github-issue`'s step 3 guidance to propose one when reasonable), form your own independent guess by reading the Issue yourself, before reading the agent's proposed default — then compare:

   - **Your guess matches the agent's proposed default** — treat it as self-evident. Confirm that default back to the agent via `SendMessage` yourself (do not ask the user), and keep a running note of what was auto-confirmed.
   - **Guesses differ, or the question has no proposed default** — forward the question to the user verbatim, and send their answer back to the same agent via `SendMessage`, as before.

   Repeat until the agent finishes updating the Issue. Never paraphrase or summarize away content that does reach the user or the agent. Before the agent's step 4 confirmation (writing the Issue), show the user the list of auto-confirmed defaults alongside the diff so they can override any before it's written.
2. Dispatch the `issue-reviewer` agent (foreground) with only the Issue number or URL — no summary of the step 1 discussion. Because you relayed every turn in step 1 yourself, your own re-read is not actually fresh eyes; a cold subagent with zero prior context is. If it finds nothing, proceed.

   For each ambiguity it reports, form your own best-guess answer independently by reading the Issue yourself, before looking at the subagent's guess — then compare:

   - **Your guess matches the subagent's guess** — two independent reads converged on the same interpretation, so treat it as self-evident. Update the Issue to state that interpretation explicitly (note that it was resolved by independent agreement, not the user) and do not ask the user.
   - **Guesses differ, or either side has no inferable default** — genuinely ambiguous; ask the user directly and update the Issue with their answer.

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
Check whether the project has its own implementation-related skills (e.g. for DB schema
changes or API spec updates) and use them when relevant.

### 5. Review

When a logical unit of work is complete, invoke `review-and-fix` in its default (uncommitted) mode to catch issues before they're committed.

### 6. Commit

Invoke `committing-changes`.
Repeat steps 4–6 as needed until all acceptance criteria are met.

### 7. Final self-review

Invoke `review-and-fix` in branch mode (diff against the base branch): steps 4–6 already committed the implementation incrementally, so there is nothing uncommitted left for the default mode to review. It fixes any issues found but does not commit — it leaves the fixes in the working tree.

Skip this step when the branch diff is identical to what step 5 already reviewed — that is, steps 4–6 ran once and the single commit was made straight after that review, with no edits since. Re-running would review the same diff a second time. Say that this is why it was skipped, and confirm the equivalence (e.g. `git diff main...HEAD --stat` against the reviewed set) rather than asserting it.

### 8. Commit the fixes

Invoke `committing-changes` to commit whatever `review-and-fix` changed. Skip this step if step 7 found nothing to fix.

### 9. Open a PR

Invoke `creating-pull-request`.

### 10. Respond to review

Invoke `responding-to-pr-review` and iterate until the PR is approved.

### 11. Run retrospective

Once the PR reaches `APPROVED`, invoke the `retrospective` skill.

1. If it left any file changes uncommitted, invoke `committing-changes` to
   commit and push them.
2. Re-check the review decision:

   ```bash
   gh pr view <PR_NUMBER> -R <OWNER/REPO> --json reviewDecision --jq .reviewDecision
   ```

   If it is no longer `APPROVED` (the push dismissed the approval, on
   repos configured that way), go back to step 10 to handle the PR as if
   new review activity occurred. Otherwise proceed to step 12.
3. If `retrospective` made no changes, proceed directly to step 12.

### 12. Finish the PR

Invoke `finishing-pull-request` to merge the PR and clean up the topic branch.

## Sub-skills

| Step | Skill |
| ---- | ----- |
| 1 | `issue-refiner` (agent), then `issue-reviewer` (agent) |
| 2 | `decomposing-github-issue` |
| 3 | `creating-branch` |
| 5 | `review-and-fix` |
| 6 | `committing-changes` |
| 7 | `review-and-fix` |
| 8 | `committing-changes` |
| 9 | `creating-pull-request` |
| 10 | `responding-to-pr-review` |
| 11 | `retrospective` |
| 12 | `finishing-pull-request` |

## Important

- Complete step 1 before writing any code — implementation without clear acceptance criteria wastes effort.
- Step 2 is always invoked, even for small Issues; the skill decides whether decomposition is needed.
- Steps 4–6 may repeat multiple times before moving to step 7.
- If the PR review reveals scope creep or new requirements, return to step 1.
- The user's request to run this skill is standing authorization for the whole
  lifecycle, including pushing branches/commits and opening the PR. Move from
  step to step without adding your own extra check-in before those actions.
  The only stops are the confirmation points each sub-skill already defines
  (e.g. decomposition breakdown, commit message, PR review plan, merge) —
  do not add another one on top.
