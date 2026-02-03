# Google Go Style Best Practices

This document provides guidance on applying Go Style effectively across common scenarios. It complements the core style guide and is neither normative nor canonical.

## Naming

### Function and Method Names

#### Avoid Repetition

When naming functions or methods, consider the call site context. Key recommendations include:

- Omit input/output types when unambiguous
- Don't repeat package names in function signatures
- Avoid restating receiver type names in method names
- Skip variable parameter names in function identities
- Exclude return value types from naming

**Example:**

```go
// Bad:
package yamlconfig
func ParseYAMLConfig(input string) (*Config, error)

// Good:
package yamlconfig
func Parse(input string) (*Config, error)
```

Use disambiguating information only when necessary for multiple similar functions.

#### Naming Conventions

- **Noun-like names** for functions returning values: "Avoid the `Get` prefix"
- **Verb-like names** for action-performing functions
- **Type suffixes** for identical functions differing only in types: `ParseInt`, `ParseInt64`

### Test Double and Helper Packages

Append `test` to package names for test helpers (e.g., `creditcardtest`). For simple cases with one test double type, use concise naming:

```go
// Good:
type Stub struct{}
func (Stub) Charge(*creditcard.Card, money.Money) error { return nil }
```

For multiple behaviors, name according to behavior:

```go
// Good:
type AlwaysCharges struct{}
type AlwaysDeclines struct{}
```

In test code, prefix variables to distinguish them from production types:

```go
// Good:
var spyCC creditcardtest.Spy
```

### Shadowing

**Stomping** occurs when a new variable isn't created via `:=`. This is acceptable when the original value becomes unnecessary.

**Shadowing** introduces a new variable in a new scope. The original becomes inaccessible after the block ends.

```go
// Good - stomping:
ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
defer cancel()

// Bad - shadowing bug:
if *shortenDeadlines {
    ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
    defer cancel()
}
// BUG: ctx here reverts to caller's context
```

Avoid shadowing standard package names, as it prevents accessing their functions.

### Util Packages

Package names should relate to functionality provided. Names like `util`, `helper`, or `common` are poor choices as they're uninformative and cause import conflicts.

Consider the call site:

```go
// Good:
db := spannertest.NewDatabaseFromFile(...)

// Bad:
db := test.NewDatabaseFromFile(...)
```

## Package Size

Key considerations:

- **Godoc visibility**: Users see one page per package with methods grouped by type
- **Implementation coupling**: Place tightly-coupled types together to access unexported identifiers
- **User convenience**: If users must import both packages meaningfully, combine them
- **No hard limits**: Go style is flexible; avoid thousands of lines per file and excessive tiny files

Files should be focused enough to locate code easily. The standard library demonstrates good layering patterns (e.g., `net/http` organizes by concern: client.go, server.go, cookie.go).

## Imports

### Protocol Buffer Messages and Stubs

Use conventional suffixes:

- `pb` for `go_proto_library` rules
- `grpc` for `go_grpc_library` rules

```go
// Good:
import (
    foopb "path/to/package/foo_service_go_proto"
    foogrpc "path/to/package/foo_service_go_grpc"
)
```

Prefer descriptive names over very short abbreviations. Use proto package names with a `pb` suffix when uncertain.

## Error Handling

### Error Structure

Provide structure for programmatic error interrogation:

```go
// Good:
var (
    ErrDuplicate = errors.New("duplicate")
    ErrMarsupial = errors.New("marsupials not supported")
)

func process(animal Animal) error {
    switch {
    case seen[animal]:
        return ErrDuplicate
    case marsupial(animal):
        return ErrMarsupial
    }
    return nil
}
```

Use `errors.Is()` with wrapped errors rather than string matching.

### Adding Information to Errors

Avoid redundant information already in underlying errors:

```go
// Good:
if err := os.Open("settings.txt"); err != nil {
    return fmt.Errorf("launch codes unavailable: %v", err)
}
// Output: launch codes unavailable: open settings.txt: no such file...

// Bad:
return fmt.Errorf("could not open settings.txt: %v", err)
// Duplicates path information already present
```

