# Data

## Allocation with new

Goには2つの割り当てプリミティブがあり、組み込み関数`new`と`make`である。これらは異なることを行い、異なる型に適用されるため混乱を招く可能性があるが、ルールは単純である。

`new`はメモリを割り当てる組み込み関数であるが、他の一部の言語における同名のものとは異なり、メモリを初期化せず、ゼロ化するだけである。つまり、`new(T)`は型`T`の新しい項目用にゼロ化されたストレージを割り当て、そのアドレス、つまり型`*T`の値を返す。Go用語では、型`T`の新しく割り当てられたゼロ値へのポインタを返す。

`new`によって返されるメモリはゼロ化されているため、データ構造を設計する際に、各型のゼロ値がさらなる初期化なしに使用できるように配置すると便利である。これは、データ構造のユーザーが`new`で作成してすぐに作業できることを意味する。例えば、`bytes.Buffer`のドキュメントには、「`Buffer`のゼロ値は使用準備ができている空のバッファである」と記されている。同様に、`sync.Mutex`には明示的なコンストラクタや`Init`メソッドがない。代わりに、`sync.Mutex`のゼロ値はロックされていないmutexとして定義されている。

ゼロ値が有用であるという性質は推移的に機能する。次の型宣言を考えてみよう。

```go
type SyncedBuffer struct {
    lock    sync.Mutex
    buffer  bytes.Buffer
}
```

型`SyncedBuffer`の値も、割り当てまたは単なる宣言の直後に使用できる状態である。次のスニペットでは、`p`と`v`の両方がさらなる配置なしで正しく機能する。

```go
p := new(SyncedBuffer)  // 型 *SyncedBuffer
var v SyncedBuffer      // 型  SyncedBuffer
```

## Constructors and composite literals

ゼロ値では不十分で、初期化コンストラクタが必要な場合もある。パッケージ`os`から派生したこの例を見てみよう。

```go
func NewFile(fd int, name string) *File {
    if fd < 0 {
        return nil
    }
    f := new(File)
    f.fd = fd
    f.name = name
    f.dirinfo = nil
    f.nepipe = 0
    return f
}
```

ここには多くの定型文がある。複合リテラルを使用して簡略化できる。複合リテラルは、評価されるたびに新しいインスタンスを作成する式である。

```go
func NewFile(fd int, name string) *File {
    if fd < 0 {
        return nil
    }
    f := File{fd, name, nil, 0}
    return &f
}
```

Cとは異なり、ローカル変数のアドレスを返すことは完全に問題ないことに注意してほしい。変数に関連付けられたストレージは、関数が返った後も存続する。実際、複合リテラルのアドレスを取ることは、評価されるたびに新しいインスタンスを割り当てるため、これらの最後の2行を組み合わせることができる。

```go
return &File{fd, name, nil, 0}
```

複合リテラルのフィールドは順番に配置され、すべて存在する必要がある。ただし、要素にfield:valueペアとして明示的にラベルを付けることで、初期化子は任意の順序で表示でき、欠落しているものはそれぞれのゼロ値のままになる。したがって、次のように言える。

```go
return &File{fd: fd, name: name}
```

限定的なケースとして、複合リテラルにフィールドがまったく含まれていない場合、型のゼロ値が作成される。式`new(File)`と`&File{}`は等価である。

複合リテラルは、array、slice、およびmapに対しても作成でき、フィールドラベルは適切にindexまたはmapキーになる。これらの例では、`Enone`、`Eio`、および`Einval`の値に関係なく、それらが異なる限り、初期化は機能する。

```go
a := [...]string   {Enone: "no error", Eio: "Eio", Einval: "invalid argument"}
s := []string      {Enone: "no error", Eio: "Eio", Einval: "invalid argument"}
m := map[int]string{Enone: "no error", Eio: "Eio", Einval: "invalid argument"}
```

## Allocation with make

