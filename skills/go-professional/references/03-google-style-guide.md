# Google Go Style Guide

## Overview

This is Google's normative and canonical style guide for Go code. The document establishes principles for writing readable, maintainable Go code within Google's codebase.

## Style Principles

The guide identifies five core attributes of readable code, ranked by importance:

1. **Clarity** – Code's purpose and rationale are evident to readers
2. **Simplicity** – Goals achieved through the most straightforward approach
3. **Concision** – High signal-to-noise ratio with minimal clutter
4. **Maintainability** – Code designed for easy future modification
5. **Consistency** – Alignment with broader codebase patterns

### Clarity

Readability focuses on the reader's perspective rather than the author's. Two dimensions matter:

- **Purpose**: What the code does should be apparent through descriptive naming, comments, whitespace, and modular structure
- **Rationale**: Why the code works this way requires explanation when dealing with language nuances, business logic subtleties, or non-obvious API usage

The guide emphasizes that "comments that explain why, not what, the code is doing" prevent future misunderstandings. Self-describing symbol names are preferable to redundant commentary.

### Simplicity

"Go code should be written in the simplest way that accomplishes its goals." Simple code:

- Reads logically from top to bottom
- Avoids unnecessary abstraction layers
- Clarifies value propagation and decisions
- Provides useful error messages and test diagnostics

Complexity should be introduced deliberately—typically for performance optimization—and accompanied by documentation explaining the rationale.

The principle of **least mechanism** recommends preferring: core language constructs first, then standard library tools, then Google's internal libraries before external dependencies.

### Concision

Concise code highlights relevant details through clear naming and structure. Mechanisms that reduce repetition—such as table-driven testing—improve signal-to-noise ratios. Readers should quickly recognize common idioms; deviations warrant explanatory comments.

### Maintainability

Code undergoes far more editing than initial writing. Maintainable code:

- Guides future programmers toward correct modifications
- Employs APIs that grow gracefully
- Avoids unnecessary coupling
- Includes comprehensive tests with clear diagnostics

Abstractions like interfaces and types remove context information. They require careful documentation to justify their complexity costs.

### Consistency

Consistent code aligns with broader codebase patterns and team conventions. When style guide principles conflict, consistency often breaks the tie—particularly within a package.

## Core Guidelines

### Formatting

All Go files must conform to output from the `gofmt` tool, enforced through presubmit checks. Generated code should also be formatted using tools like `format.Source`.

### Naming Conventions

Go uses `MixedCaps` for exported identifiers and `mixedCaps` for unexported ones, following camel case rather than snake case (e.g., `MaxLength`, not `MAX_LENGTH`).

### Line Length

No fixed line length applies. Refactoring is preferred over line splitting. Lines should not break before indentation changes or to accommodate long strings like URLs.

### Naming Guidance

Names should avoid repetition in usage contexts and resist repeating concepts already evident. More specific guidance appears in the style guide's decisions section.

### Local Consistency

When the guide provides no guidance, teams may establish consistent local practices within files or packages. Invalid local considerations include line-length restrictions or assertion-based testing libraries. Deviations must not worsen existing issues or introduce bugs.

---

**Source**: [Google Style Guide – Go](https://google.github.io/styleguide/go/guide)
