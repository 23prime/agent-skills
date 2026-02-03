# Google Go Style Decisions

This document contains style decisions for Go programming at Google, complementing the core style guide. It provides standard guidance, explanations, and examples for Go readability mentors.

## Naming

### Underscores

Names in Go generally avoid underscores with three exceptions:

- Package names imported only by generated code
- Test/Benchmark/Example function names in `*_test.go` files
- Low-level OS/cgo interop libraries (rare)

### Package Names

Package names must be concise, lowercase, and use only letters/numbers. Multi-word packages remain unbroken in lowercase (e.g., `tabwriter` not `tab_writer`). Avoid names likely shadowed by common variables like `count`. Generated proto packages must be renamed to remove underscores and use a `pb` suffix.

### Receiver Names

Method receivers should be short (1-2 letters), abbreviations of the type, applied consistently:

- `func (t Tray)` instead of `func (tray Tray)`
- `func (ri *ResearchInfo)` instead of `func (info *ResearchInfo)`

### Constant Names

Constants use MixedCaps (exported start uppercase, unexported lowercase). Names should reflect the constant's role, not its value:

```go
// Good:
const MaxPacketSize = 512
const ExecuteBit = 1 << iota

// Bad:
const MAX_PACKET_SIZE = 512
const kMaxBufferSize = 1024
```

### Initialisms

Acronyms maintain consistent casing: `URL` or `url`, never `Url`. In compound names like `XMLAPI`, each initialism maintains consistent case. Mixed-case initialisms like `iOS` appear as `IOS` (exported) or `iOS` (unexported) unless changing exportedness:

| Usage | Exported | Unexported |
| ------- | ---------- | ----------- |
| XML API | `XMLAPI` | `xmlAPI` |
| iOS | `IOS` | `iOS` |
| gRPC | `GRPC` | `gRPC` |

### Getters

Omit "Get" prefixes unless the concept uses "get" (e.g., HTTP GET). Prefer `Counts()` over `GetCounts()`. Use `Compute` or `Fetch` for complex/remote operations.

### Variable Names

Name length should be proportional to scope size and inversely proportional to usage frequency:

- **Small scope (1-7 lines):** Short names acceptable
- **Medium scope (8-15 lines):** More descriptive names needed
- **Large scope (15-25 lines+):** Detailed names required

Avoid redundant type information: `userCount` beats `numUsers` or `usersInt`. Omit context-clear words—in a `UserCount` method, use `count` not `userCount`.

#### Single-Letter Variables

Acceptable for method receivers, familiar type variables (`r` for `io.Reader`), loop indices (`i`), and coordinates (`x`, `y`). Short-scope abbreviations work when obvious.

### Repetition Issues

**Package vs. exported symbol:** Reduce redundancy between package name and exported types:

- `widget.NewWidget` → `widget.New`
- `db.LoadFromDatabase` → `db.Load`

**Variable name vs. type:** Compiler knows types; omit type information if context clarifies it:

- `numUsers` → `users`
- `nameString` → `name`
- `primaryProject` → `primary` (if only one version in scope)

**External context vs. local names:** Package/method/type names provide context; avoid repeating:

- In package `ads/targeting/revenue/reporting`: use `Report` not `AdsTargetingRevenueReport`
- In method on `Project`: use `Name()` not `ProjectName()`
- In package `sqldb`: use `Connection` not `DBConnection`

## Commentary

### Comment Line Length

Aim for 80-column width on narrow terminals, though comments can exceed this. Break based on punctuation when needed (60-70 characters common in standard library). Don't rewrap existing code solely for this guideline—teams should apply opportunistically during refactors.

### Doc Comments

All top-level exported names need doc comments, as should unexported declarations with unobvious behavior. Comments should be complete sentences beginning with the object name:

```go
// Good:
// A Request represents a command execution request.
type Request struct { ... }

// Encode writes the JSON encoding of req to w.
func Encode(w io.Writer, req *Request) { ... }
```

### Comment Sentences

Complete sentences must be capitalized and punctuated. Fragments have no such requirements. Documentation comments always require complete sentences; simple field comments can be phrases assuming the field name as subject.

### Examples

Provide runnable examples in test files; they appear in Godoc. For infeasible runnable examples, use code snippets in comments following standard formatting conventions.

### Named Result Parameters

Name result parameters when a function returns multiple parameters of the same type or when names clarify required caller actions:

