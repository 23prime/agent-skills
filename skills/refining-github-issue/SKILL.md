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
- **Acceptance criteria**: What is the definition of done?
- **Constraints and assumptions**: Are there technical or business constraints?
- **Priority and urgency**: How time-sensitive is this?

If the Issue already has a clear purpose, explicit scope, and acceptance criteria (e.g., it was previously refined), skip to the Output Format and summarize what is already known. Do not ask redundant questions.

### 3. Ask the user questions

Do not ask many questions at once. Narrow down to the 1-3 most important unclear points.
After receiving answers, ask follow-up questions if deeper clarification is needed.

Example questions:

- "Does the definition of done for this Issue include X?"
- "X may conflict with the existing Y — how should this be handled?"
- "Is this a user-facing change or internal implementation only?"

### 4. Update the Issue (optional)

With the user's consent, write the refined content back to the Issue.

```bash
gh issue edit <number> --body "$(cat <<'EOF'
<refined_body>
EOF
)"
```

Always show the proposed changes to the user before executing the update.

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
