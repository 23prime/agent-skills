# Contributing Guide

## Branch Strategy

### Branches

- `main`: Main (default) branch.
- `skills/xxxx`: Branches for agent skill work.
- `feature/xxxx`: Branches for other work.

### Approval Flow

- Changes to the `main` branch are made exclusively through pull requests.
- Merging requires approval from at least one reviewer. Reviewers should be discussed and assigned as needed.

## Commit Messages

- Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
- Scopes are optional but encouraged.
- Commit messages should be written in English.
- Commit message content:
  - Line 1: A concise summary of the change.
  - Line 3: (Optional) Reason for the change or non-obvious supplementary notes.

### Types

- `skills`: Add, update, or remove agent skills
- `docs`: Add, update, or remove documentation
- `style`: Code style changes only
- `refactor`: Refactoring (restructuring headings, reordering lists, etc.)
- `ci`: CI configuration changes
- `deps`: Dependency updates
- `chore`: Miscellaneous changes

### Scopes

Scopes are not used.

### Examples

```txt
skills: Add quick-review skill
```

```txt
chore: Update linter configuration
```

## Documentation Quality Assurance

Before committing, run the following to check and auto-fix, and confirm it passes.

1. Run markdown lint (check + auto-fix)

    ```sh
    mise fix-md
    ```

## Pull Requests

Create a pull request following the [template](.github/PULL_REQUEST_TEMPLATE.md).
