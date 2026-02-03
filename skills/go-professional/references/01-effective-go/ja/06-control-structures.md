# Control structures

Goの制御構造はCのものと関連しているが、重要な点で異なる。`do`や`while`ループは存在せず、やや一般化された`for`のみである。`switch`はより柔軟である。`if`と`switch`は`for`と同様にオプションの初期化文を受け付ける。`break`と`continue`文は、何をbreakまたはcontinueするかを識別するためのオプションのラベルを取る。そして、type switchや多方向通信マルチプレクサである`select`を含む新しい制御構造がある。構文も若干異なる。括弧は不要で、本体は常に中括弧で区切らなければならない。

## If

Goでは単純な`if`は次のようになる。

```go
if x > 0 {
    return y
}
```

中括弧の使用が必須であることで、`if`文を複数行で書くことが推奨される。いずれにせよそうするのは良いスタイルである。特に本体に`return`や`break`のような制御文が含まれる場合はなおさらだ。

`if`と`switch`は初期化文を受け付けるため、ローカル変数を設定するために使われるのをよく見かける。

```go
if err := file.Chmod(0664); err != nil {
    log.Print(err)
    return err
}
```

Goのライブラリでは、`if`文が次の文に流れない場合、つまり本体が`break`、`continue`、`goto`、または`return`で終わる場合、不要な`else`が省略されていることがわかる。

```go
f, err := os.Open(name)
if err != nil {
    return err
}
codeUsing(f)
```

これは、コードが一連のエラー条件を防御しなければならない一般的な状況の例である。成功した制御フローがページを下に流れ、エラーケースを発生時に排除していく場合、コードは読みやすくなる。エラーケースは`return`文で終わる傾向があるため、結果としてのコードには`else`文が不要になる。

```go
f, err := os.Open(name)
if err != nil {
    return err
}
d, err := f.Stat()
if err != nil {
    f.Close()
    return err
}
codeUsing(f, d)
```

## Redeclaration and reassignment

余談だが、前のセクションの最後の例は、`:=`短縮宣言形式がどのように機能するかの詳細を示している。`os.Open`を呼び出す宣言は、

```go
f, err := os.Open(name)
```

と読める。この文は2つの変数`f`と`err`を宣言する。数行後、`f.Stat`の呼び出しは、

```go
d, err := f.Stat()
```

と読めるが、これは`d`と`err`を宣言しているように見える。しかし、`err`が両方の文に現れていることに注意してほしい。この重複は合法である。`err`は最初の文で宣言されているが、2番目の文では単に再代入されているだけである。これは、`f.Stat`の呼び出しが、上で宣言された既存の`err`変数を使用し、単に新しい値を与えているだけであることを意味する。

`:=`宣言において、変数`v`は既に宣言されている場合でも現れることができる。ただし、

- この宣言が`v`の既存の宣言と同じスコープにあること（`v`が外側のスコープで既に宣言されている場合、宣言は新しい変数を作成する）
- 初期化における対応する値が`v`に代入可能であること
- 宣言によって作成される他の変数が少なくとも1つあること

が条件である。

この珍しい性質は純粋に実用主義であり、例えば長い`if-else`チェーンで単一の`err`値を使うことを容易にする。これはよく使われているのを目にするだろう。

ここで、Goでは関数パラメータと戻り値のスコープは、本体を囲む中括弧の外側に字句的に現れても、関数本体と同じであることに注意する価値がある。

## For

Goの`for`ループはCのものと似ているが、同じではない。`for`と`while`を統一しており、`do-while`は存在しない。3つの形式があり、そのうちの1つだけがセミコロンを持つ。

```go
// Cのforのような
for init; condition; post { }

// Cのwhileのような
for condition { }

// Cのfor(;;)のような
for { }
```

短縮宣言により、ループ内でインデックス変数を簡単に宣言できる。

```go
sum := 0
for i := 0; i < 10; i++ {
    sum += i
}
```

array、slice、string、またはmapをループする場合、あるいはchannelから読み取る場合、`range`句がループを管理できる。

```go
for key, value := range oldMap {
    newMap[key] = value
}
```

range内の最初の項目（keyまたはindex）だけが必要な場合は、2番目を削除する。

```go
for key := range m {
    if key.expired() {
        delete(m, key)
    }
}
```

range内の2番目の項目（value）だけが必要な場合は、ブランク識別子であるアンダースコアを使って最初を破棄する。

```go
sum := 0
for _, value := range array {
    sum += value
}
```

