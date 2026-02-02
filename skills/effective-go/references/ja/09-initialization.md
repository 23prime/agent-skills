# 初期化

表面的にはCやC++の初期化とあまり違いがないように見えるが、Goにおける初期化はより強力である。初期化中に複雑な構造を構築することができ、初期化されるオブジェクト間の順序の問題も、異なるパッケージ間であっても正しく処理される。

## 定数

Goにおける定数はまさにその名の通り、定数である。定数はコンパイル時に作成され、関数内のローカル変数として定義された場合でもそうであり、数値、文字（rune）、文字列、またはブール値のみを使用できる。コンパイル時の制約により、定数を定義する式は定数式でなければならず、コンパイラによって評価可能でなければならない。例えば、`1<<3`は定数式であるが、`math.Sin(math.Pi/4)`は`math.Sin`への関数呼び出しが実行時に行われる必要があるため、定数式ではない。

Goでは、列挙定数は`iota`列挙子を使用して作成される。`iota`は式の一部になることができ、式は暗黙的に繰り返されるため、複雑な値のセットを簡単に構築できる。

```go
type ByteSize float64

const (
    _           = iota // ブランク識別子に代入して最初の値を無視する
    KB ByteSize = 1 << (10 * iota)
    MB
    GB
    TB
    PB
    EB
    ZB
    YB
)
```

ユーザー定義型に`String`のようなメソッドを付加できる機能により、任意の値が印刷時に自動的にフォーマットされるようになる。

```go
func (b ByteSize) String() string {
    switch {
    case b >= YB:
        return fmt.Sprintf("%.2fYB", b/YB)
    case b >= ZB:
        return fmt.Sprintf("%.2fZB", b/ZB)
    case b >= EB:
        return fmt.Sprintf("%.2fEB", b/EB)
    case b >= PB:
        return fmt.Sprintf("%.2fPB", b/PB)
    case b >= TB:
        return fmt.Sprintf("%.2fTB", b/TB)
    case b >= GB:
        return fmt.Sprintf("%.2fGB", b/GB)
    case b >= MB:
        return fmt.Sprintf("%.2fMB", b/MB)
    case b >= KB:
        return fmt.Sprintf("%.2fKB", b/KB)
    }
    return fmt.Sprintf("%.2fB", b)
}
```

ここで`Sprintf`を使用して`ByteSize`の`String`メソッドを実装することが安全である（無限に再帰しない）のは、型変換のためではなく、`%f`を指定して`Sprintf`を呼び出しているためである。`%f`は文字列フォーマットではない。`Sprintf`は文字列が必要な場合にのみ`String`メソッドを呼び出すが、`%f`は浮動小数点値を要求する。

## 変数

変数は定数と同様に初期化できるが、初期化子は実行時に計算される一般的な式にすることができる。

```go
var (
    home   = os.Getenv("HOME")
    user   = os.Getenv("USER")
    gopath = os.Getenv("GOPATH")
)
```

## init関数

最後に、各ソースファイルは、必要な状態をセットアップするために独自の引数なし`init`関数を定義できる（実際には、各ファイルは複数の`init`関数を持つことができる）。そして「最後に」とは文字通り最後を意味する。`init`はパッケージ内のすべての変数宣言がその初期化子を評価した後に呼び出され、それらの初期化子はインポートされたすべてのパッケージが初期化された後にのみ評価される。

宣言として表現できない初期化以外に、`init`関数の一般的な用途は、実際の実行が始まる前にプログラム状態の正しさを検証または修復することである。

```go
func init() {
    if user == "" {
        log.Fatal("$USER not set")
    }
    if home == "" {
        home = "/home/" + user
    }
    if gopath == "" {
        gopath = home + "/go"
    }
    // gopath はコマンドラインの --gopath フラグで上書きできる。
    flag.StringVar(&gopath, "gopath", gopath, "override default GOPATH")
}
```
