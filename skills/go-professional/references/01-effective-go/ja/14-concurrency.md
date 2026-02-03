# 並行性

## 通信による共有

多くの環境での並行プログラミングは、共有変数への正しいアクセスを実装するために必要な微妙さによって難しくなっている。Goは異なるアプローチを奨励する。共有値はchannelで受け渡され、実際には別々の実行スレッドによって能動的に共有されることはない。任意の時点で1つのgoroutineだけが値にアクセスできる。設計上、データ競合は発生し得ない。この考え方を奨励するために、次のスローガンに集約した。

> メモリを共有して通信するのではなく、通信によってメモリを共有せよ。

このアプローチは行き過ぎることもある。例えば、参照カウントは整数変数の周りにmutexを置くのが最善かもしれない。しかし、高レベルのアプローチとして、アクセス制御にchannelを使用することで、明確で正しいプログラムを書きやすくなる。

このモデルを考える1つの方法は、1つのCPU上で実行される典型的なシングルスレッドプログラムを考えることだ。同期プリミティブは必要ない。次に別のそのようなインスタンスを実行する。これも同期は必要ない。次にそれら2つを通信させる。通信がシンクロナイザーであれば、他の同期は依然として不要である。Unixパイプラインなどは、このモデルに完全に適合する。Goの並行性へのアプローチはHoareのCommunicating Sequential Processes(CSP)に起源があるが、Unixパイプの型安全な汎化と見ることもできる。

## Goroutine

それらは*goroutine*と呼ばれる。既存の用語(スレッド、コルーチン、プロセスなど)は不正確な含意を伝えるためだ。goroutineはシンプルなモデルを持つ。同じアドレス空間で他のgoroutineと同時に実行される関数である。軽量で、スタック空間の割り当て以上のコストはほとんどかからない。そしてスタックは小さく始まるので安価で、必要に応じてヒープストレージを割り当てる(および解放する)ことで成長する。

Goroutineは複数のOSスレッドに多重化されるため、1つがI/Oの待機などでブロックしても、他は実行し続ける。その設計はスレッド作成と管理の複雑さの多くを隠す。

関数やメソッドの呼び出しの前に`go`キーワードを付けると、新しいgoroutineでその呼び出しが実行される。呼び出しが完了すると、goroutineは静かに終了する。

```go
go list.Sort()  // list.Sortを同時実行する。待たない
```

関数リテラルはgoroutineの呼び出しで便利だ。

```go
func Announce(message string, delay time.Duration) {
    go func() {
        time.Sleep(delay)
        fmt.Println(message)
    }()  // 括弧に注意 - 関数を呼び出す必要がある
}
```

Goでは、関数リテラルはクロージャである。実装は、関数が参照する変数がアクティブである限り生き残ることを保証する。

これらの例はあまり実用的ではない。関数が完了を知らせる方法がないためだ。そのためにchannelが必要である。

## Channel

mapと同様に、channelは`make`で割り当てられ、結果の値は基礎となるデータ構造への参照として機能する。オプションの整数パラメータが提供されると、channelのバッファサイズを設定する。デフォルトはゼロで、バッファなしまたは同期channelである。

```go
ci := make(chan int)            // バッファなしのintのchannel
cj := make(chan int, 0)         // バッファなしのintのchannel
cs := make(chan *os.File, 100)  // Fileへのポインタのバッファ付きchannel
```

バッファなしchannelは通信(値の交換)と同期を組み合わせる。つまり、2つの計算(goroutine)が既知の状態にあることを保証する。

Channelを使った素晴らしいイディオムがたくさんある。ここに始めるための1つを示す。channelは起動したgoroutineがソートの完了を待つことを可能にする。

```go
c := make(chan int)  // channelを割り当てる
// goroutineでソートを開始。完了したらchannelでシグナルを送る
go func() {
    list.Sort()
    c <- 1  // シグナルを送る。値は重要でない
}()
doSomethingForAWhile()
<-c   // ソートの完了を待つ。送信された値は破棄
```

受信者は受信するデータがあるまで常にブロックする。channelがバッファなしの場合、送信者は受信者が値を受信するまでブロックする。channelがバッファを持つ場合、送信者は値がバッファにコピーされるまでだけブロックする。バッファが満杯の場合、これはある受信者が値を取り出すまで待つことを意味する。

バッファ付きchannelはセマフォのように使える。例えばスループットを制限するために使用できる。

```go
var sem = make(chan int, MaxOutstanding)

func handle(r *Request) {
    sem <- 1    // アクティブキューが排出されるのを待つ
    process(r)  // 時間がかかるかもしれない
    <-sem       // 完了。次のリクエストの実行を可能にする
}

func Serve(queue chan *Request) {
    for {
        req := <-queue
        go handle(req)  // handleの完了を待たない
    }
}
```

しかし、この設計には問題がある。`Serve`は入ってくるリクエストごとに新しいgoroutineを作成するが、実際には任意の時点で`MaxOutstanding`個しか実行できない。`Serve`を変更してgoroutineの作成をゲートすることで、この欠陥に対処できる。

```go
func Serve(queue chan *Request) {
    for req := range queue {
        sem <- 1
        go func() {
            process(req)
            <-sem
        }()
    }
}
```