組み込み関数`make(T, args)`は`new(T)`とは異なる目的を果たす。これはslice、map、およびchannelのみを作成し、初期化された（ゼロ化されていない）型`T`の値（`*T`ではない）を返す。この区別の理由は、これら3つの型が、内部で、使用前に初期化する必要があるデータ構造への参照を表すためである。例えば、sliceは、データ（array内）へのポインタ、長さ、および容量を含む3項目のディスクリプタであり、これらの項目が初期化されるまで、sliceは`nil`である。slice、map、およびchannelの場合、`make`は内部データ構造を初期化し、使用できるように値を準備する。例えば、

```go
make([]int, 10, 100)
```

は100個のintのarrayを割り当て、次にそのarrayの最初の10要素を指す長さ10、容量100のslice構造を作成する。（sliceを作成するとき、容量は省略できる。詳細についてはsliceのセクションを参照。）対照的に、`new([]int)`は、新しく割り当てられたゼロ化されたslice構造へのポインタ、つまり`nil`のslice値へのポインタを返す。

これらの例は、`new`と`make`の違いを示している。

```go
var p *[]int = new([]int)       // slice構造を割り当てる; *p == nil; ほとんど役に立たない
var v  []int = make([]int, 100) // slice vは今や100個のintの新しいarrayを参照する

// 不必要に複雑:
var p *[]int = new([]int)
*p = make([]int, 100, 100)

// 慣用的:
v := make([]int, 100)
```

`make`はmap、slice、およびchannelにのみ適用され、ポインタを返さないことを覚えておこう。明示的なポインタを取得するには、`new`で割り当てるか、変数のアドレスを明示的に取る。

## Arrays

Arrayは、メモリの詳細なレイアウトを計画する際に有用であり、時には割り当てを回避するのに役立つが、主にsliceの構成要素である。sliceについては次のセクションで説明する。

Goにおいて:

- Arrayは値である。あるarrayを別のarrayに代入すると、すべての要素がコピーされる。
- 特に、arrayを関数に渡すと、関数はarrayへのポインタではなく、arrayのコピーを受け取る。
- arrayのサイズはその型の一部である。型`[10]int`と`[20]int`は異なる。

値プロパティは有用であるが、コストもかかる。Cのような動作と効率が必要な場合は、arrayへのポインタを渡すことができる。

```go
func Sum(a *[3]float64) (sum float64) {
    for _, v := range *a {
        sum += v
    }
    return
}

array := [...]float64{7.0, 8.5, 9.1}
x := Sum(&array)  // 明示的なアドレス演算子に注意
```

しかし、このスタイルでさえ慣用的なGoではない。代わりにsliceを使用する。

## Slices

Sliceはarrayをラップして、データのシーケンスに対するより一般的で、強力で、便利なインターフェースを提供する。変換行列のような明示的な次元を持つ項目を除いて、Goのほとんどのarrayプログラミングは、単純なarrayではなくsliceで行われる。

Sliceは基礎となるarrayへの参照を保持しており、あるsliceを別のsliceに代入すると、両方が同じarrayを参照する。関数がslice引数を取る場合、関数がsliceの要素に対して行う変更は、基礎となるarrayへのポインタを渡すのと同様に、呼び出し元に見える。したがって、`Read`関数はポインタとカウントではなく、slice引数を受け入れることができる。slice内の長さは、読み取るデータの量の上限を設定する。以下は、パッケージ`os`の`File`型の`Read`メソッドのシグネチャである。

```go
func (f *File) Read(buf []byte) (n int, err error)
```

このメソッドは、読み取られたバイト数とエラー値（ある場合）を返す。より大きなバッファ`buf`の最初の32バイトに読み込むには、バッファをslice（ここでは動詞として使用）する。

```go
n, err := f.Read(buf[0:32])
```

このようなsliceは一般的で効率的である。sliceの長さは、基礎となるarrayの制限内に収まる限り変更できる。単に自分自身のsliceに代入するだけである。sliceの容量は、組み込み関数`cap`でアクセスでき、sliceが想定できる最大長を報告する。以下は、sliceにデータを追加する関数である。データが容量を超える場合、sliceは再割り当てされる。結果のsliceが返される。

