# Google Go スタイル決定事項

本ドキュメントは、Google における Go プログラミングのスタイル決定事項を含み、コアスタイルガイドを補完するものである。Go の可読性メンターのために、標準的なガイダンス、説明、例を提供する。

## 命名

### アンダースコア

Go の名前は一般的にアンダースコアを避けるが、3つの例外がある:

- 生成コードからのみインポートされるパッケージ名
- `*_test.go` ファイル内の Test/Benchmark/Example 関数名
- 低レベルの OS/cgo 相互運用ライブラリ（まれ）

### パッケージ名

パッケージ名は簡潔で、小文字のみ、文字と数字のみを使用する必要がある。複数語のパッケージは小文字のまま区切らない（例: `tab_writer` ではなく `tabwriter`）。`count` のような一般的な変数で隠蔽される可能性のある名前を避ける。生成された proto パッケージはアンダースコアを除去し、`pb` サフィックスを付けてリネームする必要がある。

### レシーバ名

メソッドレシーバは短く（1-2文字）、型の略語を使い、一貫して適用する:

- `func (tray Tray)` ではなく `func (t Tray)`
- `func (info *ResearchInfo)` ではなく `func (ri *ResearchInfo)`

### 定数名

定数は MixedCaps を使用する（エクスポートされるものは大文字始まり、されないものは小文字始まり）。名前は値ではなく、定数の役割を反映すべきである:

```go
// 良い例:
const MaxPacketSize = 512
const ExecuteBit = 1 << iota

// 悪い例:
const MAX_PACKET_SIZE = 512
const kMaxBufferSize = 1024
```

### 頭字語

頭字語は一貫した大文字・小文字を維持する: `URL` または `url`、`Url` は不可。`XMLAPI` のような複合名では、各頭字語が一貫した大文字・小文字を維持する。`iOS` のような大文字・小文字混在の頭字語は、エクスポート性を変更しない限り `IOS`（エクスポート）または `iOS`（非エクスポート）として表記する:

| 用途 | エクスポート | 非エクスポート |
| ------- | ---------- | ----------- |
| XML API | `XMLAPI` | `xmlAPI` |
| iOS | `IOS` | `iOS` |
| gRPC | `GRPC` | `gRPC` |

### ゲッター

コンセプトが「get」を使用する場合（例: HTTP GET）を除き、「Get」プレフィックスを省略する。`GetCounts()` より `Counts()` を優先する。複雑な/リモート操作には `Compute` または `Fetch` を使用する。

### 変数名

名前の長さはスコープサイズに比例し、使用頻度に反比例すべきである:

- **小さなスコープ（1-7行）:** 短い名前が許容される
- **中程度のスコープ（8-15行）:** より説明的な名前が必要
- **大きなスコープ（15-25行以上）:** 詳細な名前が必要

冗長な型情報を避ける: `numUsers` や `usersInt` より `userCount` が良い。文脈から明らかな語を省略する — `UserCount` メソッド内では `userCount` ではなく `count` を使用する。

#### 1文字の変数

メソッドレシーバ、おなじみの型変数（`io.Reader` に対する `r`）、ループインデックス（`i`）、座標（`x`, `y`）には許容される。短いスコープの略語は明白な場合に機能する。

### 繰り返しの問題

**パッケージ vs. エクスポートされたシンボル:** パッケージ名とエクスポートされた型の間の冗長性を減らす:

- `widget.NewWidget` → `widget.New`
- `db.LoadFromDatabase` → `db.Load`

**変数名 vs. 型:** コンパイラは型を知っている。文脈が明確にするなら型情報を省略する:

- `numUsers` → `users`
- `nameString` → `name`
- `primaryProject` → `primary`（スコープ内に1つのバージョンのみの場合）

**外部コンテキスト vs. ローカル名:** パッケージ/メソッド/型名がコンテキストを提供する。繰り返しを避ける:

- パッケージ `ads/targeting/revenue/reporting` 内: `AdsTargetingRevenueReport` ではなく `Report` を使用
- `Project` のメソッド内: `ProjectName()` ではなく `Name()` を使用
- パッケージ `sqldb` 内: `DBConnection` ではなく `Connection` を使用

## コメント

### コメントの行長

