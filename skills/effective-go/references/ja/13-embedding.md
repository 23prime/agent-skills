# 埋め込み

Goは典型的な型駆動のサブクラス化の概念を提供していないが、structやinterface内に型を*埋め込む*ことで実装の一部を「借りる」能力を持っている。

## Interfaceの埋め込み

Interfaceの埋め込みは非常にシンプルである。これまでに`io.Reader`と`io.Writer`というinterfaceについて言及してきた。以下がその定義である。

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}
```

`io`パッケージはまた、複数のメソッドを実装できるオブジェクトを指定する他のいくつかのinterfaceもエクスポートしている。例えば、`io.ReadWriter`は`Read`と`Write`の両方を含むinterfaceである。2つのメソッドを明示的にリストアップすることで`io.ReadWriter`を指定することもできるが、次のように2つのinterfaceを埋め込んで新しいinterfaceを形成する方が簡単で表現力が高い。

```go
// ReadWriter は Reader と Writer のインターフェースを組み合わせたインターフェースである。
type ReadWriter interface {
    Reader
    Writer
}
```

これは見た通りのことを示している。`ReadWriter`は`Reader`ができることと`Writer`ができることの*両方*を実行できる。これは埋め込まれたinterfaceの和である。interfaceの中にはinterfaceのみが埋め込める。

## Structの埋め込み

同じ基本的な考え方がstructにも適用されるが、より広範囲に及ぶ影響がある。`bufio`パッケージには2つのstruct型、`bufio.Reader`と`bufio.Writer`があり、それぞれが当然`io`パッケージの対応するinterfaceを実装している。そして`bufio`はバッファ付きreader/writerも実装しており、これは埋め込みを使用してreaderとwriterを1つのstructに結合することで実現している。つまり、struct内で型をリストアップするがフィールド名は与えない。

```go
// ReadWriter は Reader と Writer へのポインタを格納する。
// io.ReadWriter を実装する。
type ReadWriter struct {
    *Reader  // *bufio.Reader
    *Writer  // *bufio.Writer
}
```

埋め込まれた要素はstructへのポインタであり、使用する前に有効なstructを指すように初期化されなければならない。`ReadWriter` structは次のように書くこともできる。

```go
type ReadWriter struct {
    reader *Reader
    writer *Writer
}
```

しかし、その場合、フィールドのメソッドを昇格させ、`io`のinterfaceを満たすために、次のような転送メソッドを提供する必要がある。

```go
func (rw *ReadWriter) Read(p []byte) (n int, err error) {
    return rw.reader.Read(p)
}
```

structを直接埋め込むことで、この手間を回避できる。埋め込まれた型のメソッドは無償で利用できるようになり、これは`bufio.ReadWriter`が`bufio.Reader`と`bufio.Writer`のメソッドを持つだけでなく、3つのinterface(`io.Reader`、`io.Writer`、`io.ReadWriter`)すべてを満たすことを意味する。

埋め込みがサブクラス化と異なる重要な点がある。型を埋め込むとき、その型のメソッドは外側の型のメソッドになるが、それらが呼び出されたとき、メソッドのreceiverは外側の型ではなく内側の型である。

## 名前付きフィールドを伴う埋め込み

埋め込みは単純な利便性としても使える。この例は、通常の名前付きフィールドと並んで埋め込みフィールドを示している。

```go
type Job struct {
    Command string
    *log.Logger
}
```

`Job`型は今や`*log.Logger`の`Print`、`Printf`、`Println`、その他のメソッドを持っている。もちろん`Logger`にフィールド名を与えることもできるが、そうする必要はない。そして今、一度初期化すれば、`Job`にログを記録できる。

```go
job.Println("starting now...")
```

`Logger`は`Job` structの通常のフィールドであるため、次のように`Job`のコンストラクタ内で通常の方法で初期化できる。

```go
func NewJob(command string, logger *log.Logger) *Job {
    return &Job{command, logger}
}
```

または複合リテラルで、

```go
job := &Job{command, log.New(os.Stderr, "Job: ", log.Ldate)}
```

埋め込まれたフィールドを直接参照する必要がある場合、パッケージ修飾子を無視したフィールドの型名がフィールド名として機能する。ここで、`Job`変数`job`の`*log.Logger`にアクセスする必要がある場合、`job.Logger`と書くことになり、これは`Logger`のメソッドを改良したい場合に便利である。

```go
func (job *Job) Printf(format string, args ...interface{}) {
    job.Logger.Printf("%q: %s", job.Command, fmt.Sprintf(format, args...))
}
```

## 埋め込みにおける名前の競合

型の埋め込みは名前の競合という問題をもたらすが、それを解決するルールは単純である。まず、フィールドまたはメソッド`X`は、型のより深くネストされた部分にある他の項目`X`を隠す。`log.Logger`が`Command`というフィールドまたはメソッドを含んでいた場合、`Job`の`Command`フィールドがそれを支配する。

次に、同じ名前が同じネストレベルに現れる場合、それは通常エラーである。`Job` structが`Logger`という別のフィールドまたはメソッドを含んでいた場合、`log.Logger`を埋め込むのはエラーになる。しかし、重複する名前が型定義の外側のプログラムで決して言及されない場合、それは問題ない。この条件は、外部から埋め込まれた型に対する変更に対してある程度の保護を提供する。どちらのフィールドも使用されない場合、別のサブタイプの別のフィールドと競合するフィールドが追加されても問題はない。
