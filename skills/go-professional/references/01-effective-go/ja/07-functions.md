# Functions

## Multiple return values

Goの特徴的な機能の1つは、関数とメソッドが複数の値を返せることである。この形式は、Cプログラムにおけるいくつかの不格好な慣用句、例えば`EOF`のための`-1`のようなインバンドエラー戻り値や、アドレスで渡された引数の変更などを改善するために使用できる。

Cでは、書き込みエラーは負のカウントで通知され、エラーコードは揮発性の場所に隠される。Goでは、`Write`はカウントとエラーの両方を返すことができる。「はい、いくつかのバイトを書きましたが、デバイスがいっぱいになったため、すべてではありません」。パッケージ`os`のファイルに対する`Write`メソッドのシグネチャは次のとおりである。

```go
func (file *File) Write(b []byte) (n int, err error)
```

ドキュメントが述べているように、これは書き込まれたバイト数と、`n != len(b)`のときに非nilの`error`を返す。これは一般的なスタイルである。詳細な例についてはエラー処理のセクションを参照。

同様のアプローチにより、参照パラメータをシミュレートするために戻り値へのポインタを渡す必要がなくなる。以下は、byte slice内の位置から数値を取得し、数値と次の位置を返す単純な関数である。

```go
func nextInt(b []byte, i int) (int, int) {
    for ; i < len(b) && !isDigit(b[i]); i++ {
    }
    x := 0
    for ; i < len(b) && isDigit(b[i]); i++ {
        x = x*10 + int(b[i]) - '0'
    }
    return x, i
}
```

これを使用して、入力slice `b`内の数値をスキャンできる。

```go
for i := 0; i < len(b); {
    x, i = nextInt(b, i)
    fmt.Println(x)
}
```

## Named result parameters

Goの関数の戻り値または結果「パラメータ」には名前を付けることができ、入力パラメータと同様に通常の変数として使用できる。名前が付けられると、関数が開始されるときに型のゼロ値で初期化される。関数が引数なしの`return`文を実行すると、結果パラメータの現在の値が戻り値として使用される。

名前は必須ではないが、コードを短く明確にすることができる。つまり、それらはドキュメントである。`nextInt`の結果に名前を付けると、どちらの戻り値の`int`がどちらであるかが明白になる。

```go
func nextInt(b []byte, pos int) (value, nextPos int)
```

名前付き結果は初期化され、装飾のないreturnに結び付けられているため、簡略化と明確化の両方が可能である。以下は、それらをうまく使用した`io.ReadFull`のバージョンである。

```go
func ReadFull(r Reader, buf []byte) (n int, err error) {
    for len(buf) > 0 && err == nil {
        var nr int
        nr, err = r.Read(buf)
        n += nr
        buf = buf[nr:]
    }
    return
}
```

## Defer

Goの`defer`文は、`defer`を実行している関数が返る直前に実行される関数呼び出し（遅延関数）をスケジュールする。これは珍しいが効果的な方法で、関数がどのパスで返るかに関係なく解放しなければならないリソースなどの状況に対処する。典型的な例は、mutexのロック解除やファイルのクローズである。

```go
// Contentsはファイルの内容を文字列として返す。
func Contents(filename string) (string, error) {
    f, err := os.Open(filename)
    if err != nil {
        return "", err
    }
    defer f.Close()  // f.Closeは終了時に実行される。

    var result []byte
    buf := make([]byte, 100)
    for {
        n, err := f.Read(buf[0:])
        result = append(result, buf[0:n]...) // appendは後で説明する。
        if err != nil {
            if err == io.EOF {
                break
            }
            return "", err  // ここで返る場合、fはクローズされる。
        }
    }
    return string(result), nil // ここで返る場合、fはクローズされる。
}
```

`Close`のような関数への呼び出しを遅延させることには2つの利点がある。第一に、ファイルをクローズし忘れることがないことを保証する。これは、後で関数を編集して新しいreturnパスを追加する場合に犯しやすいミスである。第二に、クローズがオープンの近くにあることを意味し、関数の最後に配置するよりもはるかに明確である。

遅延関数への引数（関数がメソッドの場合はレシーバを含む）は、呼び出しが実行されるときではなく、deferが実行されるときに評価される。関数の実行中に変数が値を変更することについての心配を避けることに加えて、これは単一の遅延呼び出しサイトが複数の関数実行を遅延できることを意味する。以下は馬鹿げた例である。

```go
for i := 0; i < 5; i++ {
    defer fmt.Printf("%d ", i)
}
```

遅延関数はLIFO順で実行されるため、このコードは関数が返るときに`4 3 2 1 0`が出力される。より妥当な例は、プログラムを通じて関数の実行をトレースする簡単な方法である。次のような単純なトレースルーチンを書くことができる。

```go
func trace(s string)   { fmt.Println("entering:", s) }
func untrace(s string) { fmt.Println("leaving:", s) }

// 次のように使用する:
func a() {
    trace("a")
    defer untrace("a")
    // 何かをする....
}
```

遅延関数への引数が`defer`が実行されるときに評価されるという事実を利用することで、さらに改善できる。この例を見てみよう。

```go
func trace(s string) string {
    fmt.Println("entering:", s)
    return s
}

func un(s string) {
    fmt.Println("leaving:", s)
}

func a() {
    defer un(trace("a"))
    fmt.Println("in a")
}

func b() {
    defer un(trace("b"))
    fmt.Println("in b")
    a()
}

func main() {
    b()
}
```

これは次を出力する。

```text
entering: b
in b
entering: a
in a
leaving: a
leaving: b
```

他の言語のブロックレベルのリソース管理に慣れているプログラマにとって、`defer`は奇妙に見えるかもしれないが、その最も興味深く強力なアプリケーションは、ブロックベースではなく関数ベースであるという事実から正確に生まれる。`panic`と`recover`のセクションで、その可能性の別の例を見る。
