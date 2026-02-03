# Google Go スタイルベストプラクティス

本ドキュメントは、一般的なシナリオにおいて Go スタイルを効果的に適用するためのガイダンスを提供する。コアスタイルガイドを補完するものであり、規範的でもカノニカルでもない。

## 命名

### 関数とメソッドの名前

#### 繰り返しを避ける

関数やメソッドの命名時には、呼び出し側のコンテキストを考慮する。主な推奨事項:

- 曖昧でない場合、入出力の型を省略する
- 関数シグネチャでパッケージ名を繰り返さない
- メソッド名でレシーバの型名を繰り返さない
- 関数の識別で変数パラメータ名をスキップする
- 命名から戻り値の型を除外する

**例:**

```go
// 悪い例:
package yamlconfig
func ParseYAMLConfig(input string) (*Config, error)

// 良い例:
package yamlconfig
func Parse(input string) (*Config, error)
```

複数の類似関数のために必要な場合のみ、曖昧さを解消する情報を使用する。

#### 命名規約

- **名詞的な名前** — 値を返す関数: 「`Get` プレフィックスを避ける」
- **動詞的な名前** — アクションを実行する関数
- **型サフィックス** — 型のみが異なる同一関数: `ParseInt`、`ParseInt64`

### テストダブルとヘルパーパッケージ

テストヘルパーのパッケージ名には `test` を追加する（例: `creditcardtest`）。1つのテストダブル型を持つ単純なケースでは、簡潔な命名を使用する:

```go
// 良い例:
type Stub struct{}
func (Stub) Charge(*creditcard.Card, money.Money) error { return nil }
```

複数の動作がある場合、動作に応じて命名する:

```go
// 良い例:
type AlwaysCharges struct{}
type AlwaysDeclines struct{}
```

テストコードでは、本番の型と区別するために変数にプレフィックスを付ける:

```go
// 良い例:
var spyCC creditcardtest.Spy
```

### シャドウイング

**スタンピング**は `:=` で新しい変数が作成されない場合に発生する。元の値が不要になった場合、これは許容される。

**シャドウイング**は新しいスコープで新しい変数を導入する。元の変数はブロック終了後にアクセス不能になる。

```go
// 良い例 - スタンピング:
ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
defer cancel()

// 悪い例 - シャドウイングバグ:
if *shortenDeadlines {
    ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
    defer cancel()
}
// バグ: ここの ctx は呼び出し側のコンテキストに戻る
```

標準パッケージ名のシャドウイングを避ける。それらの関数へのアクセスが妨げられる。

### Util パッケージ

パッケージ名は提供する機能に関連すべきである。`util`、`helper`、`common` のような名前は情報がなく、インポートの衝突を引き起こすため、不適切な選択である。

呼び出し側を考慮する:

```go
// 良い例:
db := spannertest.NewDatabaseFromFile(...)

// 悪い例:
db := test.NewDatabaseFromFile(...)
```

## パッケージサイズ

主な考慮事項:

- **Godoc の可視性**: ユーザーはパッケージごとに1ページを見て、メソッドは型ごとにグループ化される
- **実装の結合**: 密結合の型を一緒に配置して、非エクスポート識別子にアクセスできるようにする
- **ユーザーの利便性**: ユーザーが意味のある形で両方のパッケージをインポートする必要がある場合、それらを統合する
- **厳密な制限なし**: Go スタイルは柔軟である。ファイルごとに数千行や過度に小さなファイルを避ける

ファイルはコードを容易に見つけられるほど焦点を絞るべきである。標準ライブラリは良い階層化パターンを示している（例: `net/http` は関心事で整理: client.go、server.go、cookie.go）。

## インポート

### Protocol Buffer メッセージとスタブ

従来のサフィックスを使用する:

- `go_proto_library` ルールには `pb`
- `go_grpc_library` ルールには `grpc`

```go
// 良い例:
import (
    foopb "path/to/package/foo_service_go_proto"
    foogrpc "path/to/package/foo_service_go_grpc"
)
```