```go
// Good:
func (n *Node) Children() (left, right *Node, err error)

// WithTimeout documents the returned cancel function requirement:
func WithTimeout(parent Context, d time.Duration) (ctx Context, cancel func())
```

Avoid named results causing repetition or enabling naked returns inappropriately. Clarity trumps saved lines.

### Package Comments

Package comments appear immediately above the package clause (no blank line):

```go
// Good:
// Package math provides basic constants and mathematical functions.
package math
```

One comment per package. For `main` packages, name the binary from the BUILD file:

```go
// Good:
// The seed_generator command generates a Finch seed file from JSON configs.
package main
```

Alternative styles: `Binary seed_generator ...`, `Command seed_generator ...`, `Program seed_generator ...`

## Imports

### Import Renaming

Generally avoid renaming imports. Rename when necessary to avoid collisions (prefer renaming local/project-specific imports) or to remove underscores from generated proto packages:

```go
// Good:
import (
    foosvcpb "path/to/package/foo_service_go_proto"
)
```

Rename uninformative third-party packages (`util`, `v1`) sparingly:

```go
// Good:
import (
    core "github.com/kubernetes/api/core/v1"
)
```

### Import Grouping

Order imports in four groups:

1. Standard library
2. Project/vendored packages
3. Protocol Buffer imports
4. Side-effect imports

```go
// Good:
import (
    "fmt"
    "os"

    "github.com/dsnet/compress/flate"
    "google.golang.org/protobuf/proto"

    foopb "myproj/foo/proto/proto"

    _ "myproj/rpc/protocols/dial"
)
```

### Blank Imports

Limit `import _` to main packages and tests. Exceptions: bypassing nogo checks or using `//go:embed`. Avoid in library packages to control dependencies.

### Dot Imports

Do not use `import .` syntax; it obscures symbol origins. Always qualify imported names.

## Errors

### Returning Errors

Use `error` as the last result parameter to signal potential failure. Return `nil` for success:

```go
// Good:
func Good() error { /* ... */ }
func GoodLookup() (*Result, error) { /* ... */ }
```

Exported functions returning errors should use the `error` type, not concrete types (avoids concrete `nil` pointer wrapping bugs).

### Error Strings

Error strings should not be capitalized (except proper nouns/acronyms) or end with punctuation, as they typically appear within other context:

```go
// Good:
err := fmt.Errorf("something bad happened")

// Logging context can be capitalized:
log.Errorf("Operation failed: %v", err)
```

### Handling Errors

Address errors deliberately—handle immediately, return to caller, or in rare cases call `log.Fatal` or `panic`. Don't discard errors with `_` without explaining why:

```go
// Good:
n, _ := b.Write(p) // never returns a non-nil error
```

### In-Band Errors

Avoid returning special values (-1, null, empty string) to signal errors. Use multiple return values:

```go
// Bad:
func Lookup(key string) int // returns -1 on failure

// Good:
func Lookup(key string) (value string, ok bool)
```

### Indenting Error Flow

Handle errors early and continue with normal code after the `if` block, avoiding nested `else`:

```go
// Good:
if err != nil {
    // error handling
    return
}
// normal code

// Bad:
if err != nil {
    // error handling
} else {
    // normal code indented awkwardly
}
```

## Language

### Literal Formatting

#### Field Names

Struct literals for external package types must specify field names:

```go
// Good:
r := csv.Reader{
    Comma: ',',
    Comment: '#',
}

// Bad:
r := csv.Reader{',', '#', 4, false}
```

Package-local types are optional but recommended for clarity.

#### Matching Braces

Closing braces align with opening brace indentation. Multi-line literals have closing braces on their own line with trailing commas:

```go
// Good:
good := []*Type{{Key: "value"}}

good := []*Type{
    {Key: "multi"},
    {Key: "line"},
}

// Bad:
bad := []*Type{
    {Key: "multi"},
    {Key: "line"}}
```

#### Cuddled Braces

Only cuddle braces when indentation matches and inner values are literals/proto builders:

```go
// Good:
good := []*Type{{ // Cuddled correctly
    Field: "value",
}, {
    Field: "value",
}}
```

#### Repeated Type Names

Omit repeated type names in slice/map literals:

```go
// Good:
good := []*Type{
    {A: 42},
    {A: 43},
}

// Bad:
repetitive := []*Type{
    &Type{A: 42},
    &Type{A: 43},
}
```

#### Zero-Value Fields

Omit zero-value fields when clarity isn't lost:

