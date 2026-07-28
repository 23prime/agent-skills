---
name: committing-changes
description: Inspect the current git diff, compose a commit message following project conventions, and execute git commit. Use when the user asks to commit changes, requests a commit, or says they are done with a task and want to save their work.
---

# Committing Changes

Review the current working tree changes, compose a conventional commit message, and execute the commit.

## Workflow

### 1. Inspect changes

Run the following commands in parallel to understand the current state:

- `git status` — identify changed and untracked files
- `git diff` — review unstaged changes
- `git diff --staged` — review staged changes
- `git log --oneline -5` — check recent commit style for context

If there are no changes to commit, inform the user and stop.

### 2. Evaluate whether to split commits

Review the changes and determine if they should be split into multiple commits. Propose splitting when the changes contain logically independent units, such as:

- Different features or bug fixes
- Unrelated file groups (e.g., source code vs. configuration vs. documentation)
- Changes with different commit types (e.g., `skills` + `chore`)

If splitting is appropriate, present a proposed split plan (files and commit message per commit) to the user. After approval, execute each commit sequentially following steps 3-6 for each.

If the changes are cohesive and belong in a single commit, proceed directly.

### 3. Stage files

- Stage only the files relevant to the current task using `git add <file>...`.
- Never use `git add -A` or `git add .` unless the user explicitly requests it.
- Do not stage files that likely contain secrets (`.env`, credentials, tokens).

### 4. Compose a commit message

Look for the repository's own commit message conventions first — e.g. `docs/CONTRIBUTING.md`, `CONTRIBUTING.md`, a `commitlint` config, or an explicit convention in `CLAUDE.md`/`AGENTS.md`. Follow those rules if found. Only when the repository defines none of its own, fall back to `references/commit-rules.md`.

Key rules:

- Format: `<type>: <concise summary>`
- Write in English
- Summarize the *why*, not just the *what*
- Add an optional body (line 3+) only when the reason or context is non-obvious

### 5. Confirm with the user — only when committing directly to the default branch

Check the current branch and the repo's default branch:

```bash
git branch --show-current
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
```

- **Current branch is a topic/feature branch (not the default branch)** — skip
  confirmation and go straight to step 6.
- **Current branch IS the default branch** (committing directly to
  main/master) — present the proposed commit message and the list of staged
  files, and wait for approval before proceeding. If the user requests
  changes, revise and re-confirm.

### 6. Execute the commit

Run `git commit` with the approved message. Use a HEREDOC to pass the message:

```bash
git commit -m "$(cat <<'EOF'
<type>: <summary>

<optional body>
EOF
)"
```

After the commit completes, run `git status` to verify success and report the result.

## Important

- Never amend a previous commit unless the user explicitly requests it.
- Never push to a remote unless the user explicitly requests it.
- If a pre-commit hook fails, fix the issue, re-stage, and create a **new** commit (do not amend).
- Never add a `Co-Authored-By` trailer to the commit message.

## References

- `references/commit-rules.md` — fallback commit message format and type definitions, used only when the repository defines no conventions of its own