#### `%v` vs. `%w` in Error Wrapping

- **Use `%v`**: For simple annotations, logging display, or transforming errors at system boundaries (RPC/IPC)
- **Use `%w`**: For programmatic inspection within application helpers; allows `errors.Is()` and `errors.As()` checks

```go
// Good - preserves error chain:
if err != nil {
    return fmt.Errorf("couldn't find remote file: %w", err)
}
```

Prefer placing `%w` at the end for readable error chains: `[...]: %w` format.

### Logging Errors

- Avoid duplication; let callers decide whether to log
- Clearly express what failed with diagnostic information
- Be conscious of Personal Identifiable Information (PII)
- Use `log.Error` sparingly—it flushes and impacts performance
- Reserve ERROR level for actionable messages

Use verbose logging (`log.V`) for development tracing at different levels (1 for minimal, 2 for tracing, 3 for dumps).

### Program Initialization

Initialization errors should propagate to `main`, which calls `log.Exit` with an actionable message explaining how to fix the error. Avoid `log.Fatal` for setup failures.

### Program Checks and Panics

Standard error handling via return values is preferred. Call `log.Fatal` only when an unrecoverable invariant violation occurs.

#### When to Panic

- **API misuse**: Like `reflect` panicking on invalid access patterns (analogous to out-of-bounds slice access)
- **Internal implementation detail**: Panics must never escape package boundaries; use `defer` + `recover` at public API boundaries

```go
// Good:
type syntaxError struct { msg string }

func Parse(in string) (_ *Node, err error) {
    defer func() {
        if p := recover(); p != nil {
            if sErr, ok := p.(*syntaxError); ok {
                err = fmt.Errorf("syntax error: %v", sErr.msg)
            } else {
                panic(p) // Propagate unexpected panics
            }
        }
    }()
    // Parse logic calling internal functions that may panic
}
```

Panic is acceptable for unreachable code markers when the compiler cannot identify them.

## Documentation

### Conventions

#### Parameters and Configuration

Document error-prone or non-obvious fields rather than every parameter:

```go
// Good:
// Sprintf formats according to a format specifier and returns the resulting string.
// The provided data interpolates the format. If data doesn't match format verbs,
// warnings inline into the output as described by Format errors section.
func Sprintf(format string, data ...any) string

// Bad:
// format is the format, and data is the interpolation data. (Adds little value)
```

#### Contexts

Context cancellation is implied—don't restate it. Document special cases:

```go
// Good - special behavior documented:
// Run processes work until context cancellation or Stop() is called.
// Context cancellation is asynchronous; Run may return before all work stops.
func (Worker) Run(ctx context.Context) error
```

#### Concurrency

Assume conceptually read-only operations are safe for concurrent use without documentation. Document mutations and concurrency:

```go
// Good - documents non-standard behavior:
// Lookup returns cached data. This operation is not safe for concurrent use
// because LRU cache internals mutate on hit.
func (*Cache) Lookup(key string) ([]byte, bool)
```

#### Cleanup

Document explicit cleanup requirements:

```go
// Good:
// NewTicker returns a Ticker sending time after each tick.
// Call Stop to release associated resources when done.
func NewTicker(d Duration) *Ticker
```

#### Errors

Document significant error sentinels callers can anticipate:

```go
// Good:
// Read returns number of bytes read and any error encountered.
// At end of file, Read returns 0, io.EOF.
func (*File) Read(b []byte) (int, error)
```

Note whether error types use pointer receivers for correct `errors.Is()` comparisons.

### Godoc Formatting

- Blank lines separate paragraphs
- Runnable examples appear attached to documentation via `ExampleFunctionName()` test functions
- Indent lines by two additional spaces for verbatim formatting
- Capital-letter single-line text followed by a paragraph formats as a heading with auto-generated anchors

### Signal Boosting

Highlight non-obvious conditions with comments:

```go
// Good:
if err := doSomething(); err == nil { // if NO error
    // ...
}
```

