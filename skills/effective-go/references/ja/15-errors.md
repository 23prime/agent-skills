# Errors

ライブラリルーチンは、呼び出し側に何らかのエラー表示を返さなければならないことが多い。前述のとおり、Goの多値返却により、通常の返り値と並んで詳細なエラー説明を返すことが容易である。この機能を使用して詳細なエラー情報を提供するのは良いスタイルである。例えば、これから見るように、`os.Open`は失敗時に`nil`ポインタを返すだけでなく、何が問題だったかを説明するエラー値も返す。

慣例により、エラーは`error`型を持つ。これは単純な組み込みインターフェースである。

```go
type error interface {
    Error() string
}
```

ライブラリの作者は、このインターフェースをより豊かなモデルで自由に実装できる。これにより、エラーを見るだけでなく、いくらかのコンテキストを提供することも可能になる。前述のとおり、通常の`*os.File`返り値と並んで、`os.Open`はエラー値も返す。ファイルが正常に開かれた場合、エラーは`nil`であるが、問題がある場合は`os.PathError`を保持する。

```go
// PathError は操作、ファイルパス、および原因となったエラーを記録する。
type PathError struct {
    Op string    // "open", "unlink" など。
    Path string  // 関連するファイル。
    Err error    // システムコールが返したエラー。
}

func (e *PathError) Error() string {
    return e.Op + " " + e.Path + ": " + e.Err.Error()
}
```

`PathError`の`Error`は次のような文字列を生成する。

```text
open /etc/passwx: no such file or directory
```

このようなエラーは、問題のあるファイル名、操作、およびそれが引き起こしたオペレーティングシステムのエラーを含んでおり、それを引き起こした呼び出しから遠く離れた場所で出力されても有用である。単なる"no such file or directory"よりもはるかに有益である。

可能であれば、エラー文字列は、エラーを生成した操作またはパッケージの名前を付ける接頭辞を持つことで、その起源を識別すべきである。例えば、パッケージ`image`では、未知の形式によるデコードエラーの文字列表現は"image: unknown format"である。

正確なエラーの詳細を気にする呼び出し側は、type switchまたはtype assertionを使用して、特定のエラーを探し、詳細を抽出できる。

```go
for try := 0; try < 2; try++ {
    file, err = os.Create(filename)
    if err == nil {
        return
    }
    if e, ok := err.(*os.PathError); ok && e.Err == syscall.ENOSPC {
        deleteTempFiles()  // 空き容量を回復する。
        continue
    }
    return
}
```

## Panic

呼び出し側にエラーを報告する通常の方法は、追加の返り値として`error`を返すことである。標準的な`Read`メソッドはよく知られた例である。これはバイト数と`error`を返す。しかし、エラーが回復不可能な場合はどうするか。プログラムが単に続行できない場合もある。

この目的のために、プログラムを停止させる実行時エラーを実質的に作成する組み込み関数`panic`がある(ただし、次のセクションを参照)。この関数は、任意の型の単一引数を取る。多くの場合、文字列であり、プログラムが終了する際に出力される。また、無限ループから抜け出すなど、起こりえないことが起こったことを示す方法でもある。

```go
// ニュートン法による立方根の簡易実装。
func CubeRoot(x float64) float64 {
    z := x/3   // 任意の初期値
    for i := 0; i < 1e6; i++ {
        prevz := z
        z -= (z*z*z-x) / (3*z*z)
        if veryClose(z, prevz) {
            return z
        }
    }
    // 100万回の反復で収束しなかった。何かがおかしい。
    panic(fmt.Sprintf("CubeRoot(%g) did not converge", x))
}
```

これは単なる例であるが、実際のライブラリ関数は`panic`を避けるべきである。問題を隠したり回避したりできる場合は、プログラム全体を停止させるよりも、常に処理を続行させる方が良い。考えられる反例の1つは初期化時である。ライブラリが本当に自身をセットアップできない場合は、いわば、panicするのが妥当かもしれない。

```go
var user = os.Getenv("USER")

func init() {
    if user == "" {
        panic("no value for $USER")
    }
}
```

## Recover

`panic`が呼び出されると、スライスの範囲外へのインデックスアクセスやtype assertionの失敗などの実行時エラーに対して暗黙的に呼び出される場合も含めて、現在の関数の実行を直ちに停止し、goroutineのスタックの巻き戻しを開始し、途中でdeferされた関数を実行する。その巻き戻しがgoroutineのスタックの最上部に達すると、プログラムは終了する。しかし、組み込み関数`recover`を使用して、goroutineの制御を取り戻し、通常の実行を再開することができる。

`recover`の呼び出しは巻き戻しを停止し、`panic`に渡された引数を返す。巻き戻し中に実行される唯一のコードはdeferred関数の内部にあるため、`recover`はdeferred関数の内部でのみ有用である。

`recover`の1つの応用は、サーバー内で失敗したgoroutineを、他の実行中のgoroutineを停止させることなくシャットダウンすることである。

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

この例では、`do(work)`がpanicした場合、その結果がログに記録され、goroutineは他のgoroutineを妨げることなくクリーンに終了する。deferされたクロージャ内で他に何かをする必要はない。`recover`を呼び出すだけで状態を完全に処理できる。

`recover`はdeferred関数から直接呼び出されない限り常に`nil`を返すため、deferされたコードは、それ自体が`panic`と`recover`を使用するライブラリルーチンを失敗することなく呼び出すことができる。例として、`safelyDo`内のdeferred関数は、`recover`を呼び出す前にロギング関数を呼び出すかもしれない。そのロギングコードは、panicしている状態の影響を受けずに実行される。
