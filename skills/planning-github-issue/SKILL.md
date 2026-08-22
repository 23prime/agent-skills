---
name: planning-github-issue
description: Use when a refined GitHub Issue needs a technical implementation plan before any code is written — the approach, whether it needs to be split into sub-issues, and, if not, the commit-unit breakdown to implement it in.
---

# Planning a GitHub Issue

Turn a refined GitHub Issue into a concrete technical plan. Decide the approach, then either
split the Issue into sub-issues (when it's too large for one PR) or break it into commit-sized
units (when it isn't). Write the result back to the Issue so it survives as a reference through
implementation and review.

## Workflow

### 1. Fetch the Issue

```bash
gh issue view <number> --json number,title,body,labels,assignees,comments
```

If no repository is specified, use the remote origin of the current directory.
Assumes the Issue is already refined (clear purpose, scope, acceptance criteria) — if it
isn't, run `refining-github-issue` first.

### 2. Understand the codebase context

Explore the parts of the codebase the Issue touches — relevant files, layers, existing
patterns, related tests. This grounds the approach decision in what actually exists rather
than assumptions about it.

### 3. Decide the technical approach

Decide what will change and how: the overall approach, the files/layers involved, and any
design choices with a genuine tradeoff.

- Where one option has a clearly strong advantage, follows from consistency with existing
  design/implementation in the repo, or is settled by an established convention, decide it
  yourself and note the one-line rationale — don't ask.
- Ask the user only when a choice has a real tradeoff with no self-evident answer.

### 4. Decide whether decomposition is needed

Judge, in light of the approach from step 3, whether the Issue is small enough for a single
PR. It does NOT need decomposition if it:

- Addresses a single concern (one feature, one fix, one area of the codebase)
- Can be reviewed in a single PR session without overwhelming the reviewer

- **Single PR is sufficient**: continue to step 5.
- **Needs decomposition** (genuinely large, or spans multiple independent concerns): continue
  to step 6.

### 5. Break the work into commit-sized units

Decide whether the acceptance criteria break down into multiple independent logical units
(distinct concerns, layers, or files that make sense as separate commits) or form a single
unit. Note the planned units, in order, or the decision not to split. This decision is made
once, here; implementation then works through the planned units in order without
re-deciding.

Per-commit build/lint/test correctness does not need to be verified here — if the project has
pre-commit hooks for build, static analysis, or unit tests, the commit step of whatever
workflow is driving this plan already runs them on every commit and fixes-and-recommits on
failure. Rely on that instead of adding redundant checks here.

Continue to step 7.

### 6. Propose and create sub-issues

Using the approach from step 3, propose a list of sub-issues. Each sub-issue should be:

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

Ask the user if they want to adjust it (add, remove, or merge sub-issues; change titles or
descriptions) and wait for explicit approval before creating anything.

For each approved sub-issue, create it with `--parent` to link it to the parent Issue — this
is the only supported way to link Sub-issues via the `gh` CLI:

```bash
gh issue create \
  --title "<title>" \
  --body "<description>" \
  --parent <parent-number>
```

Report the URL of each created Issue. Do not start implementation of any sub-issue here — run
`planning-github-issue` again independently for each sub-issue's own scope, starting from
step 1. Then continue to step 7 for the parent Issue.

### 7. Update the Issue

Propose writing the plan back to the Issue. Show it as a diff against the current body and
confirm before writing:

```bash
gh issue edit <number> --body "$(cat <<'EOF'
<updated_body>
EOF
)"
```

## Output Format

Once the plan is settled, output a summary in one of the following formats.

Single PR (steps 5 and 7):

```markdown
## Issue #<number> — Implementation Plan

### Approach
<1–3 sentences on what will change and how>

### Implementation Units
1. <unit description>
2. <unit description>
...

### Notes
<Design tradeoffs decided and their rationale, constraints, open questions>
```

Decomposed (steps 6 and 7):

```markdown
## Issue #<number> — Implementation Plan

### Approach
<1–3 sentences on what will change and how>

### Decomposition
- #<n> <title> — <url>
- #<n> <title> — <url>
...

### Notes
<Design tradeoffs decided and their rationale, constraints, open questions>
```

## Important

- Always get user confirmation before creating sub-issues or updating the Issue.
- Do not start implementation until the plan is written back to the Issue.
- If decomposition is needed, do not produce an implementation-unit breakdown for the parent
  Issue — that belongs to each sub-issue's own plan.