```go
// Good:
ldb := leveldb.Open("/table", &db.Options{
    BlockSize: 1<<16,
    ErrorIfDBExists: true,
})
```

### Nil Slices

For local variables, prefer `nil` initialization to reduce caller bugs:

```go
// Good:
var t []string

// Bad:
t := []string{}
```

Design APIs not forcing distinctions between `nil` and empty slices. Use `len()` checks instead of `== nil`.

### Indentation Confusion

Avoid line breaks aligning with indented code blocks. If unavoidable, leave a space separating them.

### Function Formatting

Keep function signatures on one line to avoid indentation confusion:

```go
// Bad:
func (r *SomeType) SomeLongFunctionName(foo1, foo2 string,
    foo3, foo4 int) { // Looks like function body
    foo5 := bar(foo1)
}
```

Factor out locals to shorten calls. Avoid adding inline comments to specific arguments; use option structs instead.

### Conditionals and Loops

Avoid line-breaking `if` statements; extract boolean operands:

```go
// Good:
inTransaction := db.CurrentStatusIs(db.InTransaction)
keysMatch := db.ValuesEqual(db.TransactionKey(), row.Key())
if inTransaction && keysMatch {
    return db.Error(...)
}

// Bad:
if db.CurrentStatusIs(db.InTransaction) &&
    db.ValuesEqual(db.TransactionKey(), row.Key()) {
    return db.Error(...)
}
```

Ensure braces match to avoid indentation confusion. Keep `switch` and `case` on single lines unless excessively long—then indent all cases.

### Copying

Avoid copying structs with synchronization objects (like `sync.Mutex`) or optimization arrays. Don't copy values where methods associate with pointer type `*T`:

```go
// Bad:
b1 := bytes.Buffer{}
b2 := b1 // Creates copy with aliased internals
```

### Don't Panic

Use `error` and multiple returns for normal error handling. Within `package main` and initialization code, consider `log.Exit` for terminating errors. Reserve `panic` for "impossible" bugs caught during review/testing.

### Must Functions

Setup helpers following `MustXYZ` naming convention should only be called early during startup, not on user input:

```go
// Good:
func MustParse(version string) *Version {
    v, err := Parse(version)
    if err != nil {
        panic(fmt.Sprintf("MustParse(%q) failed: %v", version, err))
    }
    return v
}

var DefaultVersion = MustParse("1.2.3")
```

### Goroutine Lifetimes

Make goroutine exit conditions obvious. Use `context.Context` for conventional management:

```go
// Good:
func (w *Worker) Run(ctx context.Context) error {
    var wg sync.WaitGroup
    for item := range w.q {
        wg.Add(1)
        go func() {
            defer wg.Done()
            process(ctx, item)
        }()
    }
    wg.Wait() // Prevent goroutines from outliving function
}
```

Document when/why goroutines exit. Avoid leaving goroutines in-flight indefinitely.

### Interfaces

Interfaces belong in consuming packages, not implementing packages. Return concrete types from functions. Don't export test double implementations. Design APIs testable via public APIs of real implementations. Don't define interfaces before usage; use realistic examples first.

```go
// Good:
package consumer
type Thinger interface { Thing() bool }
func Foo(t Thinger) string { ... }

// Good in tests:
type fakeThinger struct{ ... }
func (t fakeThinger) Thing() bool { ... }

// Bad:
package producer
type Thinger interface { Thing() bool }
func NewThinger() Thinger { ... }
```

### Generics

Use generics where they fulfill business requirements. Avoid premature use or creating domain-specific languages. Start with concrete types; add polymorphism later if needed. Don't use `any` type with excessive type switching when interfaces suffice.

### Pass Values

Don't pass pointers merely to save bytes. If a function only reads `*x`, pass by value. Exception: large structs and protocol buffer messages (pass by pointer).

### Receiver Type

Choose based on correctness, not speed. Use pointers when:

- Method must mutate receiver
- Receiver contains non-copyable fields (`sync.Mutex`)
- Receiver is large
- Method modifies receiver where visibility matters
- Receiver is struct containing pointer fields

Use values for:

- Slices (if not reslicing/reallocating)
- Built-in types unchanged
- Plain old data types

Prefer consistent all-value or all-pointer methods per type.

### `switch` and `break`

Don't use redundant `break` statements; Go's `switch` auto-breaks. Use comments for empty clauses. Use labels with `break` to exit enclosing loops.

### Synchronous Functions

Prefer synchronous functions returning results directly. Callers can add concurrency by calling in separate goroutines. Synchronous functions simplify reasoning and testing.

