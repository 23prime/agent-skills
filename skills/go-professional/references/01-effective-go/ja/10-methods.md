# Methods

## Pointers vs. Values

`ByteSize`で見たように、メソッドは任意の名前付き型（pointerまたはinterfaceを除く）に対して定義できる。レシーバはstructである必要はない。

上記のsliceの議論で、`Append`関数を書いた。これを代わりにslice上のメソッドとして定義できる。これを行うには、まずメソッドをバインドできる名前付き型を宣言し、次にメソッドのレシーバをその型の値にする。

```go
type ByteSlice []byte

func (slice ByteSlice) Append(data []byte) []byte {
    // 本体は上で定義したAppend関数と全く同じ。
}
```

これでも、メソッドは更新されたsliceを返す必要がある。メソッドが呼び出し元のsliceを上書きできるように、`ByteSlice`へのpointerをレシーバとして受け取るようにメソッドを再定義することで、この不格好さを排除できる。

```go
func (p *ByteSlice) Append(data []byte) {
    slice := *p
    // 上と同じ本体、ただしreturnなし。
    *p = slice
}
```

実際、さらに改善できる。関数を標準の`Write`メソッドのように見えるように修正すると、次のようになる。

```go
func (p *ByteSlice) Write(data []byte) (n int, err error) {
    slice := *p
    // 再び上と同じ。
    *p = slice
    return len(data), nil
}
```

すると、型`*ByteSlice`は標準interface `io.Writer`を満たし、これは便利である。例えば、これに出力できる。

```go
var b ByteSlice
fmt.Fprintf(&b, "This hour has %d days\n", 7)
```

`*ByteSlice`だけが`io.Writer`を満たすため、`ByteSlice`のアドレスを渡す。レシーバに関するpointerと値のルールは、値メソッドはpointerと値で呼び出せるが、pointerメソッドはpointerでのみ呼び出せるというものである。

このルールが生じるのは、pointerメソッドがレシーバを変更できるためである。値で呼び出すと、メソッドは値のコピーを受け取るため、変更はすべて破棄される。したがって、言語はこの間違いを禁止する。ただし、便利な例外がある。値がアドレス可能である場合、言語は、値でpointerメソッドを呼び出す一般的なケースに対処するために、自動的にアドレス演算子を挿入する。この例では、変数`b`はアドレス可能であるため、単に`b.Write`でその`Write`メソッドを呼び出すことができる。コンパイラはこれを`(&b).Write`に書き換える。

ちなみに、byteのsliceで`Write`を使用するというアイデアは、`bytes.Buffer`の実装の中心である。