非常に短い略語よりも説明的な名前を優先する。不明な場合は `pb` サフィックス付きの proto パッケージ名を使用する。

## エラー処理

### エラー構造

プログラムによるエラー調査のための構造を提供する:

```go
// 良い例:
var (
    ErrDuplicate = errors.New("duplicate")
    ErrMarsupial = errors.New("marsupials not supported")
)

func process(animal Animal) error {
    switch {
    case seen[animal]:
        return ErrDuplicate
    case marsupial(animal):
        return ErrMarsupial
    }
    return nil
}
```

文字列マッチングではなく、ラップされたエラーに対して `errors.Is()` を使用する。

### エラーへの情報追加

基になるエラーに既に含まれている冗長な情報を避ける:

```go
// 良い例:
if err := os.Open("settings.txt"); err != nil {
    return fmt.Errorf("launch codes unavailable: %v", err)
}
// 出力: launch codes unavailable: open settings.txt: no such file...

// 悪い例:
return fmt.Errorf("could not open settings.txt: %v", err)
// 既に存在するパス情報を重複させている
```

#### エラーラッピングにおける `%v` vs. `%w`

- **`%v` を使用**: 単純なアノテーション、ログ表示、またはシステム境界（RPC/IPC）でのエラー変換
- **`%w` を使用**: アプリケーションヘルパー内でのプログラム的検査。`errors.Is()` と `errors.As()` チェックを可能にする

```go
// 良い例 - エラーチェーンを保持:
if err != nil {
    return fmt.Errorf("couldn't find remote file: %w", err)
}
```

読みやすいエラーチェーンのために `%w` を末尾に配置することを優先する: `[...]: %w` フォーマット。

### エラーのロギング

- 重複を避ける。呼び出し側にログを取るかどうかを決定させる
- 診断情報とともに何が失敗したかを明確に表現する
- 個人を特定できる情報（PII）に注意する
- `log.Error` を控えめに使用する — フラッシュしてパフォーマンスに影響する
- ERROR レベルはアクション可能なメッセージのために予約する

開発トレースには異なるレベルで詳細ログ（`log.V`）を使用する（1 は最小限、2 はトレース、3 はダンプ）。

### プログラムの初期化

初期化エラーは `main` に伝播し、エラーの修正方法を説明するアクション可能なメッセージとともに `log.Exit` を呼び出すべきである。セットアップ失敗には `log.Fatal` を避ける。

### プログラムチェックと panic

戻り値による標準的なエラー処理が優先される。回復不能な不変条件違反が発生した場合のみ `log.Fatal` を呼び出す。

#### いつ panic するか

- **API の誤用**: `reflect` が無効なアクセスパターンで panic するように（スライスの範囲外アクセスに類似）
- **内部実装の詳細**: panic はパッケージ境界を越えてはならない。公開 API 境界で `defer` + `recover` を使用する

```go
// 良い例:
type syntaxError struct { msg string }

func Parse(in string) (_ *Node, err error) {
    defer func() {
        if p := recover(); p != nil {
            if sErr, ok := p.(*syntaxError); ok {
                err = fmt.Errorf("syntax error: %v", sErr.msg)
            } else {
                panic(p) // 予期しない panic を伝播
            }
        }
    }()
    // panic する可能性のある内部関数を呼び出すパースロジック
}
```

コンパイラが識別できない到達不能コードマーカーには panic が許容される。

## ドキュメント

### 規約

#### パラメータと設定

すべてのパラメータではなく、エラーが発生しやすいまたは明白でないフィールドをドキュメント化する:

```go
// 良い例:
// Sprintf はフォーマット指定子に従ってフォーマットし、結果の文字列を返す。
// 提供されたデータはフォーマットに補間される。データがフォーマット動詞と
// 一致しない場合、フォーマットエラーセクションで説明されているように
// 警告が出力にインラインで含まれる。
func Sprintf(format string, data ...any) string

// 悪い例:
// format はフォーマットで、data は補間データである。（価値をほとんど追加しない）
```