```go
func Append(slice, data []byte) []byte {
    l := len(slice)
    if l + len(data) > cap(slice) {  // 再割り当て
        // 将来の成長のために、必要な量の2倍を割り当てる。
        newSlice := make([]byte, (l+len(data))*2)
        // copy関数は事前宣言されており、任意のslice型で機能する。
        copy(newSlice, slice)
        slice = newSlice
    }
    slice = slice[0:l+len(data)]
    copy(slice[l:], data)
    return slice
}
```

`Append`が`slice`の要素を変更できるが、slice自体（ポインタ、長さ、および容量を保持するランタイムデータ構造）は値渡しされるため、後でsliceを返さなければならない。

sliceに追加するというアイデアは非常に有用であるため、`append`組み込み関数によってキャプチャされている。

## Two-dimensional slices

Goのarrayとsliceは1次元である。2D arrayまたはsliceに相当するものを作成するには、次のように、array-of-arraysまたはslice-of-slicesを定義する必要がある。

```go
type Transform [3][3]float64  // 3x3 array、実際にはarrayのarray。
type LinesOfText [][]byte     // byte sliceのslice。
```

Sliceは可変長であるため、各内部sliceの長さを異なるものにすることができる。

```go
text := LinesOfText{
    []byte("Now is the time"),
    []byte("for all good gophers"),
    []byte("to bring some fun to the party."),
}
```

2D sliceを割り当てる必要がある場合もある。例えば、ピクセルのスキャンラインを処理する場合などである。これを実現する方法は2つある。1つは各sliceを独立して割り当てる方法であり、もう1つは単一のarrayを割り当てて個々のsliceをその中に向ける方法である。

まず、一度に1行ずつ:

```go
// トップレベルのsliceを割り当てる。
picture := make([][]uint8, YSize) // yの単位ごとに1行。
// 行をループし、各行のsliceを割り当てる。
for i := range picture {
    picture[i] = make([]uint8, XSize)
}
```

次に、1つの割り当てとして、行にsliceする:

```go
// トップレベルのsliceを割り当てる。前と同じ。
picture := make([][]uint8, YSize) // yの単位ごとに1行。
// すべてのピクセルを保持する1つの大きなsliceを割り当てる。
pixels := make([]uint8, XSize*YSize) // pictureは[][]uint8だがHas type []uint8。
// 行をループし、残りのpixels sliceの前から各行をsliceする。
for i := range picture {
    picture[i], pixels = pixels[:XSize], pixels[XSize:]
}
```

## Maps

Mapは便利で強力な組み込みデータ構造であり、ある型の値（key）を別の型の値（elementまたはvalue）に関連付ける。keyは、整数、浮動小数点数、複素数、文字列、ポインタ、interface（動的型が等価性をサポートする限り）、struct、およびarrayのように、等価演算子が定義されている任意の型にできる。Sliceは、等価性が定義されていないため、mapキーとして使用できない。sliceと同様に、mapは基礎となるデータ構造への参照を保持する。

Mapは、コロンで区切られたkey-valueペアを使用した通常の複合リテラル構文を使用して構築できる。

```go
var timeZone = map[string]int{
    "UTC":  0*60*60,
    "EST": -5*60*60,
    "CST": -6*60*60,
    "MST": -7*60*60,
    "PST": -8*60*60,
}
```

Map値の代入とフェッチは、arrayやsliceと構文的に同じように見えるが、indexが整数である必要がない点が異なる。

```go
offset := timeZone["EST"]
```

map内に存在しないkeyでmap値をフェッチしようとすると、map内のエントリの型のゼロ値が返される。setは、値型`bool`のmapとして実装できる。

欠落しているエントリとゼロ値を区別する必要がある場合もある。複数代入の形式で区別できる。

```go
var seconds int
var ok bool
seconds, ok = timeZone[tz]
```

明らかな理由から、これは「comma ok」イディオムと呼ばれる。以下は、それを優れたエラーレポートと組み合わせた関数である。

```go
func offset(tz string) int {
    if seconds, ok := timeZone[tz]; ok {
        return seconds
    }
    log.Println("unknown time zone:", tz)
    return 0
}
```

実際の値を気にせずにmap内の存在をテストするには、値の通常の変数の代わりにブランク識別子（`_`）を使用できる。

```go
_, present := timeZone[tz]
```

