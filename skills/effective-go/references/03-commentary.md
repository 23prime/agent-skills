# Commentary

Go provides C-style `/* */` block comments and C++-style `//` line comments. Line comments are the norm; block comments appear mostly as package comments, but are useful within an expression or to disable large swaths of code.

Comments that appear before top-level declarations, with no intervening newlines, are considered to document the declaration itself. These "doc comments" are the primary documentation for a given Go package or command. For more about doc comments, see "[Go Doc Comments](https://go.dev/doc/comment)".