狭いターミナルでは80カラム幅を目安とするが、コメントはこれを超えることがある。必要に応じて句読点で改行する（標準ライブラリでは60-70文字が一般的）。このガイドラインのためだけに既存のコードを再整形しない — チームはリファクタリング時に適宜適用すべきである。

### ドキュメントコメント

すべてのトップレベルのエクスポートされた名前にはドキュメントコメントが必要であり、動作が明白でない非エクスポートの宣言にも必要である。コメントはオブジェクト名で始まる完全な文であるべきである:

```go
// 良い例:
// A Request represents a command execution request.
type Request struct { ... }

// Encode writes the JSON encoding of req to w.
func Encode(w io.Writer, req *Request) { ... }
```

### コメントの文

完全な文は大文字で始まり句読点を付ける必要がある。断片にはそのような要件はない。ドキュメントコメントは常に完全な文を必要とする。単純なフィールドコメントはフィールド名を主語として仮定するフレーズでよい。

### 例

テストファイル内に実行可能な例を提供する。それらは Godoc に表示される。実行可能な例が実現不可能な場合、標準的なフォーマット規約に従ってコメント内にコードスニペットを使用する。

### 名前付き戻り値パラメータ

関数が同じ型の複数のパラメータを返す場合、または名前が呼び出し側に必要なアクションを明確にする場合、結果パラメータに名前を付ける:

```go
// 良い例:
func (n *Node) Children() (left, right *Node, err error)

// WithTimeout は返されるキャンセル関数の要件をドキュメント化する:
func WithTimeout(parent Context, d time.Duration) (ctx Context, cancel func())
```

繰り返しを引き起こしたり、素の return を不適切に有効にする名前付き結果を避ける。明確さは行数の節約に勝る。

### パッケージコメント

パッケージコメントは package 節の直前に置く（空行なし）:

```go
// 良い例:
// Package math provides basic constants and mathematical functions.
package math
```

パッケージごとに1つのコメント。`main` パッケージの場合、BUILD ファイルからバイナリ名を付ける:

```go
// 良い例:
// The seed_generator command generates a Finch seed file from JSON configs.
package main
```

代替スタイル: `Binary seed_generator ...`、`Command seed_generator ...`、`Program seed_generator ...`

## インポート

### インポートのリネーム

一般的にインポートのリネームを避ける。衝突を避けるために必要な場合（ローカル/プロジェクト固有のインポートをリネームすることを優先）、または生成された proto パッケージからアンダースコアを除去する場合にリネームする:

```go
// 良い例:
import (
    foosvcpb "path/to/package/foo_service_go_proto"
)
```

情報のないサードパーティパッケージ（`util`、`v1`）を控えめにリネームする:

```go
// 良い例:
import (
    core "github.com/kubernetes/api/core/v1"
)
```

### インポートのグループ化

インポートを4つのグループに分けて順序付ける:

1. 標準ライブラリ
2. プロジェクト/ベンダーパッケージ
3. Protocol Buffer インポート
4. 副作用インポート

```go
// 良い例:
import (
    "fmt"
    "os"

    "github.com/dsnet/compress/flate"
    "google.golang.org/protobuf/proto"

    foopb "myproj/foo/proto/proto"

    _ "myproj/rpc/protocols/dial"
)
```

### ブランクインポート

`import _` は main パッケージとテストに限定する。例外: nogo チェックのバイパスまたは `//go:embed` の使用。依存関係を制御するためにライブラリパッケージでは避ける。

### ドットインポート

`import .` 構文を使用しない。シンボルの出所が不明瞭になる。常にインポートされた名前を修飾する。

## エラー

### エラーを返す

潜在的な失敗を知らせるために、最後の結果パラメータとして `error` を使用する。成功時には `nil` を返す:

```go
// 良い例:
func Good() error { /* ... */ }
func GoodLookup() (*Result, error) { /* ... */ }
```

エラーを返すエクスポートされた関数は、具象型ではなく `error` 型を使用すべきである（具象 `nil` ポインタのラッピングバグを避けるため）。

### エラー文字列

エラー文字列は大文字で始めず（固有名詞/頭字語を除く）、句読点で終わらない。通常、他のコンテキスト内に表示されるためである:

```go
// 良い例:
err := fmt.Errorf("something bad happened")

// ログのコンテキストは大文字で始めてよい:
log.Errorf("Operation failed: %v", err)
```

### エラーの処理

