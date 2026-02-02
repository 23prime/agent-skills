# 制御構造

Goの制御構造はCのものと関連しているが、重要な点で異なる。`do`や`while`ループは存在せず、やや一般化された`for`のみがある。`switch`はより柔軟である。`if`と`switch`は`for`のようなオプションの初期化文を受け入れる。`break`と`continue`文はオプションのラベルを取り、何をbreakまたはcontinueするかを識別できる。そして、型switchや多方向通信マルチプレクサである`select`を含む新しい制御構造がある。構文もやや異なる。括弧は不要で、本体は常に中括弧で区切られなければならない。

## If

Goでは、シンプルな`if`は次のようになる。

```go
if x > 0 {
    return y
}
```

必須の中括弧は、シンプルな`if`文を複数行で書くことを促進する。特に本体が`return`や`break`のような制御文を含む場合は、そうすることが良いスタイルである。

`if`と`switch`は初期化文を受け入れるため、ローカル変数を設定するために使用されるのをよく見かける。

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

これは、コードが一連のエラー条件に対してガードしなければならない一般的な状況の例である。コードは、制御の成功フローがページを下に流れ、発生したエラーケースを排除する場合にうまく読める。エラーケースは`return`文で終わる傾向があるため、結果のコードには`else`文は不要である。

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

## 再宣言と再代入

余談である。前のセクションの最後の例は、`:=`短縮宣言形式がどのように機能するかの詳細を示している。`os.Open`を呼び出す宣言は次のように読む。

```go
f, err := os.Open(name)
```

この文は2つの変数`f`と`err`を宣言する。数行後、`f.Stat`への呼び出しは次のように読む。

```go
d, err := f.Stat()
```

これは`d`と`err`を宣言しているように見える。しかし、`err`が両方の文に現れていることに注意してほしい。この重複は合法である。`err`は最初の文で宣言されているが、2番目では*再代入*されているだけである。これは、`f.Stat`への呼び出しが上で宣言された既存の`err`変数を使用し、単にそれに新しい値を与えるだけであることを意味する。

`:=`宣言において、変数`v`はすでに宣言されていても現れることができる。ただし次の条件を満たす必要がある。

- この宣言が`v`の既存の宣言と同じスコープ内にある（`v`が外側のスコープですでに宣言されている場合、宣言は新しい変数を作成する）
- 初期化における対応する値が`v`に代入可能である
- 宣言によって作成される他の変数が少なくとも1つある

この珍しい特性は純粋なプラグマティズムであり、例えば長い`if-else`チェーンで単一の`err`値を使用することを容易にする。これがよく使われているのを目にするだろう。

ここで注目に値するのは、Goでは関数パラメータと戻り値のスコープが関数本体と同じであることである。たとえそれらが本体を囲む中括弧の外側に字句的に現れていてもである。

## For

Goの`for`ループはCのものと似ているが、同じではない。それは`for`と`while`を統一しており、`do-while`は存在しない。3つの形式があり、そのうち1つだけがセミコロンを持つ。

```go
// C の for と同様
for init; condition; post { }

// C の while と同様
for condition { }

// C の for(;;) と同様
for { }
```

短縮宣言は、インデックス変数をループ内で直接宣言することを容易にする。

```go
sum := 0
for i := 0; i < 10; i++ {
    sum += i
}
```

配列、スライス、文字列、またはマップをループする場合、またはチャネルから読み取る場合、`range`節がループを管理できる。

```go
for key, value := range oldMap {
    newMap[key] = value
}
```

range内の最初の項目（キーまたはインデックス）のみが必要な場合は、2番目を削除する。

```go
for key := range m {
    if key.expired() {
        delete(m, key)
    }
}
```

range内の2番目の項目（値）のみが必要な場合は、*空白識別子*であるアンダースコアを使用して最初を破棄する。

```go
sum := 0
for _, value := range array {
    sum += value
}
```

文字列の場合、`range`はより多くの作業を行い、UTF-8を解析して個々のUnicodeコードポイントを抽出する。誤ったエンコーディングは1バイトを消費し、置換runeであるU+FFFDを生成する。（関連する組み込み型を持つ名前`rune`は、単一のUnicodeコードポイントに対するGo用語である。詳細は[言語仕様](https://go.dev/ref/spec#Rune_literals)を参照。）次のループは

```go
for pos, char := range "日本\x80語" { // \x80 is an illegal UTF-8 encoding
    fmt.Printf("character %#U starts at byte position %d\n", char, pos)
}
```

次のように出力する。

```text
character U+65E5 '日' starts at byte position 0
character U+672C '本' starts at byte position 3
character U+FFFD '�' starts at byte position 6
character U+8A9E '語' starts at byte position 7
```

最後に、Goにはカンマ演算子がなく、`++`と`--`は式ではなく文である。したがって、`for`で複数の変数を実行したい場合は、並列代入を使用する必要がある（ただし、それは`++`と`--`を排除する）。

```go
// a を逆順にする
for i, j := 0, len(a)-1; i < j; i, j = i+1, j-1 {
    a[i], a[j] = a[j], a[i]
}
```

## Switch

Goの`switch`はCのものより一般的である。式は定数や整数である必要はなく、caseは一致が見つかるまで上から下へ評価され、`switch`が式を持たない場合は`true`でスイッチする。したがって、`if`-`else`-`if`-`else`チェーンを`switch`として書くことが可能であり、慣用的である。

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

Goでは他のCライクな言語ほど一般的ではないが、`break`文を使用して`switch`を早期に終了できる。しかし、時には周囲のループを抜ける必要があり、switchではない。Goでは、ループにラベルを付けてそのラベルに"breaking"することでこれを達成できる。この例は両方の使用法を示している。

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

もちろん、`continue`文もオプションのラベルを受け入れるが、それはループにのみ適用される。

このセクションを締めくくるために、2つの`switch`文を使用するバイトスライスの比較ルーチンを示す。

```go
// Compare は2つのバイトスライスを辞書順で比較し、整数を返す。
// 結果は a == b なら 0、a < b なら -1、a > b なら +1 となる。
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

## 型switch

switchは、インターフェース変数の動的型を発見するためにも使用できる。そのような*型switch*は、括弧内にキーワード`type`を持つ型アサーションの構文を使用する。switchが式内で変数を宣言する場合、変数は各節で対応する型を持つ。また、そのような場合に名前を再利用することも慣用的であり、実際には各caseで同じ名前だが異なる型の新しい変数を宣言している。

```go
var t interface{}
t = functionOfSomeType()
switch t := t.(type) {
default:
    fmt.Printf("unexpected type %T\n", t)     // %T は t の型を出力する
case bool:
    fmt.Printf("boolean %t\n", t)             // t は bool 型
case int:
    fmt.Printf("integer %d\n", t)             // t は int 型
case *bool:
    fmt.Printf("pointer to boolean %t\n", *t) // t は *bool 型
case *int:
    fmt.Printf("pointer to integer %d\n", *t) // t は *int 型
}
```
