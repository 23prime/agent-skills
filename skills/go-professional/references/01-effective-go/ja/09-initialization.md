# Initialization

CやC++の初期化と表面的にはあまり変わらないように見えるが、Goの初期化はより強力である。複雑な構造を初期化中に構築でき、初期化されたオブジェクト間の、さらには異なるパッケージ間の順序の問題が正しく処理される。

## Constants

Goの定数はまさにそのとおり、定数である。それらはコンパイル時に作成され、関数内のローカルとして定義された場合でも同様であり、数値、文字（rune）、文字列、またはブール値のみにできる。コンパイル時の制限のため、それらを定義する式は、コンパイラによって評価可能な定数式でなければならない。例えば、`1<<3`は定数式であるが、`math.Sin(math.Pi/4)`は、`math.Sin`への関数呼び出しが実行時に発生する必要があるため、そうではない。

Goでは、列挙定数は`iota`列挙子を使用して作成される。`iota`は式の一部にでき、式は暗黙的に繰り返されるため、複雑な値のセットを簡単に構築できる。

```go
type ByteSize float64

const (
    _           = iota // blank identifierへの代入で最初の値を無視
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

`String`のようなメソッドを任意のユーザー定義型にアタッチできる機能により、任意の値が出力のために自動的にフォーマットされることが可能になる。

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

ここで`Sprintf`を使用して`ByteSize`の`String`メソッドを実装するのが安全（無限に再帰しない）なのは、変換のためではなく、`%f`で`Sprintf`を呼び出すためである。`%f`は文字列フォーマットではない。`Sprintf`は、文字列が必要なときにのみ`String`メソッドを呼び出し、`%f`は浮動小数点値を必要とする。

## Variables

変数は定数と同じように初期化できるが、初期化子は実行時に計算される一般的な式にできる。

```go
var (
    home   = os.Getenv("HOME")
    user   = os.Getenv("USER")
    gopath = os.Getenv("GOPATH")
)
```

## The init function

最後に、各ソースファイルは、必要な状態を設定するために独自の引数なし`init`関数を定義できる。（実際、各ファイルは複数の`init`関数を持つことができる。）そして最後とは本当に最後を意味する。`init`は、パッケージ内のすべての変数宣言がそれらの初期化子を評価した後に呼び出され、それらは、インポートされたすべてのパッケージが初期化された後にのみ評価される。

宣言として表現できない初期化の他に、`init`関数の一般的な使用法は、実際の実行が始まる前にプログラム状態の正確性を検証または修復することである。

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
    // gopathはコマンドラインの--gopathフラグでオーバーライドできる。
    flag.StringVar(&gopath, "gopath", gopath, "override default GOPATH")
}
```
