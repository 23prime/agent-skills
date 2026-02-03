# 埋め込み

Goは典型的な型駆動のサブクラス化の概念を提供していないが、structやインターフェース内に型を*埋め込む*ことで実装の一部を「借りる」能力を持っている。

## インターフェースの埋め込み

インターフェースの埋め込みは非常にシンプルだ。以前`io.Reader`と`io.Writer`インターフェースに言及したが、これらの定義は次のとおりである。

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}
```

`io`パッケージは、複数のそのようなメソッドを実装できるオブジェクトを指定する他のインターフェースもエクスポートしている。例えば、`Read`と`Write`の両方を含むインターフェースである`io.ReadWriter`がある。2つのメソッドを明示的にリストアップして`io.ReadWriter`を指定することもできるが、次のように2つのインターフェースを埋め込んで新しいものを形成する方が簡単で示唆的である。

```go
// ReadWriterはReaderとWriterインターフェースを組み合わせたインターフェースである
type ReadWriter interface {
    Reader
    Writer
}
```

これは見た目のとおりである。`ReadWriter`は`Reader`ができることと`Writer`ができることの*両方*ができる。これは埋め込まれたインターフェースの和集合である。インターフェース内に埋め込めるのはインターフェースだけだ。

## structの埋め込み

同じ基本的な考え方がstructにも適用されるが、より広範囲な影響がある。`bufio`パッケージには2つのstruct型、`bufio.Reader`と`bufio.Writer`があり、もちろんそれぞれが`io`パッケージの対応するインターフェースを実装している。そして`bufio`はバッファ付きreader/writerも実装している。これは、埋め込みを使ってreaderとwriterを1つのstructに組み合わせることで実現している。つまり、structの中に型をリストするが、フィールド名を付けない。

```go
// ReadWriterはReaderとWriterへのポインタを格納する
// これはio.ReadWriterを実装する
type ReadWriter struct {
    *Reader  // *bufio.Reader
    *Writer  // *bufio.Writer
}
```

埋め込まれた要素はstructへのポインタであり、使用前に有効なstructを指すように初期化しなければならない。`ReadWriter` structは次のように書くこともできる。

```go
type ReadWriter struct {
    reader *Reader
    writer *Writer
}
```

しかし、そうするとフィールドのメソッドを昇格させ、`io`インターフェースを満たすために、次のような転送メソッドも提供する必要がある。

```go
func (rw *ReadWriter) Read(p []byte) (n int, err error) {
    return rw.reader.Read(p)
}
```

structを直接埋め込むことで、この事務処理を回避できる。埋め込まれた型のメソッドは自動的に付いてくるため、`bufio.ReadWriter`は`bufio.Reader`と`bufio.Writer`のメソッドを持つだけでなく、3つのインターフェース`io.Reader`、`io.Writer`、`io.ReadWriter`も満たす。

埋め込みがサブクラス化と異なる重要な点がある。型を埋め込むと、その型のメソッドは外側の型のメソッドになるが、それらが呼び出されたとき、メソッドのレシーバは外側の型ではなく、内側の型になる。

## 名前付きフィールドを伴う埋め込み

埋め込みは単純な便利さでもある。次の例は、通常の名前付きフィールドと並んで埋め込みフィールドを示している。

```go
type Job struct {
    Command string
    *log.Logger
}
```

`Job`型は現在、`*log.Logger`の`Print`、`Printf`、`Println`、その他のメソッドを持っている。もちろん`Logger`にフィールド名を付けることもできるが、その必要はない。そして今、初期化すれば、`Job`にログを記録できる。

```go
job.Println("starting now...")
```

`Logger`は`Job` structの通常のフィールドなので、次のように`Job`のコンストラクタ内で通常の方法で初期化できる。

```go
func NewJob(command string, logger *log.Logger) *Job {
    return &Job{command, logger}
}
```

または複合リテラルで。

```go
job := &Job{command, log.New(os.Stderr, "Job: ", log.Ldate)}
```

埋め込みフィールドを直接参照する必要がある場合、パッケージ修飾子を無視したフィールドの型名がフィールド名として機能する。`Job`変数`job`の`*log.Logger`にアクセスする必要がある場合、`job.Logger`と書く。これは`Logger`のメソッドを改良したい場合に便利だ。

```go
func (job *Job) Printf(format string, args ...interface{}) {
    job.Logger.Printf("%q: %s", job.Command, fmt.Sprintf(format, args...))
}
```

## 埋め込みにおける名前の競合

型の埋め込みは名前の競合の問題を引き起こすが、それを解決するルールはシンプルだ。まず、フィールドまたはメソッド`X`は、型のより深くネストされた部分にある他の項目`X`を隠す。`log.Logger`が`Command`というフィールドまたはメソッドを含んでいた場合、`Job`の`Command`フィールドがそれを支配する。

次に、同じ名前が同じネストレベルに現れる場合、通常はエラーである。`Job` structが`Logger`という別のフィールドまたはメソッドを含んでいた場合、`log.Logger`を埋め込むのは誤りとなる。しかし、重複した名前が型定義の外側のプログラムで決して言及されない場合は問題ない。この制限は、外部から埋め込まれた型に対する変更に対してある程度の保護を提供する。どちらのフィールドも使用されていなければ、別のサブタイプの別のフィールドと競合するフィールドが追加されても問題ない。
