# インターフェースとその他の型

## インターフェース

Goのインターフェースは、オブジェクトの振る舞いを指定する方法を提供する。つまり、何かが*これ*を行えるなら、*ここ*で使えるということだ。すでにいくつかの簡単な例を見てきた。カスタムプリンタは`String`メソッドで実装でき、`Fprintf`は`Write`メソッドを持つものに対して出力を生成できる。Goのコードでは1つか2つのメソッドしか持たないインターフェースが一般的で、通常はそのメソッドから派生した名前が付けられる。例えば`io.Writer`は`Write`を実装するものを表す。

1つの型は複数のインターフェースを実装できる。例えば、あるコレクションが`sort.Interface`を実装していれば`sort`パッケージのルーチンでソート可能になる。`sort.Interface`は`Len()`、`Less(i, j int) bool`、`Swap(i, j int)`を含む。また、カスタムフォーマッタを持つこともできる。次の作為的な例では、`Sequence`が両方を満たしている。

```go
type Sequence []int

// sort.Interfaceが要求するメソッド
func (s Sequence) Len() int {
    return len(s)
}
func (s Sequence) Less(i, j int) bool {
    return s[i] < s[j]
}
func (s Sequence) Swap(i, j int) {
    s[i], s[j] = s[j], s[i]
}

// Copyはシーケンスのコピーを返す
func (s Sequence) Copy() Sequence {
    copy := make(Sequence, 0, len(s))
    return append(copy, s...)
}

// 出力用メソッド - 要素をソートしてから出力する
func (s Sequence) String() string {
    s = s.Copy() // コピーを作る。引数を上書きしない
    sort.Sort(s)
    str := "["
    for i, elem := range s { // ループはO(N²)。次の例で修正する
        if i > 0 {
            str += " "
        }
        str += fmt.Sprint(elem)
    }
    return str + "]"
}
```

## 変換

`Sequence`の`String`メソッドは、`Sprint`がsliceに対してすでに行っている処理を再現している。`Sprint`を呼び出す前に`Sequence`を普通の`[]int`に変換すれば、作業を共有できる(また高速化もできる)。

```go
func (s Sequence) String() string {
    s = s.Copy()
    sort.Sort(s)
    return fmt.Sprint([]int(s))
}
```

このメソッドは、`String`メソッドから`Sprintf`を安全に呼び出すための変換テクニックのもう1つの例である。2つの型(`Sequence`と`[]int`)は型名を無視すれば同じなので、それらの間で変換することは合法だ。変換は新しい値を作らず、単に既存の値が一時的に新しい型を持つかのように振る舞うだけだ。

Goプログラムでは、異なるメソッドセットにアクセスするために式の型を変換するのが慣用句である。例として、既存の型`sort.IntSlice`を使えば、全体の例を次のように減らせる。

```go
type Sequence []int

// 出力用メソッド - 要素をソートしてから出力する
func (s Sequence) String() string {
    s = s.Copy()
    sort.IntSlice(s).Sort()
    return fmt.Sprint([]int(s))
}
```

## インターフェース変換と型アサーション

型switchは変換の一形態である。つまり、インターフェースを受け取り、switchの各caseに対して、ある意味でそのcaseの型に変換する。以下は`fmt.Printf`の内部で型switchを使って値を文字列に変換する方法の簡略版である。

```go
type Stringer interface {
    String() string
}

var value interface{} // 呼び出し元が提供する値
switch str := value.(type) {
case string:
    return str
case Stringer:
    return str.String()
}
```

関心のある型が1つだけの場合はどうだろうか? 1つのcaseだけの型switchでも可能だが、*型アサーション*も使える。型アサーションはインターフェース値を受け取り、指定された明示的な型の値を抽出する。

```go
value.(typeName)
```

panicを防ぐには、「comma, ok」イディオムを使って安全にテストする。

```go
str, ok := value.(string)
if ok {
    fmt.Printf("string value is: %q\n", str)
} else {
    fmt.Printf("value is not a string\n")
}
```

型アサーションが失敗した場合でも、`str`は存在してstring型になるが、ゼロ値の空文字列となる。

## 汎用性

ある型がインターフェースを実装するためだけに存在し、そのインターフェースを超えてエクスポートされたメソッドを持たない場合、その型自体をエクスポートする必要はない。インターフェースだけをエクスポートすれば、その値がインターフェースに記述されたもの以外に興味深い振る舞いを持たないことが明確になる。また、共通メソッドの各インスタンスでドキュメントを繰り返す必要もなくなる。

このような場合、コンストラクタは実装型ではなくインターフェース値を返すべきである。例えば、ハッシュライブラリでは`crc32.NewIEEE`と`adler32.New`の両方がインターフェース型`hash.Hash32`を返す。GoプログラムでCRC-32アルゴリズムをAdler-32に置き換えるには、コンストラクタの呼び出しを変更するだけでよい。残りのコードはアルゴリズムの変更による影響を受けない。

同様のアプローチにより、様々な`crypto`パッケージのストリーム暗号アルゴリズムを、それらが連鎖するブロック暗号から分離できる。

```go
type Block interface {
    BlockSize() int
    Encrypt(dst, src []byte)
    Decrypt(dst, src []byte)
}

type Stream interface {
    XORKeyStream(dst, src []byte)
}
```

`NewCTR`は、特定の暗号化アルゴリズムとデータソースだけでなく、`Block`インターフェースと任意の`Stream`の実装に適用される。インターフェース値を返すので、CTR暗号化を他の暗号化モードに置き換えることは局所的な変更となる。