stringの場合、`range`はUTF-8を解析して個々のUnicodeコードポイントを分解し、より多くの作業を行う。誤ったエンコーディングは1バイトを消費し、置換rune U+FFFDを生成する。（関連する組み込み型を持つ名前`rune`は、単一のUnicodeコードポイントを表すGo用語である。詳細は[言語仕様](https://go.dev/ref/spec#Rune_literals)を参照。）次のループ

```go
for pos, char := range "日本\x80語" { // \x80は不正なUTF-8エンコーディング
    fmt.Printf("character %#U starts at byte position %d\n", char, pos)
}
```

は、次を出力する。

```text
character U+65E5 '日' starts at byte position 0
character U+672C '本' starts at byte position 3
character U+FFFD '�' starts at byte position 6
character U+8A9E '語' starts at byte position 7
```

最後に、Goにはカンマ演算子がなく、`++`と`--`は式ではなく文である。したがって、`for`で複数の変数を実行したい場合は、並列代入を使用する必要がある（ただし、これは`++`と`--`を排除する）。

```go
// aを反転する
for i, j := 0, len(a)-1; i < j; i, j = i+1, j-1 {
    a[i], a[j] = a[j], a[i]
}
```

## Switch

Goの`switch`はCのものよりも一般的である。式は定数や整数である必要はなく、caseは一致が見つかるまで上から下に評価され、`switch`が式を持たない場合は`true`でswitchする。したがって、`if`-`else`-`if`-`else`チェーンを`switch`として書くことが可能であり、慣用的である。

```go
func unhex(c byte) byte {
    switch {
    case '0' <= c && c <= '9':
        return c - '0'
    case 'a' <= c && c <= 'f':
        return c - 'a' + 10
    case 'A' <= c && c <= 'F':
        return c - 'A' + 10
    }
    return 0
}
```

自動的なフォールスルーはないが、caseはカンマ区切りのリストで提示できる。

```go
func shouldEscape(c byte) bool {
    switch c {
    case ' ', '?', '&', '=', '#', '+', '%':
        return true
    }
    return false
}
```

他のCライクな言語ほどGoでは一般的ではないが、`break`文を使用して`switch`を早期に終了できる。しかし、時には、switchではなく、囲んでいるループから抜け出す必要がある。Goでは、ループにラベルを付けてそのラベルに「break」することでこれを実現できる。この例は両方の使用法を示している。

```go
Loop:
    for n := 0; n < len(src); n += size {
        switch {
        case src[n] < sizeOne:
            if validateOnly {
                break
            }
            size = 1
            update(src[n])

        case src[n] < sizeTwo:
            if n+1 >= len(src) {
                err = errShortInput
                break Loop
            }
            if validateOnly {
                break
            }
            size = 2
            update(src[n] + src[n+1]<<shift)
        }
    }
```

もちろん、`continue`文もオプションのラベルを受け付けるが、これはループにのみ適用される。

このセクションを締めくくるために、2つの`switch`文を使用したbyte sliceの比較ルーチンを示す。

```go
// Compareは2つのbyte sliceを辞書順に比較し、
// 整数を返す。
// 結果はa == bの場合0、a < bの場合-1、a > bの場合+1となる
func Compare(a, b []byte) int {
    for i := 0; i < len(a) && i < len(b); i++ {
        switch {
        case a[i] > b[i]:
            return 1
        case a[i] < b[i]:
            return -1
        }
    }
    switch {
    case len(a) > len(b):
        return 1
    case len(a) < len(b):
        return -1
    }
    return 0
}
```

## Type switch

switchは、interface変数の動的型を発見するためにも使用できる。このようなtype switchは、括弧内にキーワード`type`を含む型アサーションの構文を使用する。switchが式内で変数を宣言する場合、変数は各句で対応する型を持つ。また、このような場合に名前を再利用することも慣用的であり、事実上、各caseで同じ名前だが異なる型の新しい変数を宣言している。

```go
var t interface{}
t = functionOfSomeType()
switch t := t.(type) {
default:
    fmt.Printf("unexpected type %T\n", t)     // %Tはtが持つ型を出力する
case bool:
    fmt.Printf("boolean %t\n", t)             // tはbool型
case int:
    fmt.Printf("integer %d\n", t)             // tはint型
case *bool:
    fmt.Printf("pointer to boolean %t\n", *t) // tは*bool型
case *int:
    fmt.Printf("pointer to integer %d\n", *t) // tは*int型
}
```