Mapエントリを削除するには、引数がmapと削除するkeyである`delete`組み込み関数を使用する。keyが既にmapから欠落している場合でもこれを行うのは安全である。

```go
delete(timeZone, "PDT")  // 今は標準時間
```

## Printing

Goのフォーマット付き出力は、Cの`printf`ファミリーと似たスタイルを使用するが、より豊富で一般的である。関数は`fmt`パッケージにあり、大文字の名前を持つ。`fmt.Printf`、`fmt.Fprintf`、`fmt.Sprintf`など。文字列関数（`Sprintf`など）は、提供されたバッファに入力するのではなく、文字列を返す。

フォーマット文字列を提供する必要はない。`Printf`、`Fprintf`、および`Sprintf`のそれぞれに、別の関数のペアがある。例えば、`Print`と`Println`。これらの関数はフォーマット文字列を取らず、代わりに各引数のデフォルトフォーマットを生成する。

```go
fmt.Printf("Hello %d\n", 23)
fmt.Fprint(os.Stdout, "Hello ", 23, "\n")
fmt.Println("Hello", 23)
fmt.Println(fmt.Sprint("Hello ", 23))
```

フォーマット付き出力関数`fmt.Fprint`とその仲間は、第1引数として`io.Writer`interfaceを実装する任意のオブジェクトを取る。変数`os.Stdout`と`os.Stderr`はよく知られたインスタンスである。

デフォルトの変換だけが必要な場合、例えば整数の10進数の場合、包括的なフォーマット`%v`（「value」の略）を使用できる。結果は`Print`と`Println`が生成するものと正確に同じである。さらに、そのフォーマットは、array、slice、struct、およびmapを含む任意の値を出力できる。

structを出力する際、修飾されたフォーマット`%+v`は構造体のフィールドに名前を注釈し、任意の値に対して代替フォーマット`%#v`は値を完全なGo構文で出力する。

```go
type T struct {
    a int
    b float64
    c string
}
t := &T{ 7, -2.35, "abc\tdef" }
fmt.Printf("%v\n", t)
fmt.Printf("%+v\n", t)
fmt.Printf("%#v\n", t)
fmt.Printf("%#v\n", timeZone)
```

は次を出力する。

```text
&{7 -2.35 abc   def}
&{a:7 b:-2.35 c:abc    def}
&main.T{a:7, b:-2.35, c:"abc\tdef"}
map[string]int{"CST":-21600, "EST":-18000, "MST":-25200, "PST":-28800, "UTC":0}
```

別の便利なフォーマットは`%T`で、値の型を出力する。

```go
fmt.Printf("%T\n", timeZone)
```

は次を出力する。

```text
map[string]int
```

カスタム型のデフォルトフォーマットを制御したい場合、必要なのは型にシグネチャ`String() string`のメソッドを定義することだけである。

```go
func (t *T) String() string {
    return fmt.Sprintf("%d/%g/%q", t.a, t.b, t.c)
}
fmt.Printf("%v\n", t)
```

`String`メソッド内で無限に再帰する方法で`Sprintf`を呼び出して`String`メソッドを構築してはいけない。

```go
type MyString string

func (m MyString) String() string {
    return fmt.Sprintf("MyString=%s", m) // エラー: 永遠に再帰する。
}
```

これは簡単に修正できる。引数を基本的な文字列型に変換すると、メソッドを持たない。

```go
type MyString string
func (m MyString) String() string {
    return fmt.Sprintf("MyString=%s", string(m)) // OK: 変換に注意。
}
```

## Append

組み込み関数`append`は、sliceの末尾に要素を追加し、結果を返す。基礎となるarrayが変更される可能性があるため、結果を返す必要がある。

```go
x := []int{1,2,3}
x = append(x, 4, 5, 6)
fmt.Println(x)
```

は`[1 2 3 4 5 6]`を出力する。

sliceにsliceを追加するには、呼び出しサイトで`...`を使用する。

```go
x := []int{1,2,3}
y := []int{4,5,6}
x = append(x, y...)
fmt.Println(x)
```

その`...`がないと、型が間違っているためコンパイルされない。`y`は型`int`ではない。