エラーを意図的に処理する — 即座に処理するか、呼び出し側に返すか、まれに `log.Fatal` または `panic` を呼び出す。理由を説明せずに `_` でエラーを破棄しない:

```go
// 良い例:
n, _ := b.Write(p) // 非 nil エラーを返さない
```

### インバンドエラー

エラーを知らせるために特別な値（-1、null、空文字列）を返すことを避ける。複数の戻り値を使用する:

```go
// 悪い例:
func Lookup(key string) int // 失敗時に -1 を返す

// 良い例:
func Lookup(key string) (value string, ok bool)
```

### エラーフローのインデント

エラーを早期に処理し、`if` ブロックの後に通常のコードを続け、ネストした `else` を避ける:

```go
// 良い例:
if err != nil {
    // エラー処理
    return
}
// 通常のコード

// 悪い例:
if err != nil {
    // エラー処理
} else {
    // 通常のコードが不格好にインデントされる
}
```

## 言語

### リテラルのフォーマット

#### フィールド名

外部パッケージ型の構造体リテラルはフィールド名を指定する必要がある:

```go
// 良い例:
r := csv.Reader{
    Comma: ',',
    Comment: '#',
}

// 悪い例:
r := csv.Reader{',', '#', 4, false}
```

パッケージローカル型はオプションだが、明確さのために推奨される。

#### 対応するブレース

閉じブレースは開きブレースのインデントに揃える。複数行リテラルは閉じブレースを独自の行に置き、末尾カンマを付ける:

```go
// 良い例:
good := []*Type{{Key: "value"}}

good := []*Type{
    {Key: "multi"},
    {Key: "line"},
}

// 悪い例:
bad := []*Type{
    {Key: "multi"},
    {Key: "line"}}
```

#### くっついたブレース

インデントが一致し、内部の値がリテラル/proto ビルダーの場合のみブレースをくっつける:

```go
// 良い例:
good := []*Type{{ // 正しくくっついている
    Field: "value",
}, {
    Field: "value",
}}
```

#### 繰り返される型名

スライス/マップリテラルで繰り返される型名を省略する:

```go
// 良い例:
good := []*Type{
    {A: 42},
    {A: 43},
}

// 悪い例:
repetitive := []*Type{
    &Type{A: 42},
    &Type{A: 43},
}
```

#### ゼロ値フィールド

明確さが失われない場合、ゼロ値フィールドを省略する:

```go
// 良い例:
ldb := leveldb.Open("/table", &db.Options{
    BlockSize: 1<<16,
    ErrorIfDBExists: true,
})
```

### nil スライス

ローカル変数には、呼び出し側のバグを減らすために `nil` 初期化を優先する:

```go
// 良い例:
var t []string

// 悪い例:
t := []string{}
```

`nil` と空のスライスの区別を強制しない API を設計する。`== nil` ではなく `len()` チェックを使用する。

### インデントの混乱

インデントされたコードブロックと揃う改行を避ける。避けられない場合、それらを分離するスペースを残す。

### 関数のフォーマット

インデントの混乱を避けるため、関数シグネチャを1行に保つ:

```go
// 悪い例:
func (r *SomeType) SomeLongFunctionName(foo1, foo2 string,
    foo3, foo4 int) { // 関数本体のように見える
    foo5 := bar(foo1)
}
```

呼び出しを短くするためにローカル変数を抽出する。特定の引数へのインラインコメントを追加しない。代わりにオプション構造体を使用する。

### 条件分岐とループ

`if` 文の改行を避ける。ブール演算子を抽出する:

```go
// 良い例:
inTransaction := db.CurrentStatusIs(db.InTransaction)
keysMatch := db.ValuesEqual(db.TransactionKey(), row.Key())
if inTransaction && keysMatch {
    return db.Error(...)
}

// 悪い例:
if db.CurrentStatusIs(db.InTransaction) &&
    db.ValuesEqual(db.TransactionKey(), row.Key()) {
    return db.Error(...)
}
```

インデントの混乱を避けるためにブレースが一致することを確認する。`switch` と `case` を1行に保つ。過度に長い場合はすべての case をインデントする。

### コピー

同期オブジェクト（`sync.Mutex` など）や最適化配列を含む構造体をコピーしない。メソッドがポインタ型 `*T` に関連付けられている場合、値をコピーしない:

```go
// 悪い例:
b1 := bytes.Buffer{}
b2 := b1 // エイリアスされた内部でコピーを作成
```

