---
name: go-professional
description: Comprehensive Go style, code review, and best practices guide based on Effective Go, Go Code Review Comments, and Google Go Style Guide. This skill should be used when writing, reviewing, or refactoring Go code to ensure it follows professional-grade conventions for naming, error handling, interfaces, concurrency, testing, and program structure.
---

# Go Professional

## Overview

This skill integrates three authoritative Go style references into a single comprehensive resource:

- **Effective Go** — The official guide by the Go team covering idiomatic Go patterns, conventions, and language mechanics.
- **Go Code Review Comments** — Community-maintained supplement to Effective Go, collecting common code review feedback and style issues.
- **Google Go Style Guide** — Google's internal Go style guide covering style principles, decisions, and best practices for large-scale Go codebases.

These sources complement each other: Effective Go teaches the language idioms, Code Review Comments addresses frequent real-world mistakes, and the Google Style Guide provides comprehensive rules for professional teams.

## When to use

- Writing new Go code (packages, types, functions)
- Reviewing or refactoring existing Go code
- Resolving naming, formatting, or structural questions
- Designing error handling, interfaces, or concurrency patterns
- Establishing team coding standards or review checklists
- Onboarding developers to Go best practices

## Reference guide

Load the relevant file(s) from `references/` based on the task.

> **Note**: The `ja/` subdirectories contain Japanese translations for human reference. Always load the English originals for processing.

### Effective Go (`references/01-effective-go/`)

| File | Topic | When to consult |
| ------ | ------- | ----------------- |
| `01-introduction.md` | Introduction and examples | General orientation |
| `02-formatting.md` | gofmt, indentation, line length | Formatting questions |
| `03-commentary.md` | Comments and doc comments | Writing documentation |
| `04-names.md` | Package names, getters, interfaces, MixedCaps | Naming decisions |
| `05-semicolons.md` | Semicolon insertion rules | Syntax questions |
| `06-control-structures.md` | if, for, switch, type switch | Control flow patterns |
| `07-functions.md` | Multiple returns, named results, defer | Function design |
| `08-data.md` | new vs make, slices, maps, printing, append | Data structure usage |
| `09-initialization.md` | Constants, iota, variables, init functions | Initialization patterns |
| `10-methods.md` | Pointer vs value receivers | Method design |
| `11-interfaces-and-other-types.md` | Interfaces, conversions, type assertions | Interface design |
| `12-blank-identifier.md` | Blank identifier, unused imports | Blank identifier idioms |
| `13-embedding.md` | Interface and struct embedding | Composition patterns |
| `14-concurrency.md` | Goroutines, channels, parallelization | Concurrent programming |
| `15-errors.md` | Error types, panic, recover | Error handling |

### Supplementary references (`references/`)

| File | Source | When to consult |
| ------ | -------- | ----------------- |
| `02-code-review-comments.md` | Go Wiki | Code reviews, common style issues, naming, error handling |
| `03-google-style-guide.md` | Google | Style principles, readability, consistency guidelines |
| `04-google-style-decisions.md` | Google | Specific style decisions: naming, formatting, patterns |
| `05-google-best-practices.md` | Google | Practical guidance: testing, error handling, concurrency |

## Quick reference

Essential rules across all three sources:

- **Formatting**: Run `gofmt`. Do not fight the formatter.
- **Naming**: Short, concise names. `MixedCaps` not underscores. No `Get` prefix on getters. Package name avoids stutter (`bufio.Reader` not `bufio.BufReader`). Use `ctx` for `context.Context`, `err` for errors.
- **Control flow**: Eliminate unnecessary `else` after `return`. Keep the happy path unindented. Use `switch` over `if-else` chains.
- **Error handling**: Return errors as the last return value. Wrap with context (`fmt.Errorf("op: %w", err)`). Handle errors immediately; do not ignore them. Prefer `error` over `panic`.
- **Error strings**: Lower-case, no punctuation — they may be composed with other messages.
- **Interfaces**: Accept interfaces, return concrete types. One-method interfaces get `-er` suffix. Define interfaces at the consumer, not the implementer. Use compile-time checks (`var _ Interface = (*Type)(nil)`).
- **Concurrency**: Share memory by communicating. Use channels for synchronization. Prefer fixed worker pools. Do not start goroutines without knowing how they stop.
- **Package design**: Avoid `package util`. Do not export unnecessarily. Separate packages by responsibility, not by type.
- **Testing**: Use table-driven tests. Test behavior, not implementation. Use `t.Helper()` in test helpers.
- **Comments**: Every exported name needs a doc comment. Start with the name of the thing being described.
- **Imports**: Group into standard library, third-party, and local packages. Do not use dot imports except in tests.