リソースをうまく管理する別のアプローチは、固定数の`handle` goroutineを起動し、すべてリクエストchannelから読み取るようにすることである。

```go
func handle(queue chan *Request) {
    for r := range queue {
        process(r)
    }
}

func Serve(clientRequests chan *Request, quit chan bool) {
    // ハンドラを起動
    for i := 0; i < MaxOutstanding; i++ {
        go handle(clientRequests)
    }
    <-quit  // 終了を告げられるまで待つ
}
```

## Channelのchannel

Goの最も重要な特性の1つは、channelがファーストクラスの値であり、他の値と同様に割り当てて受け渡しできることだ。このプロパティの一般的な用途は、安全で並列な逆多重化を実装することである。

その型が返信用のchannelを含む場合、各クライアントは答えのための独自のパスを提供できる。

```go
type Request struct {
    args        []int
    f           func([]int) int
    resultChan  chan int
}
```

クライアントは、関数とその引数、そして答えを受け取るためのchannelをリクエストオブジェクト内に提供する。

```go
func sum(a []int) (s int) {
    for _, v := range a {
        s += v
    }
    return
}

request := &Request{[]int{3, 4, 5}, sum, make(chan int)}
// リクエストを送信
clientRequests <- request
// レスポンスを待つ
fmt.Printf("answer: %d\n", <-request.resultChan)
```

サーバー側では、ハンドラ関数だけが変わる。

```go
func handle(queue chan *Request) {
    for req := range queue {
        req.resultChan <- req.f(req.args)
    }
}
```

## 並列化

これらのアイデアのもう1つの応用は、複数のCPUコアにわたって計算を並列化することである。計算が独立に実行できる別々の部分に分割できる場合、各部分が完了したときにシグナルを送るchannelを使って並列化できる。

```go
type Vector []float64

// v[i]、v[i+1] ... v[n-1]に操作を適用
func (v Vector) DoSome(i, n int, u Vector, c chan int) {
    for ; i < n; i++ {
        v[i] += u.Op(v[i])
    }
    c <- 1    // この部分が完了したことをシグナル
}
```

ループで各部分を独立に起動する。CPUごとに1つ。

```go
const numCPU = 4 // CPUコア数

func (v Vector) DoAll(u Vector) {
    c := make(chan int, numCPU)  // バッファリングはオプションだが賢明
    for i := 0; i < numCPU; i++ {
        go v.DoSome(i*len(v)/numCPU, (i+1)*len(v)/numCPU, u, c)
    }
    // channelを排出
    for i := 0; i < numCPU; i++ {
        <-c    // 1つのタスクの完了を待つ
    }
    // すべて完了
}
```

numCPUの定数値を作成するのではなく、ランタイムに適切な値を尋ねることができる。

```go
var numCPU = runtime.NumCPU()
```

また、Goプログラムが同時に実行できるユーザー指定のコア数を報告(または設定)する関数`runtime.GOMAXPROCS()`もある。

```go
var numCPU = runtime.GOMAXPROCS(0)
```

並行性(独立して実行されるコンポーネントとしてプログラムを構造化すること)と並列性(効率のために複数のCPU上で計算を並列に実行すること)のアイデアを混同しないように注意すること。Goの並行性機能は一部の問題を並列計算として構造化することを容易にできるが、Goは並行言語であり並列言語ではなく、すべての並列化問題がGoのモデルに適合するわけではない。

## リーキーバッファ

並行プログラミングのツールは、非並行のアイデアをより簡単に表現することさえできる。以下はRPCパッケージから抽象化された例である。クライアントgoroutineはソース(おそらくネットワーク)からデータを受信するループを実行する。バッファの割り当てと解放を避けるため、フリーリストを保持し、バッファ付きchannelを使ってそれを表現する。

```go
var freeList = make(chan *Buffer, 100)
var serverChan = make(chan *Buffer)

func client() {
    for {
        var b *Buffer
        // 利用可能ならバッファを取得。なければ割り当てる
        select {
        case b = <-freeList:
            // 取得。他に何もしない
        default:
            // 空なので新しいものを割り当てる
            b = new(Buffer)
        }
        load(b)              // ネットワークから次のメッセージを読む
        serverChan <- b      // サーバーに送る
    }
}
```

サーバーループはクライアントから各メッセージを受信し、処理し、バッファをフリーリストに返す。

```go
func server() {
    for {
        b := <-serverChan    // 作業を待つ
        process(b)
        // スペースがあればバッファを再利用
        select {
        case freeList <- b:
            // バッファはフリーリストに。他に何もしない
        default:
            // フリーリストが満杯。そのまま続ける
        }
    }
}
```

クライアントは`freeList`からバッファを取得しようとする。利用できなければ、新しいものを割り当てる。サーバーの`freeList`への送信は、リストが満杯でなければ`b`をフリーリストに戻す。リストが満杯の場合、バッファは床に落とされ、ガベージコレクタによって回収される。(`select`文の`default`句は他のcaseが準備できていないときに実行される。つまり、`select`は決してブロックしない)この実装は、バッファ付きchannelとガベージコレクタに頼って帳簿管理を行い、わずか数行でリーキーバケットフリーリストを構築する。