### Type Aliases

Use type definitions (`type T1 T2`) for new types. Reserve type aliases (`type T1 = T2`) for migration; they're rare.

### Use %q

Prefer `%q` formatting for readable string output:

```go
// Good:
fmt.Printf("value %q looks like text", someText)

// Bad:
fmt.Printf("value \"%s\" looks like text", someText)
```

### Use any

Go 1.18+ provides `any` as an `interface{}` alias. Prefer `any` in new code.

## Common Libraries

### Flags

Internal Google code uses a custom `flag` package variant. Flag names use snake_case; variables use MixedCaps:

```go
// Good:
var (
    pollInterval = flag.Duration("poll_interval", time.Minute, "Polling interval.")
)
```

Define flags only in `package main`. General packages configure via APIs, not CLI flags.

### Logging

Google codebase uses a custom `log` package variant (open source: `glog`). Use `log.Fatal` for abnormal exits with stacktrace; `log.Exit` without stacktrace. No `log.Panic` exists. Prefer non-formatting versions when no formatting needed.

### Contexts

`context.Context` carries credentials, tracing, deadlines, and cancellation. Always pass as first parameter:

```go
func F(ctx context.Context /* others */) {}
```

Exceptions:

- HTTP handlers: use `req.Context()`
- Streaming RPCs: use stream's context
- Entrypoints: use `context.Background()` or `tb.Context()`

Never add context fields to structs; pass as parameters. Don't create custom context types—use standard `context.Context` exclusively.

### crypto/rand

Never use `math/rand` for keys; use `crypto/rand`:

```go
// Good:
import "crypto/rand"
func Key() string {
    buf := make([]byte, 16)
    if _, err := rand.Read(buf); err != nil {
        log.Fatalf("Randomness failed: %v", err)
    }
    return fmt.Sprintf("%x", buf)
}
```

## Useful Test Failures

Tests should diagnose failures without reading source. Include:

- Cause of failure
- Inputs producing error
- Actual result
- Expected result

### Avoid Assertion Libraries

Don't create assertion helpers combining validation and failure messages. They fragment experience and omit relevant context:

```go
// Good: Compare directly
if !cmp.Equal(got, want) {
    t.Errorf("Blog() = %v, want %v", got, want)
}

// Bad: Assertion library
assert.StringEq(t, "obj.Type", obj.Type, "blogPost")
```

Use standard libraries like `cmp` and `fmt` instead.

### Identify the Function

Include function names in failures: `YourFunc(%v) = %v, want %v` not just `got %v, want %v`.

### Identify the Input

Include inputs if short. For large/opaque inputs, use descriptive test case names.

### Got Before Want

Show actual values before expected. Standard format: `YourFunc(%v) = %v, want %v`. For diffs, include explicit direction indicators.

### Full Structure Comparisons

Compare complete data structures directly using deep comparison:

```go
// Good:
want := &Doc{Type: "post", Comments: 2}
if !cmp.Equal(got, want) {
    t.Errorf("AddPost() = %+v, want %+v", got, want)
}
```

For approximate equality or uncomparable fields, use `cmp.Diff` with `cmpopts` options.

### Compare Stable Results

Avoid comparing output depending on unstable package behavior. For formatted strings/serialized bytes, compare semantic equivalence instead:

```go
// Good: Parse and compare structure
var got, want map[string]interface{}
json.Unmarshal(gotBytes, &got)
json.Unmarshal(wantBytes, &want)
if !reflect.DeepEqual(got, want) {
    t.Errorf(...)
}
```

### Keep Going

Use `t.Error` to continue testing after failures, showing all issues in one run. Call `t.Fatal` only when subsequent tests would be meaningless:

```go
// Good: Multiple errors reported
if diff := cmp.Diff(wantMean, gotMean); diff != "" {
    t.Errorf("Mean diff: %s", diff)
}
if diff := cmp.Diff(wantVariance, gotVariance); diff != "" {
    t.Errorf("Variance diff: %s", diff)
}

// Good: Fatal makes subsequent tests pointless
if gotEncoded != wantEncoded {
    t.Fatalf("Encode failed: got %q, want %q", gotEncoded, wantEncoded)
}
```

For table-driven tests, consider subtests with `t.Fatal` rather than `t.Error` + `continue`.

---

**Document Status:** This is a normative but non-canonical document subordinate to the core style guide. It will grow over time and should be updated when contradicted by the guide.
