---
name: creating-branch
description: GitHub Issue や新機能の作業を開始するとき、実装前にトピックブランチを作成する必要があるときに使用する。
translated_from: SKILL.md
---

# ブランチの作成

リポジトリの命名規則に従ってトピックブランチを作成し、
upstream トラッキングを設定してリモートに push する。

## ワークフロー

### 1. 命名規則を調べる

以下の順番でブランチ命名ルールを探す：

1. 命名規則をインストラクションファイルと貢献ガイドから探す：

   ```bash
   fd -e md --max-depth 3 | rg -i 'CLAUDE|AGENTS|CONTRIBUTING'
   ```

   見つかったファイルを読み、ブランチ命名規則が記載されていないか確認する。
2. 既存のリモートブランチから、すでに存在するブランチ名のパターンを推定：

   ```bash
   git branch -r --format '%(refname:short)' | grep -v 'HEAD\|main\|master\|develop'
   ```

ルールが見つからない場合は以下のデフォルトを使う：

| 種別 | プレフィックス |
| ---- | -------------- |
| 新機能 | `feature/` |
| バグ修正 | `fix/` |
| 緊急修正 | `hotfix/` |
| 保守・雑務 | `chore/` |
| ドキュメント | `docs/` |
| リファクタリング | `refactor/` |

### 2. ブランチ名を決める

Issue 番号とタイトル（またはタスクの説明）からブランチ名を組み立てる：

- タイトルを小文字のケバブケースに変換する
- 英数字とハイフン以外の文字を除去する
- プレフィックスを含めて読みやすい長さに収める（合計 50 文字以内）
- Issue 番号がある場合は含める

例：

| 入力 | ブランチ名 |
| ---- | ---------- |
| Issue #42 "Add OAuth login" | `feature/42-add-oauth-login` |
| Issue #7 "Fix null pointer on startup" | `fix/7-null-pointer-on-startup` |
| "Upgrade dependencies" | `chore/upgrade-dependencies` |

### 3. デフォルトブランチを最新化する

デフォルトブランチを特定し、最新の状態に更新する：

```bash
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
git switch <default-branch>
git pull
```

### 4. ブランチを作成して push する

```bash
git switch -c <branch-name>
git push -u origin <branch-name>
```

作成したブランチ名をユーザーに報告する。

## 注意事項

- ユーザーが明示的に指示しない限り、別のトピックブランチからではなく `gh repo view` で取得したデフォルトブランチから分岐する。
- ブランチ名をユーザーに確認しない。すぐに作成する。
- ブランチ作成後に実装に入らない。ユーザーの指示を待つ。
