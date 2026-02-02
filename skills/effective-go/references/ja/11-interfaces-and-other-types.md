# インターフェースとその他の型

## インターフェース

Goにおけるインターフェースは、オブジェクトの振る舞いを指定する方法を提供する。もし何かが*これ*を実行できるなら、*ここ*で使用できる、ということである。既にいくつかの簡単な例を見てきた。カスタムプリンタは`String`メソッドによって実装でき、`Fprintf`は`Write`メソッドを持つものに対して出力を生成できる。1つまたは2つのメソッドのみを持つインターフェースはGoのコードでは一般的であり、通常は`Write`を実装するものに対する`io.Writer`のように、メソッドから派生した名前が付けられる。

1つの型は複数のインターフェースを実装できる。例えば、コレクションは`sort.Interface`を実装していれば`sort`パッケージのルーチンによってソート可能であり、これは`Len()`、`Less(i, j int) bool`、`Swap(i, j int)`を含む。また、カスタムフォーマッタを持つこともできる。この工夫された例では、`Sequence`が両方を満たしている。

```go
type Sequence []int

// sort.Interface が要求するメソッド。
func (s Sequence) Len() int {
    return len(s)
}
func (s Sequence) Less(i, j int) bool {
    return s[i] < s[j]
}
func (s Sequence) Swap(i, j int) {
    s[i], s[j] = s[j], s[i]
}

// Copy は Sequence のコピーを返す。
func (s Sequence) Copy() Sequence {
    copy := make(Sequence, 0, len(s))
    return append(copy, s...)
}

// 出力用メソッド - 出力前に要素をソートする。
func (s Sequence) String() string {
    s = s.Copy() // コピーを作成する。引数を上書きしない。
    sort.Sort(s)
    str := "["
    for i, elem := range s { // ループは O(N²)。次の例で改善する。
        if i > 0 {
            str += " "
        }
        str += fmt.Sprint(elem)
    }
    return str + "]"
}
```

## 変換

`Sequence`の`String`メソッドは、`Sprint`が既にスライスに対して行っている処理を再現している。`Sprint`を呼び出す前に`Sequence`を単純な`[]int`に変換すれば、処理を共有でき(また高速化もできる)。

```go
func (s Sequence) String() string {
    s = s.Copy()
    sort.Sort(s)
    return fmt.Sprint([]int(s))
}
```

このメソッドは、`String`メソッドから`Sprintf`を安全に呼び出すための変換技法の別の例である。2つの型(`Sequence`と`[]int`)は型名を無視すれば同じであるため、それらの間で変換することは合法である。変換は新しい値を作成せず、既存の値が一時的に新しい型を持つかのように振る舞うだけである。

Goのプログラムでは、異なるメソッドのセットにアクセスするために式の型を変換することは慣用的である。例として、既存の型`sort.IntSlice`を使用して、例全体を次のように短縮できる。

```go
type Sequence []int

// 出力用メソッド - 出力前に要素をソートする
func (s Sequence) String() string {
    s = s.Copy()
    sort.IntSlice(s).Sort()
    return fmt.Sprint([]int(s))
}
```

## インターフェース変換と型アサーション

型switchは変換の一形態である。インターフェースを受け取り、switchの各caseに対して、ある意味でそのcaseの型に変換する。以下は、`fmt.Printf`の内部コードが型switchを使用して値を文字列に変換する方法の簡略版である。

```go
type Stringer interface {
    String() string
}

var value interface{} // 呼び出し元から提供される値。
switch str := value.(type) {
case string:
    return str
case Stringer:
    return str.String()
}
```

もし関心のある型が1つだけならどうだろうか。1つのcaseを持つ型switchでもよいが、*型アサーション*でもよい。型アサーションはインターフェース値を受け取り、そこから指定された明示的な型の値を抽出する。

```go
value.(typeName)
```

panicを防ぐには、「comma, ok」イディオムを使用して安全にテストする。

```go
str, ok := value.(string)
if ok {
    fmt.Printf("string value is: %q\n", str)
} else {
    fmt.Printf("value is not a string\n")
}
```

型アサーションが失敗した場合、`str`は依然として存在し、string型であるが、ゼロ値である空文字列を持つことになる。

## 一般性

型がインターフェースを実装するためだけに存在し、そのインターフェースを超えたエクスポートされたメソッドを決して持たない場合、型自体をエクスポートする必要はない。インターフェースだけをエクスポートすることで、値がインターフェースで説明されているもの以外に興味深い振る舞いを持たないことが明確になる。また、共通のメソッドのすべてのインスタンスでドキュメントを繰り返す必要もなくなる。

このような場合、コンストラクタは実装型ではなくインターフェース値を返すべきである。例として、hashライブラリでは`crc32.NewIEEE`と`adler32.New`の両方がインターフェース型`hash.Hash32`を返す。GoプログラムでCRC-32アルゴリズムをAdler-32に置き換えるには、コンストラクタの呼び出しを変更するだけでよい。コードの残りの部分はアルゴリズムの変更による影響を受けない。

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

`NewCTR`は、特定の暗号化アルゴリズムとデータソースだけでなく、`Block`インターフェースの任意の実装と任意の`Stream`に適用される。これらはインターフェース値を返すため、CTR暗号化を他の暗号化モードに置き換えることは局所的な変更となる。