#### コンテキスト

コンテキストのキャンセルは暗黙的である — 繰り返さない。特殊なケースをドキュメント化する:

```go
// 良い例 - 特殊な動作をドキュメント化:
// Run はコンテキストのキャンセルまたは Stop() が呼び出されるまで作業を処理する。
// コンテキストのキャンセルは非同期である。すべての作業が停止する前に Run が
// 返る可能性がある。
func (Worker) Run(ctx context.Context) error
```

#### 並行性

概念的に読み取り専用の操作は、ドキュメントなしで並行使用に安全であると仮定する。変更と並行性をドキュメント化する:

```go
// 良い例 - 非標準の動作をドキュメント化:
// Lookup はキャッシュされたデータを返す。この操作は並行使用に安全ではない。
// LRU キャッシュの内部がヒット時に変更されるためである。
func (*Cache) Lookup(key string) ([]byte, bool)
```

#### クリーンアップ

明示的なクリーンアップ要件をドキュメント化する:

```go
// 良い例:
// NewTicker は各 tick 後に時間を送信する Ticker を返す。
// 完了したら関連リソースを解放するために Stop を呼び出す。
func NewTicker(d Duration) *Ticker
```

#### エラー

呼び出し側が予想できる重要なエラーセンチネルをドキュメント化する:

```go
// 良い例:
// Read は読み取ったバイト数と発生したエラーを返す。
// ファイルの終わりでは、Read は 0, io.EOF を返す。
func (*File) Read(b []byte) (int, error)
```

正しい `errors.Is()` 比較のために、エラー型がポインタレシーバを使用するかどうかに注意する。

### Godoc のフォーマット

- 空行は段落を分離する
- 実行可能な例は `ExampleFunctionName()` テスト関数を通じてドキュメントに添付される
- 行を2つの追加スペースでインデントすると、逐語的なフォーマットになる
- 大文字の単一行テキストの後に段落が続くと、自動生成されたアンカー付きの見出しとしてフォーマットされる

### シグナルブースト

明白でない条件をコメントで強調する:

```go
// 良い例:
if err := doSomething(); err == nil { // エラーがない場合
    // ...
}
```

## 変数宣言

### 初期化

非ゼロ値の新しい変数には `:=` を優先する:

```go
// 良い例:
i := 42

// 悪い例:
var i = 42
```

### ゼロ値

空の、使用準備ができた状態を伝える場合、ゼロ値を使用して変数を宣言する:

```go
// 良い例:
var (
    coords Point
    magic  [4]byte
    primes []int
)

// 悪い例:
var coords = Point{X: 0, Y: 0}
```

アンマーシャリングの一般的なパターン:

```go
// 良い例:
var coords Point
if err := json.Unmarshal(data, &coords); err != nil {
```

### 複合リテラル

初期要素がわかっている場合、複合リテラルを使用する:

```go
// 良い例:
var captains = map[string]string{"Kirk": "James Tiberius", "Picard": "Jean-Luc"}
```

ゼロ値ポインタには、空の複合リテラルまたは `new()` のいずれかが機能する:

```go
// 良い例:
var buf = new(bytes.Buffer)
```

### サイズヒント

最終サイズがわかっている場合（例: map とスライスの間の変換）、事前割り当てする:

```go
// 良い例:
var seen = make(map[string]bool, shardSize)
```

ただし、ほとんどのコードは事前割り当てを必要としない。パフォーマンス分析が正当化しない限り、デフォルトでゼロ初期化を使用する。

**警告**: 過剰なメモリの事前割り当ては、フリート全体でリソースを浪費する。最適化前にベンチマークを行う。

### チャネルの方向

カジュアルなエラーを防ぐためにチャネルの方向を指定する:

