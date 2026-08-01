---
name: refining-github-issue
description: Use when a GitHub Issue is vague, missing acceptance criteria, or needs scope clarification before implementation begins.
---

# Refining a GitHub Issue

Fetch a specified GitHub Issue and brush up its content through dialogue with the user.
The goal is to clarify the intent, scope, and acceptance criteria before starting implementation.

## Workflow

### 1. Fetch the Issue

Accept an Issue number or URL as input and fetch it with the `gh` CLI.

```bash
# By number
gh issue view <number> --json number,title,body,labels,assignees,comments

# By URL (repository is resolved automatically)
gh issue view <url> --json number,title,body,labels,assignees,comments
```

If no repository is specified, use the remote origin of the current directory.

### 2. Analyze the Issue

Read the fetched Issue body **and comments** and identify unclear or ambiguous points from the following perspectives:

- **Purpose**: Why is this Issue needed?
- **Scope**: What is in scope and what is explicitly out of scope?
- **Acceptance criteria**: What is the definition of done? For user-facing changes, confirm whether the user can verify the result themselves via a browser or real device, or whether verification will rely on tests/code review alone.
- **Constraints and assumptions**: Are there technical or business constraints?
- **Hidden scope**: Are there changes the Issue doesn't mention but that the stated change still requires — CI/workflow configs, other config files, adjacent test types (e.g. E2E alongside unit tests), or docs? List candidates and confirm with the user rather than assuming they're out of scope.

If the Issue already has a clear purpose, explicit scope, and acceptance criteria (e.g., it was previously refined), skip to the Output Format and summarize what is already known. Do not ask redundant questions.

### 3. Ask the user questions

Interview the user relentlessly about every unclear point identified in step 2, resolving each one before moving to the next. Do not stop at a vague or partial answer — ask a follow-up that drills into the specific ambiguity until it is resolved.

- Ask **one question at a time**; never batch multiple questions into a single message.
- Work through the unclear points from step 2 one by one. Do not jump to Output Format while points remain unresolved, unless the user explicitly says to move on.
- If a question can be answered by exploring the codebase, explore it instead of asking.
- Where you have a reasonable default, propose it and ask the user to confirm or override, rather than asking an open-ended question.
- Don't ask about a point at all when it's already near-self-evident — e.g. one option has a clearly strong advantage, the answer follows from consistency with existing design/implementation in the repo, or an established industry-standard convention settles it. Decide it yourself, state the decision and its one-line rationale in the Output Format instead, and move on without waiting for confirmation. Reserve actual questions for points with a genuine tradeoff.
- For UI/visual/UX details (exact spacing, wording nuance, layout tweaks, interaction feel), don't press the user to judge from a text description alone — that's unreliable without seeing it rendered. Propose a reasonable default, note in the Output Format that it's pending visual confirmation, and defer the final call to post-implementation verification (browser or real device) rather than resolving it here through more questions.

Example questions:

- "Does the definition of done for this Issue include X?"
- "X may conflict with the existing Y — how should this be handled?"
- "Is this a user-facing change or internal implementation only?"
- "Can you verify this yourself in a browser or on a real device, or should verification rely on tests/code review only?"

### 4. Update the Issue

Propose writing the refined content back to the Issue. Show it as a diff
against the current body and confirm before writing:

```bash
gh issue edit <number> --body "$(cat <<'EOF'
<refined_body>
EOF
)"
```

## Output Format

Once the Q&A is complete, output a summary in the following format:

```markdown
## Issue #<number> — Refinement Result

### Purpose
<1–2 sentences>

### Scope
- In scope: ...
- Out of scope: ...

### Acceptance Criteria
- [ ] ...
- [ ] ...

### Notes
<Constraints, assumptions, or unresolved questions>
```

## Important

- Always get user confirmation before updating the Issue.
- Do not start implementation until the user says to proceed.
- Keep questions concise — use a one-question-at-a-time approach to go deep.
