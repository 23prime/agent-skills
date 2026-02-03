# エラー

ライブラリルーチンは、呼び出し元に何らかのエラー表示を返す必要があることが多い。前述のように、Goの多値返却により、通常の戻り値と一緒に詳細なエラー説明を返すことが容易になる。この機能を使って詳細なエラー情報を提供するのは良いスタイルである。例えば、これから見るように、`os.Open`は失敗時に単に`nil`ポインタを返すのではなく、何が間違ったかを説明するエラー値も返す。

慣例として、エラーは`error`型を持つ。これはシンプルな組み込みインターフェースである。

```go
type error interface {
    Error() string
}
```

ライブラリライターは、内部でこのインターフェースをより豊かなモデルで自由に実装でき、エラーを見るだけでなくコンテキストも提供できる。前述のように、通常の`*os.File`戻り値と一緒に、`os.Open`はエラー値も返す。ファイルが正常に開かれた場合、エラーは`nil`だが、問題がある場合は`os.PathError`を保持する。

```go
// PathErrorはエラーと、それを引き起こした操作と
// ファイルパスを記録する
type PathError struct {
    Op string    // "open"、"unlink"など
    Path string  // 関連するファイル
    Err error    // システムコールが返したもの
}

func (e *PathError) Error() string {
    return e.Op + " " + e.Path + ": " + e.Err.Error()
}
```

`PathError`の`Error`は次のような文字列を生成する。

```text
open /etc/passwx: no such file or directory
```

このようなエラーは、問題のあるファイル名、操作、引き起こされたオペレーティングシステムのエラーを含んでおり、それを引き起こした呼び出しから遠く離れて出力されても有用である。単なる「no such file or directory」よりもはるかに情報量が多い。

可能であれば、エラー文字列はその起源を識別すべきである。例えば、エラーを生成した操作やパッケージを命名するプレフィックスを持つことなどである。例えば、`image`パッケージでは、未知のフォーマットによるデコードエラーの文字列表現は「image: unknown format」である。

正確なエラーの詳細を気にする呼び出し元は、型switchまたは型アサーションを使って特定のエラーを探し、詳細を抽出できる。

```go
for try := 0; try < 2; try++ {
    file, err = os.Create(filename)
    if err == nil {
        return
    }
    if e, ok := err.(*os.PathError); ok && e.Err == syscall.ENOSPC {
        deleteTempFiles()  // スペースを回復
        continue
    }
    return
}
```

## Panic

呼び出し元にエラーを報告する通常の方法は、追加の戻り値として`error`を返すことである。標準的な`Read`メソッドはよく知られた例だ。バイト数と`error`を返す。しかし、エラーが回復不可能な場合はどうだろうか? プログラムが単に続行できない場合もある。

この目的のために、組み込み関数`panic`がある。これは実質的にプログラムを停止する実行時エラーを作成する(ただし次のセクションを参照)。この関数は任意の型の単一の引数(多くの場合は文字列)を取り、プログラムが終了する際に出力される。また、無限ループを抜けるなど、不可能なことが起こったことを示す方法でもある。

```go
// Newtonの方法を使った立方根の玩具実装
func CubeRoot(x float64) float64 {
    z := x/3   // 任意の初期値
    for i := 0; i < 1e6; i++ {
        prevz := z
        z -= (z*z*z-x) / (3*z*z)
        if veryClose(z, prevz) {
            return z
        }
    }
    // 100万回の反復が収束しなかった。何かが間違っている
    panic(fmt.Sprintf("CubeRoot(%g) did not converge", x))
}
```

これは例に過ぎないが、実際のライブラリ関数は`panic`を避けるべきだ。問題をマスクまたは回避できる場合、プログラム全体を停止するよりも、常に実行を継続させる方が良い。可能性のある反例は初期化時である。ライブラリが本当に自身を設定できない場合、いわばpanicするのは合理的かもしれない。

```go
var user = os.Getenv("USER")

func init() {
    if user == "" {
        panic("no value for $USER")
    }
}
```

## Recover

`panic`が呼び出されると、範囲外のsliceのインデックスアクセスや型アサーションの失敗などの実行時エラーによって暗黙的に呼び出される場合も含めて、現在の関数の実行を即座に停止し、goroutineのスタックを巻き戻し始め、その過程で遅延関数を実行する。その巻き戻しがgoroutineのスタックのトップに達すると、プログラムは終了する。しかし、組み込み関数`recover`を使ってgoroutineの制御を取り戻し、通常の実行を再開することが可能である。

`recover`の呼び出しは巻き戻しを停止し、`panic`に渡された引数を返す。巻き戻し中に実行されるコードは遅延関数の内部だけなので、`recover`は遅延関数の内部でのみ有用である。

`recover`の1つの応用は、サーバー内で失敗したgoroutineを、他の実行中のgoroutineを殺すことなくシャットダウンすることである。

```go
func server(workChan <-chan *Work) {
    for work := range workChan {
        go safelyDo(work)
    }
}

func safelyDo(work *Work) {
    defer func() {
        if err := recover(); err != nil {
            log.Println("work failed:", err)
        }
    }()
    do(work)
}
```

この例では、`do(work)`がpanicすると、結果はログに記録され、goroutineは他を妨げることなくクリーンに終了する。遅延クロージャで他に何かをする必要はない。`recover`を呼び出すだけで状態を完全に処理する。

`recover`は遅延関数から直接呼び出されない限り常に`nil`を返すため、遅延コードは`panic`と`recover`を自身で使うライブラリルーチンを失敗せずに呼び出せる。例として、`safelyDo`の遅延関数は`recover`を呼び出す前にロギング関数を呼び出すかもしれず、そのロギングコードはpanicしている状態に影響されずに実行される。