### panic しない

通常のエラー処理には `error` と複数の戻り値を使用する。`package main` と初期化コード内では、終了エラーに `log.Exit` を検討する。レビュー/テスト中に発見された「不可能な」バグには `panic` を予約する。

### Must 関数

`MustXYZ` 命名規約に従うセットアップヘルパーは、ユーザー入力ではなく、起動時の早期にのみ呼び出すべきである:

```go
// 良い例:
func MustParse(version string) *Version {
    v, err := Parse(version)
    if err != nil {
        panic(fmt.Sprintf("MustParse(%q) failed: %v", version, err))
    }
    return v
}

var DefaultVersion = MustParse("1.2.3")
```

### goroutine のライフタイム

goroutine の終了条件を明確にする。従来の管理には `context.Context` を使用する:

```go
// 良い例:
func (w *Worker) Run(ctx context.Context) error {
    var wg sync.WaitGroup
    for item := range w.q {
        wg.Add(1)
        go func() {
            defer wg.Done()
            process(ctx, item)
        }()
    }
    wg.Wait() // goroutine が関数より長生きするのを防ぐ
}
```

goroutine がいつ/なぜ終了するかをドキュメント化する。goroutine を無期限に稼働中のまま放置しない。

### インターフェース

インターフェースは実装パッケージではなく、消費パッケージに属する。関数からは具象型を返す。テストダブル実装をエクスポートしない。実際の実装の公開 API を通じてテスト可能な API を設計する。使用前にインターフェースを定義しない。まず現実的な例を使用する。

```go
// 良い例:
package consumer
type Thinger interface { Thing() bool }
func Foo(t Thinger) string { ... }

// テストでは良い例:
type fakeThinger struct{ ... }
func (t fakeThinger) Thing() bool { ... }

// 悪い例:
package producer
type Thinger interface { Thing() bool }
func NewThinger() Thinger { ... }
```

### ジェネリクス

ジェネリクスはビジネス要件を満たす場合に使用する。早すぎる使用やドメイン固有言語の作成を避ける。具象型から始め、必要に応じて後からポリモーフィズムを追加する。インターフェースで十分な場合、過度な型スイッチを伴う `any` 型を使用しない。

### 値を渡す

バイトを節約するためだけにポインタを渡さない。関数が `*x` を読むだけなら、値で渡す。例外: 大きな構造体と protocol buffer メッセージ（ポインタで渡す）。

### レシーバの型

速度ではなく正確さに基づいて選択する。以下の場合にポインタを使用する:

- メソッドがレシーバを変更する必要がある
- レシーバにコピー不可のフィールド（`sync.Mutex`）が含まれる
- レシーバが大きい
- メソッドが可視性が重要な場所でレシーバを変更する
- レシーバがポインタフィールドを含む構造体である

以下の場合に値を使用する:

- スライス（再スライス/再割り当てしない場合）
- 変更されない組み込み型
- 単純なデータ型

型ごとに一貫したすべて値またはすべてポインタのメソッドを優先する。

### `switch` と `break`

冗長な `break` 文を使用しない。Go の `switch` は自動的に break する。空の句にはコメントを使用する。囲むループを抜けるにはラベル付き `break` を使用する。

### 同期関数

結果を直接返す同期関数を優先する。呼び出し側は別の goroutine で呼び出すことで並行性を追加できる。同期関数は推論とテストを簡素化する。

### 型エイリアス

新しい型には型定義（`type T1 T2`）を使用する。型エイリアス（`type T1 = T2`）は移行用に予約する。まれである。

### %q を使用する

読みやすい文字列出力には `%q` フォーマットを優先する:

```go
// 良い例:
fmt.Printf("value %q looks like text", someText)

// 悪い例:
fmt.Printf("value \"%s\" looks like text", someText)
```

### any を使用する

Go 1.18 以降では `any` が `interface{}` のエイリアスとして提供される。新しいコードでは `any` を優先する。

## 共通ライブラリ

### フラグ

Google 内部コードはカスタム `flag` パッケージバリアントを使用する。フラグ名は snake_case を使用する。変数は MixedCaps を使用する:

```go
// 良い例:
var (
    pollInterval = flag.Duration("poll_interval", time.Minute, "Polling interval.")
)
```

フラグは `package main` でのみ定義する。汎用パッケージは CLI フラグではなく API を通じて設定する。

