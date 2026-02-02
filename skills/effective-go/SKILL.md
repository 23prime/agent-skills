---
name: effective-go
description: Apply best practices and conventions from the official Effective Go guide to write clean, idiomatic Go code. This skill should be used when writing, reviewing, or refactoring Go code to ensure it follows established Go conventions for naming, formatting, error handling, concurrency, and program structure.
---

# Effective Go

## Overview

This skill provides the complete Effective Go reference material, enabling idiomatic Go code that follows the conventions established by the Go team. Consult the relevant reference files when making decisions about Go code style, structure, or patterns.

## When to use

- Writing new Go code (functions, types, packages)
- Reviewing or refactoring existing Go code
- Deciding on naming conventions, error handling patterns, or concurrency approaches
- Resolving questions about idiomatic Go style

## Reference guide

The `references/` directory contains the full Effective Go guide split by topic. Load the relevant file(s) based on the task at hand:

| File | Topic | When to consult |
| ------ | ------- | ----------------- |
| `01-introduction.md` | Introduction and examples | General orientation |
| `02-formatting.md` | gofmt, indentation, line length, parentheses | Formatting questions |
| `03-commentary.md` | Comments and doc comments | Writing documentation |
| `04-names.md` | Package names, getters, interfaces, MixedCaps | Naming decisions |
| `05-semicolons.md` | Semicolon insertion rules, brace placement | Syntax questions |
| `06-control-structures.md` | if, for, switch, type switch | Control flow patterns |
| `07-functions.md` | Multiple returns, named results, defer | Function design |
| `08-data.md` | new vs make, slices, maps, printing, append | Data structure usage |
| `09-initialization.md` | Constants, iota, variables, init functions | Initialization patterns |
| `10-methods.md` | Pointer vs value receivers | Method design |
| `11-interfaces-and-other-types.md` | Interfaces, conversions, type assertions, generality | Interface design |
| `12-blank-identifier.md` | Blank identifier, unused imports, interface checks | Blank identifier idioms |
| `13-embedding.md` | Interface and struct embedding, name conflicts | Composition patterns |
| `14-concurrency.md` | Goroutines, channels, parallelization, leaky buffer | Concurrent programming |
| `15-errors.md` | Error types, panic, recover | Error handling |

## Key principles

To write idiomatic Go, apply these high-level principles (details in the reference files):

- **Formatting**: Run `gofmt`. Do not fight the formatter.
- **Naming**: Short, concise names. No `Get` prefix on getters. `MixedCaps` not underscores. Package name avoids stutter (`bufio.Reader` not `bufio.BufReader`).
- **Control flow**: Eliminate unnecessary `else` after `return`. Use `switch` over `if-else` chains. Keep the happy path unindented.
- **Error handling**: Return errors as the last return value. Wrap with context. Prefer `error` over `panic`.
- **Concurrency**: Share memory by communicating. Use channels for synchronization. Prefer fixed worker pools over unbounded goroutine creation.
- **Interfaces**: Accept interfaces, return concrete types. One-method interfaces get `-er` suffix. Use compile-time interface checks (`var _ Interface = (*Type)(nil)`).
- **Composition**: Prefer embedding over inheritance-style patterns. Use composite literals over field-by-field initialization.
