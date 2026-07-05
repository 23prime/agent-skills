---
name: decomposing-github-issue
description: GitHub Issue が複数の独立した関心事にまたがっており、単一 PR で実装するには大きすぎると感じるときに使用する。
translated_from: SKILL.md
---

# GitHub Issue の分解

大きな GitHub Issue を分析し、適切なサイズの子 Issue に分解する。
GitHub の Sub-issues 機能で親 Issue と紐付けた状態で子 Issue を作成する。

## ワークフロー

### 1. Issue を取得する

```bash
gh issue view <number> --json number,title,body,labels,assignees,comments
```

リポジトリが明示されていない場合は、カレントディレクトリの remote origin を使う。

### 2. 分解が必要か判断する

Issue を読み、分解が必要なほど大きいかを判断する。
以下の条件を満たす Issue は分解不要：

- 単一の関心事に収まっている（1つの機能、1つの修正、1つのコード領域）。
- 単一の PR でレビュアーが無理なく読み切れる規模に収まっている。

分解不要と判断した場合は、その理由をユーザーに伝えて終了する。例：

> この Issue は3つの受け入れ条件を持つ単一機能の実装です -- 分解は不要です。

Issue が本当に大きい、または複数の独立した関心事にまたがる場合のみ次のステップへ進む。

### 3. 分解案を提示する

Issue を分析し、子 Issue の一覧を提案する。各子 Issue は以下の条件を満たすこと：

- **独立している**：一覧内の他の子 Issue に依存せず実装できる。
- **小さい**：単一の PR で完結できる。
- **具体的**：明確なタイトルと何を実装するかの簡潔な説明がある。

以下の形式でユーザーに提示する：

```markdown
## #<number> の分解案

1. **<タイトル>** — <1行の説明>
2. **<タイトル>** — <1行の説明>
...
```

### 4. ユーザーと調整する

分解案を調整するかどうか確認する：

- 子 Issue の追加・削除・統合
- タイトルや説明の変更

明示的な承認を得てから作成に進む。

### 5. 子 Issue を作成する

承認された各子 Issue を `--parent` 付きで作成し、親 Issue と紐付ける：

```bash
gh issue create \
  --title "<タイトル>" \
  --body "<説明>" \
  --parent <親 Issue 番号>
```

作成後、各 Issue の URL を報告する。

## 出力形式

全ての子 Issue を作成したら、以下の形式でまとめを出力する：

```markdown
## #<number> に作成した子 Issue

- #<n> <タイトル> — <url>
- #<n> <タイトル> — <url>
...
```

## 注意事項

- ユーザーが分解案全体を承認するまで、子 Issue を作成しない。
- `gh issue create --parent` を使うこと -- CLI で Sub-issues を紐付ける唯一の方法。
- ユーザーが明示的に指示するまで、子 Issue の実装には着手しない。