### ロギング

Google のコードベースはカスタム `log` パッケージバリアント（オープンソース: `glog`）を使用する。スタックトレース付きの異常終了には `log.Fatal` を使用する。スタックトレースなしには `log.Exit`。`log.Panic` は存在しない。フォーマットが不要な場合は非フォーマットバージョンを優先する。

### コンテキスト

`context.Context` は認証情報、トレース、デッドライン、キャンセルを運ぶ。常に最初のパラメータとして渡す:

```go
func F(ctx context.Context /* その他 */) {}
```

例外:

- HTTP ハンドラ: `req.Context()` を使用
- ストリーミング RPC: ストリームのコンテキストを使用
- エントリポイント: `context.Background()` または `tb.Context()` を使用

構造体にコンテキストフィールドを追加しない。パラメータとして渡す。カスタムコンテキスト型を作成しない — 標準の `context.Context` のみを使用する。

### crypto/rand

キーには絶対に `math/rand` を使用しない。`crypto/rand` を使用する:

```go
// 良い例:
import "crypto/rand"
func Key() string {
    buf := make([]byte, 16)
    if _, err := rand.Read(buf); err != nil {
        log.Fatalf("Randomness failed: %v", err)
    }
    return fmt.Sprintf("%x", buf)
}
```

## 有用なテスト失敗

テストはソースを読まずに失敗を診断できるべきである。以下を含める:

- 失敗の原因
- エラーを生成した入力
- 実際の結果
- 期待される結果

### アサーションライブラリを避ける

検証と失敗メッセージを組み合わせるアサーションヘルパーを作成しない。それらは体験を分断し、関連するコンテキストを省略する:

```go
// 良い例: 直接比較
if !cmp.Equal(got, want) {
    t.Errorf("Blog() = %v, want %v", got, want)
}

// 悪い例: アサーションライブラリ
assert.StringEq(t, "obj.Type", obj.Type, "blogPost")
```

代わりに `cmp` や `fmt` のような標準ライブラリを使用する。

### 関数を特定する

失敗に関数名を含める: `got %v, want %v` ではなく `YourFunc(%v) = %v, want %v`。

### 入力を特定する

短い場合は入力を含める。大きい/不透明な入力には説明的なテストケース名を使用する。

### Got を Want より先に

実際の値を期待される値より先に表示する。標準フォーマット: `YourFunc(%v) = %v, want %v`。diff には明示的な方向指示子を含める。

### 完全な構造体の比較

深い比較を使用してデータ構造全体を直接比較する:

```go
// 良い例:
want := &Doc{Type: "post", Comments: 2}
if !cmp.Equal(got, want) {
    t.Errorf("AddPost() = %+v, want %+v", got, want)
}
```

近似等価性や比較不可能なフィールドには、`cmpopts` オプション付きの `cmp.Diff` を使用する。

### 安定した結果を比較する

不安定なパッケージ動作に依存する出力の比較を避ける。フォーマットされた文字列/シリアライズされたバイトには、代わりにセマンティックな等価性を比較する:

```go
// 良い例: パースして構造体を比較
var got, want map[string]interface{}
json.Unmarshal(gotBytes, &got)
json.Unmarshal(wantBytes, &want)
if !reflect.DeepEqual(got, want) {
    t.Errorf(...)
}
```

### 続行する

失敗後もテストを続行するには `t.Error` を使用し、1回の実行ですべての問題を表示する。後続のテストが無意味な場合のみ `t.Fatal` を呼び出す:

```go
// 良い例: 複数のエラーを報告
if diff := cmp.Diff(wantMean, gotMean); diff != "" {
    t.Errorf("Mean diff: %s", diff)
}
if diff := cmp.Diff(wantVariance, gotVariance); diff != "" {
    t.Errorf("Variance diff: %s", diff)
}

// 良い例: Fatal により後続のテストが無意味になる
if gotEncoded != wantEncoded {
    t.Fatalf("Encode failed: got %q, want %q", gotEncoded, wantEncoded)
}
```

テーブル駆動テストでは、`t.Error` + `continue` ではなく `t.Fatal` 付きのサブテストを検討する。

---

**ドキュメントのステータス:** これはコアスタイルガイドに従属する規範的だが非カノニカルなドキュメントである。時間とともに成長し、ガイドと矛盾する場合は更新されるべきである。