## Variable Declarations

### Initialization

Prefer `:=` for new variables with non-zero values:

```go
// Good:
i := 42

// Bad:
var i = 42
```

### Zero Values

Declare variables using zero values when conveying an empty, ready-for-use state:

```go
// Good:
var (
    coords Point
    magic  [4]byte
    primes []int
)

// Bad:
var coords = Point{X: 0, Y: 0}
```

Common pattern for unmarshalling:

```go
// Good:
var coords Point
if err := json.Unmarshal(data, &coords); err != nil {
```

### Composite Literals

Use composite literals when knowing initial elements:

```go
// Good:
var captains = map[string]string{"Kirk": "James Tiberius", "Picard": "Jean-Luc"}
```

For zero-value pointers, either empty composite literals or `new()` work:

```go
// Good:
var buf = new(bytes.Buffer)
```

### Size Hints

Preallocate when final size is known (e.g., converting between map and slice):

```go
// Good:
var seen = make(map[string]bool, shardSize)
```

However, most code doesn't require preallocation. Default to zero initialization unless performance analysis warrants it.

**Warning**: Preallocating excess memory wastes resources fleet-wide. Benchmark before optimizing.

### Channel Direction

Specify channel direction to prevent casual errors:

```go
// Good:
func sum(values <-chan int) int {
    // ...
}

// Bad:
func sum(values chan int) (out int) {
    for v := range values {
        out += v
    }
    close(values) // Panic on second close!
}
```

## Function Argument Lists

Don't let function signatures grow excessively complex. As parameter count increases, individual parameter roles become unclear and adjacent same-type parameters invite confusion.

### Option Structure

Collect optional arguments into a struct passed as the final parameter:

```go
// Good:
type ReplicationOptions struct {
    Config              *replicator.Config
    PrimaryRegions      []string
    ReadonlyRegions     []string
    ReplicateExisting   bool
    OverwritePolicies   bool
    ReplicationInterval time.Duration
    CopyWorkers         int
    HealthWatcher       health.Watcher
}

func EnableReplication(ctx context.Context, opts ReplicationOptions) {
    // ...
}

// Call:
storage.EnableReplication(ctx, storage.ReplicationOptions{
    Config:              config,
    PrimaryRegions:      []string{"us-east1", "us-central2"},
    OverwritePolicies:   true,
    ReplicationInterval: 1 * time.Hour,
})
```

**Benefits**: Self-documenting, omit defaults, share across functions, grow without breaking calls.

### Variadic Options

Use exported option functions returning closures for substantial flexibility:

```go
// Good:
type ReplicationOption func(*replicationOptions)

func ReadonlyCells(cells ...string) ReplicationOption {
    return func(opts *replicationOptions) {
        opts.readonlyCells = append(opts.readonlyCells, cells...)
    }
}

func EnableReplication(ctx context.Context, config *placer.Config, 
    primaryCells []string, opts ...ReplicationOption) {
    var options replicationOptions
    for _, opt := range opts {
        opt(&options)
    }
}

// Call:
storage.EnableReplication(ctx, config, []string{"po", "is", "ea"},
    storage.ReadonlyCells("ix", "gg"),
    storage.OverwritePolicies(true),
)
```

**Prefer when**: Most callers don't specify options, most options are infrequent, many options exist, options require arguments, or users can provide custom options.

Options should accept parameters rather than using presence alone (e.g., prefer `rpc.FailFast(enable bool)` over `rpc.EnableFailFast()`).

## Complex Command-Line Interfaces

For programs with sub-commands, libraries include:

