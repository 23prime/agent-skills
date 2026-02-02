# Functions

## Multiple return values

Goの特異な機能の1つは、関数とメソッドが複数の値を返すことができることである。この形式は、Cプログラムにおけるいくつかの不格好なイディオムを改善するために使用できる。例えば、`EOF`を示す`-1`のようなインバンドエラーリターンや、アドレスで渡された引数を変更するなどである。

Cでは、書き込みエラーは負の数でシグナルされ、エラーコードは揮発性の場所に隠される。Goでは、`Write`は書き込んだバイト数*と*エラーを返すことができる。「あなたはいくつかのバイトを書き込んだが、デバイスがいっぱいになったため全部ではない」ということである。パッケージ`os`のファイルに対する`Write`メソッドのシグネチャは次の通りである。

```go
func (file *File) Write(b []byte) (n int, err error)
```

ドキュメントに記載されているように、`n != len(b)`のとき、書き込まれたバイト数と非nilの`error`を返す。これは一般的なスタイルである。より多くの例についてはエラーハンドリングのセクションを参照されたい。

同様のアプローチにより、参照パラメータをシミュレートするために戻り値へのポインタを渡す必要がなくなる。以下は、バイトスライス内の位置から数値を取得し、その数値と次の位置を返す単純な関数である。

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

これを使って、入力スライス`b`内の数値をスキャンするには次のようにする。

```go
for i := 0; i < len(b); {
    x, i = nextInt(b, i)
    fmt.Println(x)
}
```

## Named result parameters

Go関数の戻り値または結果「パラメータ」には名前を付けることができ、入力パラメータと同様に通常の変数として使用できる。名前を付けると、関数の開始時にその型のゼロ値に初期化される。関数が引数なしの`return`文を実行すると、結果パラメータの現在の値が戻り値として使用される。

名前は必須ではないが、コードをより短く明確にすることができる。つまり、ドキュメントとなる。`nextInt`の結果に名前を付けると、どの`int`がどれであるかが明白になる。

```go
func nextInt(b []byte, pos int) (value, nextPos int)
```

名前付き結果は初期化され、引数なしのreturnと結びついているため、簡潔化と明確化の両方が可能になる。以下は、これらをうまく使用した`io.ReadFull`のバージョンである。

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

Goの`defer`文は、関数呼び出し(*deferred*関数)を、`defer`を実行している関数が返る直前に実行されるようスケジュールする。これは異例だが効果的な方法であり、関数がどのパスを通って返るかに関係なく解放しなければならないリソースなどの状況に対処できる。典型的な例は、mutexのアンロックやファイルのクローズである。

```go
// Contentsはファイルの内容を文字列として返す。
func Contents(filename string) (string, error) {
    f, err := os.Open(filename)
    if err != nil {
        return "", err
    }
    defer f.Close()  // 終了時にf.Closeが実行される。

    var result []byte
    buf := make([]byte, 100)
    for {
        n, err := f.Read(buf[0:])
        result = append(result, buf[0:n]...) // appendについては後述する。
        if err != nil {
            if err == io.EOF {
                break
            }
            return "", err  // ここでreturnしてもfはクローズされる。
        }
    }
    return string(result), nil // ここでreturnしてもfはクローズされる。
}
```

`Close`のような関数の呼び出しを遅延させることには2つの利点がある。第一に、ファイルのクローズを忘れないことが保証される。後で関数を編集して新しいreturnパスを追加する場合に犯しやすいミスである。第二に、closeがopenの近くに配置されることを意味し、関数の最後に配置するよりもはるかに明確である。

遅延関数への引数(関数がメソッドの場合はレシーバを含む)は、*呼び出し*が実行される時ではなく、*defer*が実行される時に評価される。関数の実行中に変数の値が変わることを心配する必要がないだけでなく、これは単一の遅延呼び出しサイトが複数の関数実行を遅延できることを意味する。以下は馬鹿げた例である。

```go
for i := 0; i < 5; i++ {
    defer fmt.Printf("%d ", i)
}
```

遅延関数はLIFO順で実行されるため、このコードは関数が返る時に`4 3 2 1 0`が出力される。より妥当な例は、プログラムを通して関数実行をトレースする簡単な方法である。次のような簡単なトレースルーチンを書くことができる。

```go
func trace(s string)   { fmt.Println("entering:", s) }
func untrace(s string) { fmt.Println("leaving:", s) }

// 次のように使用する:
func a() {
    trace("a")
    defer untrace("a")
    // 何らかの処理....
}
```

遅延関数への引数が`defer`実行時に評価されるという事実を利用することで、より良くできる。この例は次の通りである。

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

他の言語のブロックレベルのリソース管理に慣れたプログラマには、`defer`は奇妙に見えるかもしれないが、その最も興味深く強力なアプリケーションは、まさにそれがブロックベースではなく関数ベースであるという事実から生まれる。`panic`と`recover`のセクションでは、その可能性の別の例を見る。