```go
// 良い例:
func sum(values <-chan int) int {
    // ...
}

// 悪い例:
func sum(values chan int) (out int) {
    for v := range values {
        out += v
    }
    close(values) // 2回目の close で panic！
}
```

## 関数引数リスト

関数シグネチャが過度に複雑にならないようにする。パラメータ数が増えると、個々のパラメータの役割が不明確になり、隣接する同じ型のパラメータが混乱を招く。

### オプション構造体

オプションの引数を最後のパラメータとして渡される構造体に集める:

```go
// 良い例:
type ReplicationOptions struct {
    Config              *replicator.Config
    PrimaryRegions      []string
    ReadonlyRegions     []string
    ReplicateExisting   bool
    OverwritePolicies   bool
    ReplicationInterval time.Duration
    CopyWorkers         int
    HealthWatcher       health.Watcher
}

func EnableReplication(ctx context.Context, opts ReplicationOptions) {
    // ...
}

// 呼び出し:
storage.EnableReplication(ctx, storage.ReplicationOptions{
    Config:              config,
    PrimaryRegions:      []string{"us-east1", "us-central2"},
    OverwritePolicies:   true,
    ReplicationInterval: 1 * time.Hour,
})
```

**利点**: 自己ドキュメント化、デフォルトの省略、関数間で共有、呼び出しを壊さずに成長。

### 可変長オプション

相当な柔軟性のためにクロージャを返すエクスポートされたオプション関数を使用する:

```go
// 良い例:
type ReplicationOption func(*replicationOptions)

func ReadonlyCells(cells ...string) ReplicationOption {
    return func(opts *replicationOptions) {
        opts.readonlyCells = append(opts.readonlyCells, cells...)
    }
}

func EnableReplication(ctx context.Context, config *placer.Config,
    primaryCells []string, opts ...ReplicationOption) {
    var options replicationOptions
    for _, opt := range opts {
        opt(&options)
    }
}

// 呼び出し:
storage.EnableReplication(ctx, config, []string{"po", "is", "ea"},
    storage.ReadonlyCells("ix", "gg"),
    storage.OverwritePolicies(true),
)
```

**以下の場合に優先**: ほとんどの呼び出し側がオプションを指定しない、ほとんどのオプションがまれ、多くのオプションが存在する、オプションが引数を必要とする、またはユーザーがカスタムオプションを提供できる。

オプションは存在だけでなくパラメータを受け取るべきである（例: `rpc.EnableFailFast()` より `rpc.FailFast(enable bool)` を優先）。

## 複雑なコマンドラインインターフェース

サブコマンドを持つプログラムには、以下のライブラリがある:

- **[cobra](https://pkg.go.dev/github.com/spf13/cobra)**: Getopt 規約、多機能、Google 外で一般的
- **[subcommands](https://pkg.go.dev/github.com/google/subcommands)**: Go flag 規約、シンプル、デフォルトとして推奨

**警告**: cobra では、`context.Background` でルートコンテキストを作成するのではなく、`cmd.Context()` を使用してコンテキストを取得する。

サブコマンドは別のパッケージに存在する必要はない。標準的なパッケージ境界の考慮事項を適用する。

## テスト

### テスト関数にテストを任せる

Go はテストヘルパー（セットアップ/クリーンアップ）とアサーションヘルパー（正確性チェック）を区別する。アサーションヘルパーは[慣用的ではない](guide#assert)。

テストを失敗させる理想的な場所は、明確さのために `Test` 関数自体の中である。機能を抽出する場合、バリデーション関数は `testing.T` を直接呼び出すのではなく、値（通常は `error`）を返すべきである:

```go
// 良い例:
func polygonCmp() cmp.Option {
    return cmp.Options{
        cmp.Transformer("polygon", func(p *s2.Polygon) []*s2.Loop {
            return p.Loops()
        }),
        cmpopts.EquateApprox(0.00000001, 0),
    }
}

func TestFenceposts(t *testing.T) {
    got := Fencepost(tomsDiner, 1*meter)
    if diff := cmp.Diff(want, got, polygonCmp()); diff != "" {
        t.Errorf("Fencepost(tomsDiner, 1m) returned unexpected diff:\n%v", diff)
    }
}
```

### 拡張可能なバリデーション API の設計

**アクセプタンステスト**は、ライブラリ要件に対するユーザー実装型を検証する。テストパッケージを作成し、実装をブラックボックスとして実行する:

```go
// 良い例 - アクセプタンステスト:
func ExercisePlayer(b *chess.Board, p chess.Player) error
```

エラーを返して早期に失敗するか、実行時間の期待に応じてすべての失敗を集約する。

### 実際のトランスポートを使用する

HTTP/RPC とのコンポーネント統合をテストする場合、テストダブル（モック/スタブ/フェイク）バックエンドに接続する実際のトランスポートを使用する:

```go
// 良い例:
// テスト OperationsServer に接続された実際の OperationsClient を使用
client := longrunning.NewOperationsClient(testConn)
```

これにより、テストがクライアントを手動で実装するのではなく、可能な限り多くの実際のコードを使用することが保証される。

### `t.Error` vs. `t.Fatal`

一般的に、テストは最初の問題で中断すべきではない。`t.Fatal` を適切に使用する:

- **テストセットアップの失敗**: テストが実行できないセットアップ関数の失敗
- **ループ前のテーブル駆動テスト**: テスト全体に影響する失敗
- **`t.Run` サブテスト内**: サブテストを終了。テストは次のエントリに進む
- **サブテスト外の複数のテーブルエントリ**: `t.Error` + `continue` を使用してスキップ

**警告**: 別の goroutine から `t.Fatal` を呼び出すのは安全ではない（次のセクションを参照）。

### テストヘルパーでのエラー処理

テストヘルパーの失敗は、多くの場合、満たされていないセットアップ前提条件を示す。`Fatal` 関数を呼び出す:

```go
// 良い例:
func mustAddGameAssets(t *testing.T, dir string) {
    t.Helper()
    if err := os.WriteFile(path.Join(dir, "pak0.pak"), pak0, 0644);
        err != nil {
        t.Fatalf("Setup failed: could not write pak0 asset: %v", err)
    }
}
```

説明的な失敗メッセージを含める。テスト完了時に実行されるクリーンアップ関数を登録するには `t.Cleanup`（Go 1.14+）を使用する。

### 別の goroutine から `t.Fatal` を呼び出さない

テスト関数自体以外の goroutine から `t.FailNow`、`t.Fatal` などを呼び出すのは正しくない。代わりに `t.Error` + `return` を使用する:

```go
// 良い例:
go func() {
    defer wg.Done()
    if err := engine.Vroom(); err != nil {
        t.Errorf("No vroom left on engine: %v", err) // t.Fatalf ではない
        return
    }
}()
```

### 構造体リテラルでフィールド名を使用する

多くの行にわたるテーブル駆動テストや、隣接する同じ型のフィールドがある場合、フィールド名を指定する:

```go
// 良い例:
tests := []struct {
    slice     []string
    separator string
    skipEmpty bool
    want      string
}{
    {
        slice:     []string{"a", "b", ""},
        separator: ",",
        want:      "a,b,",
    },
    {
        slice:     []string{"a", "b", ""},
        separator: ",",
        skipEmpty: true,
        want:      "a,b",
    },
}
```

### セットアップコードのスコープを特定のテストに限定する

共有セットアップではなく、必要なテストでセットアップ関数を明示的に呼び出す:

```go
// 良い例:
func TestParseData(t *testing.T) {
    data := mustLoadDataset(t)
    parsed, err := ParseData(data)
    if err != nil {
        t.Fatalf("Unexpected error parsing data: %v", err)
    }
    // ...
}
```

---

**注意**: この要約は Google の Go スタイルベストプラクティスの核心的なガイダンスを捉えている。包括的なカバレッジと追加の例については、完全なドキュメントを参照すること。
