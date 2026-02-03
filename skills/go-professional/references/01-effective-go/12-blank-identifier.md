# The blank identifier

The blank identifier (`_`) can be assigned or declared with any value of any type, with the value discarded harmlessly. It's like writing to the Unix `/dev/null` file: it represents a write-only value to be used as a place-holder where a variable is needed but the actual value is irrelevant.

## The blank identifier in multiple assignment

The blank identifier is used in multiple assignment situations to discard unwanted return values:

```go
if _, err := os.Stat(path); os.IsNotExist(err) {
    fmt.Printf("%s does not exist\n", path)
}
```

**Important:** Avoid discarding error values to ignore errors. Always check error returns:

```go
// Bad! This code will crash if path does not exist.
fi, _ := os.Stat(path)
if fi.IsDir() {
    fmt.Printf("%s is a directory\n", path)
}
```

## Unused imports and variables

It is an error to import a package or declare a variable without using it. Unused imports bloat the program and slow compilation. When a program is under active development, the blank identifier provides a workaround:

```go
package main

import (
    "fmt"
    "io"
    "log"
    "os"
)

var _ = fmt.Printf // For debugging; delete when done.
var _ io.Reader    // For debugging; delete when done.

func main() {
    fd, err := os.Open("test.go")
    if err != nil {
        log.Fatal(err)
    }
    // TODO: use fd.
    _ = fd
}
```

By convention, global declarations to silence import errors should come right after the imports and be commented, to make them easy to find and as a reminder to clean things up later.

## Import for side effect

Sometimes it is useful to import a package only for its side effects, without any explicit use. For example, the `net/http/pprof` package registers HTTP handlers that provide debugging information during its `init` function. To import the package only for its side effects, rename it to the blank identifier:

```go
import _ "net/http/pprof"
```

This form of import makes clear that the package is being imported for its side effects, because there is no other possible use of the package: in this file, it doesn't have a name.

## Interface checks

A type need not declare explicitly that it implements an interface. Instead, a type implements the interface just by implementing its methods. Most interface conversions are static and checked at compile time. However, some interface checks happen at run-time.

When it is necessary to guarantee within a package that a type actually satisfies an interface, use a global declaration with the blank identifier:

```go
var _ json.Marshaler = (*RawMessage)(nil)
```

In this declaration, the assignment involving a conversion of `*RawMessage` to `Marshaler` requires that `*RawMessage` implements `Marshaler`, and this property will be checked at compile time. Should the `json.Marshaler` interface change, this package will no longer compile and you will be notified that it needs updating.

The appearance of the blank identifier in this construct indicates that the declaration exists only for type checking, not to create a variable. By convention, such declarations are only used when there are no static conversions already present in the code, which is a rare event.