- **[cobra](https://pkg.go.dev/github.com/spf13/cobra)**: Getopt conventions, many features, common outside Google
- **[subcommands](https://pkg.go.dev/github.com/google/subcommands)**: Go flag conventions, simple, recommended as default

**Warning**: With cobra, use `cmd.Context()` to obtain context rather than creating root contexts with `context.Background`.

Subcommands need not live in separate packages; apply standard package boundary considerations.

## Tests

### Leave Testing to the Test Function

Go distinguishes between test helpers (setup/cleanup) and assertion helpers (checking correctness). Assertion helpers are [not idiomatic](guide#assert).

The ideal place to fail a test is within the `Test` function itself for clarity. When factoring out functionality, validation functions should return values (typically `error`) rather than calling `testing.T` directly:

```go
// Good:
func polygonCmp() cmp.Option {
    return cmp.Options{
        cmp.Transformer("polygon", func(p *s2.Polygon) []*s2.Loop { 
            return p.Loops() 
        }),
        cmpopts.EquateApprox(0.00000001, 0),
    }
}

func TestFenceposts(t *testing.T) {
    got := Fencepost(tomsDiner, 1*meter)
    if diff := cmp.Diff(want, got, polygonCmp()); diff != "" {
        t.Errorf("Fencepost(tomsDiner, 1m) returned unexpected diff:\n%v", diff)
    }
}
```

### Designing Extensible Validation APIs

**Acceptance testing** validates user-implemented types against library requirements. Create a test package and exercise the implementation as a blackbox:

```go
// Good - acceptance test:
func ExercisePlayer(b *chess.Board, p chess.Player) error
```

Fail fast returning errors, or aggregate all failures depending on execution time expectations.

### Use Real Transports

When testing component integrations with HTTP/RPC, use the real transport connecting to a test double (mock/stub/fake) backend:

```go
// Good:
// Use real OperationsClient connected to test OperationsServer
client := longrunning.NewOperationsClient(testConn)
```

This ensures tests use as much real code as possible rather than hand-implementing clients.

### `t.Error` vs. `t.Fatal`

Generally, tests should not abort at the first problem. Use `t.Fatal` appropriately:

- **Test setup failures**: Setup functions failing without which tests cannot run
- **Table-driven tests before the loop**: Failures affecting the entire test
- **Within `t.Run` subtests**: Ends the subtest; test progresses to the next entry
- **Multiple table entries outside subtests**: Use `t.Error` + `continue` to skip

**Warning**: It's not safe to call `t.Fatal` from separate goroutines (see next section).

### Error Handling in Test Helpers

Test helper failures often signify unmet setup preconditions. Call `Fatal` functions:

```go
// Good:
func mustAddGameAssets(t *testing.T, dir string) {
    t.Helper()
    if err := os.WriteFile(path.Join(dir, "pak0.pak"), pak0, 0644); 
        err != nil {
        t.Fatalf("Setup failed: could not write pak0 asset: %v", err)
    }
}
```

Include descriptive failure messages. Use `t.Cleanup` (Go 1.14+) to register cleanup functions running when tests complete.

### Don't Call `t.Fatal` from Separate Goroutines

It's incorrect to call `t.FailNow`, `t.Fatal`, etc. from goroutines other than the test function itself. Use `t.Error` + `return` instead:

```go
// Good:
go func() {
    defer wg.Done()
    if err := engine.Vroom(); err != nil {
        t.Errorf("No vroom left on engine: %v", err) // Not t.Fatalf
        return
    }
}()
```

### Use Field Names in Struct Literals

For table-driven tests spanning many lines or with adjacent same-type fields, specify field names:

```go
// Good:
tests := []struct {
    slice     []string
    separator string
    skipEmpty bool
    want      string
}{
    {
        slice:     []string{"a", "b", ""},
        separator: ",",
        want:      "a,b,",
    },
    {
        slice:     []string{"a", "b", ""},
        separator: ",",
        skipEmpty: true,
        want:      "a,b",
    },
}
```

### Keep Setup Code Scoped to Specific Tests

Call setup functions explicitly in tests needing them rather than in shared setup:

```go
// Good:
func TestParseData(t *testing.T) {
    data := mustLoadDataset(t)
    parsed, err := ParseData(data)
    if err != nil {
        t.Fatalf("Unexpected error parsing data: %v", err)
    }
    // ...
}
```

---

**Note**: This summary captures core guidance from Google's Go Style Best Practices. Consult the full document for comprehensive coverage and additional examples.
