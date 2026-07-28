# Commit Message Rules

This is a fallback convention. If the repository defines its own commit message rules (e.g. `docs/CONTRIBUTING.md`, `CONTRIBUTING.md`, a `commitlint` config, or an explicit convention in `CLAUDE.md`/`AGENTS.md`), follow the repository's rules instead of this file.

Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## Format

- Line 1: `<type>: <concise summary>`
- Line 2: (blank)
- Line 3: (Optional) Reason for the change or non-obvious supplementary notes.

## Rules

- Write in English.
- Scopes are not used.

## Types

- `feat`: Feature additions or changes
- `fix`: Bug fixes or corrections
- `build`: Build tool configuration changes
- `ai`: AI configuration changes (e.g. agent skills, prompts)
- `ci`: CI configuration changes
- `docs`: Add, update, or remove documentation
- `style`: Code style changes only
- `refactor`: Refactoring (restructuring headings, reordering lists, etc.)
- `perf`: Performance improvements
- `test`: Test additions or modifications
- `deps`: Dependency updates
- `chore`: Miscellaneous changes

## Examples

```txt
feat: Add quick-review skill
```

```txt
chore: Update linter configuration
```
