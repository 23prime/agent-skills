# Go Wiki: Go Code Review Comments

このページでは、Goコードのレビュー時によく行われるコメントを集約しており、簡潔な指摘で詳細な説明を参照できるようにしている。これは一般的なスタイル問題の一覧であり、包括的なスタイルガイドではない。

本ページは[Effective Go](https://go.dev/doc/effective_go)の補足として利用できる。

テストに関する追加コメントは[Go Test Comments](/wiki/TestComments)を参照のこと。

Googleは、より詳細な[Go Style Guide](https://google.github.io/styleguide/go/decisions)を公開している。

## Gofmt

コードに対して[gofmt](https://pkg.go.dev/cmd/gofmt/)を実行し、機械的なスタイル問題の大部分を自動的に修正すること。実際に使用されているほぼ全てのGoコードが`gofmt`を使用している。本ドキュメントの残りの部分では、機械的でないスタイルのポイントを扱う。

代替手段として[goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports)も利用できる。これは`gofmt`のスーパーセットであり、必要に応じてimport行を追加・削除する機能を持つ。

## Comment Sentences

[Effective Go - Commentary](https://go.dev/doc/effective_go#commentary)を参照のこと。宣言をドキュメント化するコメントは、少し冗長に見えても完全な文にすべきである。このアプローチにより、godocドキュメントとして抽出された際に適切にフォーマットされる。コメントは説明対象の名前で始まり、ピリオドで終わること。

```go
// Request represents a request to run a command.
type Request struct { ...

// Encode writes the JSON encoding of req to w.
func Encode(w io.Writer, req *Request) { ...
```

## Contexts

context.Context型の値は、セキュリティ認証情報、トレーシング情報、デッドライン、キャンセルシグナルをAPI境界やプロセス境界を越えて伝搬する。Goプログラムは、受信RPCやHTTPリクエストから送信リクエストまで、関数呼び出しチェーン全体で明示的にContextを渡す。

Contextを使用するほとんどの関数は、最初のパラメータとして受け取るべきである。

```go
func F(ctx context.Context, /* other arguments */) {}
```

リクエスト固有でない関数はcontext.Background()を使用してもよいが、必要ないと思う場合でもContextを渡す側に倒すこと。デフォルトのケースはContextを渡すことであり、context.Background()を直接使用するのは代替案が誤りである明確な理由がある場合のみとする。

構造体型にContextメンバーを追加してはならない。代わりに、Contextを渡す必要がある各メソッドにctxパラメータを追加すること。唯一の例外は、標準ライブラリやサードパーティライブラリのインターフェースに合わせる必要があるメソッドの場合である。

カスタムContext型を作成したり、関数シグネチャでContext以外のインターフェースを使用したりしてはならない。

アプリケーションデータを渡す必要がある場合は、パラメータ、レシーバー、グローバル変数に配置するか、本当にそこに属する場合のみContext値に配置すること。

Contextは不変であるため、同じctxを同じデッドライン、キャンセルシグナル、認証情報、親トレースなどを共有する複数の呼び出しに渡しても問題ない。

## Copying

別のパッケージから構造体をコピーする際は、予期しないエイリアシングを避けるため注意すること。例えば、bytes.Buffer型は`[]byte` sliceを含んでいる。`Buffer`をコピーすると、コピー内のsliceが元の配列をエイリアスする可能性があり、その後のメソッド呼び出しで驚くべき効果が生じる。

一般的に、メソッドがポインタ型`*T`に関連付けられている場合は、型`T`の値をコピーしてはならない。

## Crypto Rand

パッケージ[`math/rand`](https://pkg.go.dev/math/rand)や[`math/rand/v2`](https://pkg.go.dev/math/rand/v2)を使用して鍵を生成してはならない。使い捨ての鍵であっても同様である。[`Time.Nanoseconds()`](https://pkg.go.dev/time#Time.Nanosecond)でシードした場合、数ビットのエントロピーしか得られない。代わりに[`crypto/rand.Reader`](https://pkg.go.dev/crypto/rand#pkg-variables)を使用すること。テキストが必要な場合は[`crypto/rand.Text`](https://pkg.go.dev/crypto/rand#Text)を使用するか、またはランダムバイトを[`encoding/hex`](https://pkg.go.dev/encoding/hex)や[`encoding/base64`](https://pkg.go.dev/encoding/base64)でエンコードすること。

```go
import (
    "crypto/rand"
    "fmt"
)

func Key() string {
  return rand.Text()
}
```

## Declaring Empty Slices

空のsliceを宣言する場合は

```go
var t []string
```

を優先し、

```go
t := []string{}
```

は避けること。

前者はnil slice値を宣言するが、後者は非nilで長さゼロのsliceである。これらは機能的には等価であり、`len`と`cap`は両方ともゼロであるが、nil sliceが推奨されるスタイルである。

非nilで長さゼロのsliceが好まれる限定的な状況もある。例えば、JSONオブジェクトをエンコードする場合(`nil` sliceは`null`にエンコードされるが、`[]string{}`はJSON配列`[]`にエンコードされる)。

インターフェースを設計する際は、nil sliceと非nilで長さゼロのsliceを区別しないようにすること。微妙なプログラミングエラーにつながる可能性がある。

Goにおけるnilの詳細については、Francesc Campoyの講演[Understanding Nil](https://www.youtube.com/watch?v=ynoY2xz-F8s)を参照のこと。

## Doc Comments

全てのトップレベルのエクスポートされた名前にはdocコメントが必要であり、自明でないエクスポートされていない型や関数の宣言にも必要である。コメント規約の詳細については[Effective Go - Commentary](https://go.dev/doc/effective_go#commentary)を参照のこと。

## Don't Panic

[Effective Go - Errors](https://go.dev/doc/effective_go#errors)を参照のこと。通常のエラー処理にpanicを使用してはならない。errorと複数の戻り値を使用すること。

## Error Strings

エラー文字列は(固有名詞や頭字語で始まる場合を除いて)大文字で始めたり句読点で終わらせたりしてはならない。通常、他のコンテキストに続けて表示されるためである。つまり、`fmt.Errorf("something bad")`を使用し、`fmt.Errorf("Something bad")`は使用しない。こうすることで`log.Printf("Reading %s: %v", filename, err)`がメッセージ途中に不自然な大文字を含まずにフォーマットされる。これはロギングには適用されない。ロギングは暗黙的に行指向であり、他のメッセージ内で結合されない。

## Examples

新しいパッケージを追加する際は、意図された使用方法の例を含めること。実行可能なExampleか、完全な呼び出しシーケンスを示すシンプルなテストなど。

[testable Example() functions](https://go.dev/blog/examples)について詳しく読むこと。

## Goroutine Lifetimes

goroutineを起動する際は、いつ(または、するかどうか)終了するのかを明確にすること。

goroutineはchannel送受信でブロックすることでリークする可能性がある。ガベージコレクターは、ブロックされているchannelに到達不能になったとしてもgoroutineを終了しない。

goroutineがリークしない場合でも、不要になった時点で実行中のままにしておくと、他の微妙で診断困難な問題を引き起こす可能性がある。クローズされたchannelへの送信はpanicを引き起こす。「結果が不要になった後」でも使用中の入力を変更するとデータ競合につながる可能性がある。また、任意に長い時間goroutineを実行中のままにしておくと、予測不可能なメモリ使用につながる。

並行コードは、goroutineのライフタイムが明白になるよう十分にシンプルに保つこと。それが実現可能でない場合は、いつ、なぜgoroutineが終了するのかをドキュメント化すること。

## Handle Errors

[Effective Go - Errors](https://go.dev/doc/effective_go#errors)を参照のこと。`_`変数を使用してエラーを破棄してはならない。関数がエラーを返す場合は、関数が成功したことを確認するためにチェックすること。エラーを処理するか、返すか、真に例外的な状況ではpanicすること。

## Imports

名前の衝突を避ける場合を除き、importの名前変更は避けること。良いパッケージ名は名前変更を必要としない。衝突が発生した場合は、最もローカルまたはプロジェクト固有のimportの名前を変更することを優先する。

importはグループに整理され、グループ間には空行がある。標準ライブラリパッケージは常に最初のグループに配置される。

```go
package main

import (
    "fmt"
    "hash/adler32"
    "os"

    "github.com/foo/bar"
    "rsc.io/goversion/version"
)
```

[goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports)がこれを自動的に行う。

## Import Blank

副作用のためだけにインポートされるパッケージ(`import _ "pkg"`構文を使用)は、プログラムのmainパッケージ、または必要とするテスト内でのみインポートすべきである。

## Import Dot

import . 形式は、循環依存のためテスト対象パッケージの一部にできないテストで有用である。

```go
package foo_test

import (
    "bar/testutil" // also imports "foo"
    . "foo"
)
```

この場合、テストファイルはbar/testutilを使用するためpackage fooにできない。bar/tesutilはfooをimportするためである。そのため、'import .' 形式を使用してファイルをpackage fooの一部であるかのように扱う。この1つのケースを除き、プログラム内でimport .を使用してはならない。プログラムが非常に読みにくくなる。Quuxのような名前が現在のパッケージのトップレベル識別子なのか、インポートされたパッケージのものなのかが不明確になるためである。

## In-Band Errors

Cおよび類似の言語では、関数がエラーや結果の欠落を通知するために-1やnullのような値を返すことが一般的である。

```go
// Lookup returns the value for key or "" if there is no mapping for key.
func Lookup(key string) string

// Failing to check for an in-band error value can lead to bugs:
Parse(Lookup(key))  // returns "parse failure for value" instead of "no value for key"
```

Goの複数戻り値のサポートは、より良いソリューションを提供する。クライアントにin-bandエラー値をチェックさせる代わりに、関数は他の戻り値が有効かどうかを示す追加の値を返すべきである。この戻り値はerrorでもよいし、説明が不要な場合はbooleanでもよい。最後の戻り値とすべきである。

```go
// Lookup returns the value for key or ok=false if there is no mapping for key.
func Lookup(key string) (value string, ok bool)
```

これにより、呼び出し側が結果を誤って使用することを防ぐ。

```go
Parse(Lookup(key))  // compile-time error
```

そして、より堅牢で読みやすいコードを促進する。

```go
value, ok := Lookup(key)
if !ok {
    return fmt.Errorf("no value for %q", key)
}
return Parse(value)
```

このルールはエクスポートされた関数に適用されるが、エクスポートされていない関数にも有用である。

nil、""、0、-1のような戻り値は、関数の有効な結果である場合、つまり呼び出し側が他の値と異なる処理をする必要がない場合は問題ない。

package "strings"の関数など、一部の標準ライブラリ関数はin-bandエラー値を返す。これは、プログラマーによる注意深さを必要とする代償として、文字列操作コードを大幅に簡素化する。一般的に、Goコードはエラーのために追加の値を返すべきである。

## Indent Error Flow

通常のコードパスを最小限のインデントに保ち、エラー処理をインデントして最初に処理するようにすること。これにより、通常のパスを視覚的に素早くスキャンできるようになり、コードの可読性が向上する。例えば、次のように書いてはならない。

```go
if err != nil {
    // error handling
} else {
    // normal code
}
```

代わりに、次のように書くこと。

```go
if err != nil {
    // error handling
    return // or continue, etc.
}
// normal code
```

`if`文に初期化文がある場合、例えば

```go
if x, err := f(); err != nil {
    // error handling
    return
} else {
    // use x
}
```

このような場合は、短い変数宣言を独自の行に移動する必要がある。

```go
x, err := f()
if err != nil {
    // error handling
    return
}
// use x
```

## Initialisms

名前内の初期語や頭字語(例:"URL"や"NATO")は一貫した大文字小文字を持つべきである。例えば、"URL"は"URL"または"url"("urlPony"や"URLPony"のように)として表示されるべきであり、決して"Url"としてはならない。例として:ServeHTTPであってServeHttpではない。複数の初期化された「単語」を持つ識別子の場合、例えば"xmlHTTPRequest"または"XMLHTTPRequest"を使用する。

このルールは"identifier"(ほぼ全てのケースで"id"が"ego"、"superego"の"id"でない場合)の短縮形である場合の"ID"にも適用される。したがって"appId"ではなく"appID"と書くこと。

protocol bufferコンパイラによって生成されたコードは、このルールから免除される。人間が書いたコードは、機械が書いたコードよりも高い基準を保持される。

## Interfaces

Goのインターフェースは一般的に、その値を実装するパッケージではなく、インターフェース型の値を使用するパッケージに属する。実装パッケージは具体的な(通常はポインタまたは構造体)型を返すべきである。こうすることで、広範なリファクタリングを必要とせずに実装に新しいメソッドを追加できる。

「モックのため」に実装側のAPIでインターフェースを定義してはならない。代わりに、実際の実装の公開APIを使用してテストできるようAPIを設計すること。

使用される前にインターフェースを定義してはならない。現実的な使用例がないと、インターフェースが必要かどうか、ましてやどのようなメソッドを含むべきかを判断することは困難である。

```go
package consumer  // consumer.go

type Thinger interface { Thing() bool }

func Foo(t Thinger) string { … }
```

```go
package consumer // consumer_test.go

type fakeThinger struct{ … }
func (t fakeThinger) Thing() bool { … }
…
if Foo(fakeThinger{…}) == "x" { … }
```

```go
// DO NOT DO IT!!!
package producer

type Thinger interface { Thing() bool }

type defaultThinger struct{ … }
func (t defaultThinger) Thing() bool { … }

func NewThinger() Thinger { return defaultThinger{ … } }
```

代わりに具体的な型を返し、コンシューマーがプロデューサーの実装をモックできるようにする。

```go
package producer

type Thinger struct{ … }
func (t Thinger) Thing() bool { … }

func NewThinger() Thinger { return Thinger{ … } }
```

## Line Length

Goコードには厳密な行の長さ制限はないが、不快なほど長い行は避けること。同様に、長い方が読みやすい場合(例えば、反復的な場合)に、短く保つために改行を追加してはならない。

ほとんどの場合、人々が「不自然に」行を折り返す時(例えば、関数呼び出しや関数宣言の途中など)、適度な数のパラメータと適度に短い変数名を使用していれば折り返しは不要である。長い行は長い名前とともに現れる傾向があり、長い名前を取り除くことが大いに役立つ。

言い換えると、書いている内容のセマンティクスに基づいて行を分割すること(一般的なルールとして)、行の長さのためではない。これによって長すぎる行が生じる場合は、名前やセマンティクスを変更すれば、おそらく良い結果が得られる。

これは実際には、関数がどれくらい長くあるべきかについてのアドバイスと全く同じである。「N行を超える関数を作らない」というルールはないが、明らかに長すぎる関数や、細かすぎて反復的な関数というものは存在する。解決策は、行数を数え始めることではなく、関数の境界を変更することである。

## Mixed Caps

[Effective Go - Mixed Caps](https://go.dev/doc/effective_go#mixed-caps)を参照のこと。これは他の言語の慣例を破る場合でも適用される。例えば、エクスポートされていない定数は`MaxLength`や`MAX_LENGTH`ではなく`maxLength`である。

[Initialisms](#initialisms)も参照のこと。

## Named Result Parameters

godocでどのように見えるかを考慮すること。次のような名前付き結果パラメータ:

```go
func (n *Node) Parent1() (node *Node) {}
func (n *Node) Parent2() (node *Node, err error) {}
```

はgodocで反復的になる。次のように使用する方が良い。

```go
func (n *Node) Parent1() *Node {}
func (n *Node) Parent2() (*Node, error) {}
```

一方で、関数が同じ型の2つまたは3つのパラメータを返す場合、または結果の意味がコンテキストから明確でない場合、いくつかのコンテキストで名前を追加することは有用である。varを関数内で宣言するのを避けるためだけに結果パラメータに名前を付けてはならない。それは、不必要なAPI冗長性の代償として、わずかな実装の簡潔さをトレードオフしている。

```go
func (f *Foo) Location() (float64, float64, error)
```

は次よりも明確でない。

```go
// Location returns f's latitude and longitude.
// Negative values mean south and west, respectively.
func (f *Foo) Location() (lat, long float64, err error)
```

Naked returnは、関数が数行の場合は問題ない。中規模の関数になったら、戻り値を明示すること。補足:結果パラメータに名前を付けることで、naked returnを使用できるようにするだけの価値はない。ドキュメントの明確性は、関数内で1行か2行を節約することよりも常に重要である。

最後に、場合によっては、遅延クロージャで変更するために結果パラメータに名前を付ける必要がある。それは常に問題ない。

## Naked Returns

引数なしの`return`文は、名前付き戻り値を返す。これは「naked」returnとして知られる。

```go
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return
}
```

[Named Result Parameters](#named-result-parameters)を参照のこと。

## Package Comments

godocによって提示される全てのコメントと同様に、パッケージコメントはpackage句に隣接し、空行なしで表示される必要がある。

```go
// Package math provides basic constants and mathematical functions.
package math
```

```go
/*
Package template implements data-driven templates for generating textual
output such as HTML.
....
*/
package template
```

「package main」コメントの場合、バイナリ名の後に他のコメントスタイルが許容される(最初に来る場合は大文字にしてもよい)。例えば、ディレクトリ`seedgen`内の`package main`では次のように書ける。

```go
// Binary seedgen ...
package main
```

または

```go
// Command seedgen ...
package main
```

または

```go
// Program seedgen ...
package main
```

または

```go
// The seedgen command ...
package main
```

または

```go
// The seedgen program ...
package main
```

または

```go
// Seedgen ..
package main
```

これらは例であり、これらの妥当なバリエーションは許容される。

文を小文字の単語で始めることは、パッケージコメントの許容可能なオプションではないことに注意すること。これらは公開されて見えるものであり、文の最初の単語を大文字にすることを含む適切な英語で書かれるべきである。バイナリ名が最初の単語である場合、コマンドライン呼び出しのスペリングと厳密に一致しなくても、大文字にすることが必要である。

コメント規約の詳細については[Effective Go - Commentary](https://go.dev/doc/effective_go#commentary)を参照のこと。

## Package Names

パッケージ内の名前への全ての参照はパッケージ名を使用して行われるため、識別子からその名前を省略できる。例えば、package chubby内にいる場合、クライアントが`chubby.ChubbyFile`と書く型ChubbyFileは不要である。代わりに、型を`File`と命名すれば、クライアントは`chubby.File`と書く。util、common、misc、api、types、interfacesのような意味のないパッケージ名は避けること。詳細については[Effective Go - Package Names](https://go.dev/doc/effective_go#package-names)および[Go Blog - Package Names](https://go.dev/blog/package-names)を参照のこと。

## Pass Values

数バイトを節約するためだけに関数引数としてポインタを渡してはならない。関数が引数`x`を`*x`としてのみ参照する場合、引数はポインタであるべきではない。これには、文字列へのポインタ(`*string`)やインターフェース値へのポインタ(`*io.Reader`)を渡すことが含まれる。どちらの場合も、値自体は固定サイズであり、直接渡すことができる。このアドバイスは大きな構造体、または成長する可能性のある小さな構造体には適用されない。

## Receiver Names

メソッドのレシーバーの名前は、そのアイデンティティを反映したものであるべきである。多くの場合、型の1文字または2文字の略語で十分である("Client"の場合は"c"または"cl"など)。"me"、"this"、"self"のような一般的な名前を使用してはならない。これらはオブジェクト指向言語で典型的な識別子であり、メソッドに特別な意味を与える。Goでは、メソッドのレシーバーは単なる別のパラメータであるため、それに応じて命名されるべきである。名前はメソッド引数ほど説明的である必要はない。その役割は明白であり、ドキュメント的な目的を果たさないためである。型の全てのメソッドのほぼ全ての行に表示されるため、非常に短くてもよい。馴染みがあれば簡潔さが許される。一貫性も保つこと。あるメソッドでレシーバーを"c"と呼ぶなら、別のメソッドで"cl"と呼んではならない。

## Receiver Type

メソッドに値レシーバーを使うかポインタレシーバーを使うかの選択は、特に新しいGoプログラマーには難しい場合がある。迷ったらポインタを使用すること。ただし、効率上の理由、例えば小さな不変の構造体や基本型の値などで、値レシーバーが意味を持つ場合もある。有用なガイドライン:

- レシーバーがmap、func、chanの場合、それらへのポインタを使用してはならない。レシーバーがsliceでメソッドがsliceを再スライスまたは再割り当てしない場合、それへのポインタを使用してはならない。
- メソッドがレシーバーを変更する必要がある場合、レシーバーはポインタでなければならない。
- レシーバーがsync.Mutexまたは類似の同期フィールドを含む構造体である場合、コピーを避けるためレシーバーはポインタでなければならない。
- レシーバーが大きな構造体または配列である場合、ポインタレシーバーの方が効率的である。どのくらいが大きいか?全ての要素を引数としてメソッドに渡すのと同等であると仮定する。大きすぎると感じる場合、レシーバーにとっても大きすぎる。
- 関数またはメソッドが、このメソッドから呼び出された時またはこのメソッドから呼び出した時に、並行してまたは同時にレシーバーを変更する可能性があるか?値型は、メソッドが呼び出された時にレシーバーのコピーを作成するため、外部の更新はこのレシーバーに適用されない。変更が元のレシーバーで可視である必要がある場合、レシーバーはポインタでなければならない。
- レシーバーが構造体、配列、またはsliceで、その要素のいずれかが変更される可能性のある何かへのポインタである場合、読者に意図をより明確にするため、ポインタレシーバーを優先する。
- レシーバーが小さな配列または構造体で、自然に値型である場合(例えば、time.Time型のようなもの)、可変フィールドがなくポインタもない場合、または単純な基本型(intやstringなど)の場合、値レシーバーが意味を持つ。値レシーバーは生成されるガベージの量を減らすことができる。値が値メソッドに渡される場合、ヒープに割り当てる代わりにスタック上のコピーを使用できる。(コンパイラはこの割り当てを避けるよう賢く振る舞おうとするが、常に成功するわけではない。)この理由で、プロファイリングせずに値レシーバー型を選択してはならない。
- レシーバー型を混在させてはならない。全ての利用可能なメソッドにポインタまたは構造体型のいずれかを選択すること。
- 最後に、迷った場合はポインタレシーバーを使用すること。

## Synchronous Functions

同期関数を優先する。同期関数は結果を直接返すか、returnする前にコールバックやchannel操作を完了する関数である。非同期関数よりも同期関数を優先する。

同期関数はgoroutineを呼び出し内にローカライズし、ライフタイムについて推論しやすくし、リークやデータ競合を避けやすくする。また、テストも容易である。呼び出し側は入力を渡し、ポーリングや同期の必要なしに出力をチェックできる。

呼び出し側がより多くの並行性を必要とする場合、別のgoroutineから関数を呼び出すことで簡単に追加できる。しかし、呼び出し側で不必要な並行性を除去することは非常に困難であり、時には不可能である。

## Useful Test Failures

テストは、何が間違っていたか、どのような入力だったか、実際に何が得られたか、何が期待されていたかを示す有用なメッセージで失敗すべきである。assertFooヘルパーをたくさん書きたくなるかもしれないが、ヘルパーが有用なエラーメッセージを生成することを確認すること。失敗したテストをデバッグする人が自分でも自分のチームでもないと仮定すること。典型的なGoテストは次のように失敗する。

```go
if got != tt.want {
    t.Errorf("Foo(%q) = %d; want %d", tt.in, got, tt.want) // or Fatalf, if test can't test anything more past this point
}
```

ここでの順序は、actual != expectedであり、メッセージもその順序を使用していることに注意すること。一部のテストフレームワークは、これを逆に書くことを推奨している。0 != x、"expected 0, got x"など。Goはそうではない。

大量のタイピングに見える場合は、[table-driven test](TableDrivenTests)を書きたくなるかもしれない。

異なる入力で失敗したテストを明確にする別の一般的なテクニックは、それぞれの呼び出し側を異なるTestFoo関数でラップし、その名前でテストが失敗するようにすることである。

```go
func TestSingleValue(t *testing.T) { testHelper(t, []int{80}) }
func TestNoValues(t *testing.T)    { testHelper(t, []int{}) }
```

いずれにせよ、将来コードをデバッグする人のために有用なメッセージで失敗させることは、あなたの責任である。

## Variable Names

Goの変数名は長いよりも短くすべきである。これは特に、限定されたスコープを持つローカル変数に当てはまる。`lineCount`よりも`c`を優先する。`sliceIndex`よりも`i`を優先する。

基本的なルール:名前がその宣言から離れて使用されるほど、より説明的な名前でなければならない。メソッドレシーバーの場合、1文字または2文字で十分である。ループインデックスやリーダーのような一般的な変数は1文字(`i`、`r`)でよい。より珍しいものやグローバル変数には、より説明的な名前が必要である。

[the Google Go Style Guide](https://google.github.io/styleguide/go/decisions#variable-names)のより詳細な議論も参照のこと。
