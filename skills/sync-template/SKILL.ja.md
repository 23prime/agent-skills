---
name: sync-template
description: 各テンプレート派生リポジトリに対して `git sync-upstream --push` を実行し同期する。テンプレートリポジトリの同期、複数リポジトリへの sync-upstream 実行、upstream の変更を派生リポジトリに反映する際に使用する。
translated_from: SKILL.md
---

# Sync Template

テンプレート派生リポジトリを順に処理し、`git sync-upstream --push` を実行する。失敗はスキップして最後に結果を報告する。

## ワークフロー

### 1. 同期対象の確認

`skills/sync-template/sync_targets.txt` が存在することを確認する。

存在しない場合は、`skills/sync-template/sync_targets.example.txt` を `skills/sync-template/sync_targets.txt` にコピーして編集するようユーザーに伝え、処理を停止する。

### 2. sync-all スクリプトの実行

同梱のラッパースクリプトを**一度だけ**実行する。ループ処理はスクリプト内部で行われる：

```bash
./skills/sync-template/scripts/sync-all.sh ./skills/sync-template/sync_targets.txt
```

スクリプトは進捗を stderr にストリーミングし、標準出力にタブ区切りの `<repo>\t<OK|FAILED>\t<notes>` 行を含む `---RESULTS---` ブロックを出力する。

### 3. 結果の報告

`---RESULTS---` ブロックを解析し、サマリーテーブルを報告する：

| Repository | Result      | Notes                    |
|------------|-------------|--------------------------|
| repo-name  | OK / FAILED | error message if failed  |

失敗したリポジトリには、以下を参考に推奨アクションを付記する：

- マージコンフリクト → 「`~/develop/<repo>` で手動解消してから push する」
- 認証/SSH エラー → 「リモートへの SSH キーのアクセスを確認する」
- 履歴の乖離 → 「`git log` を確認し、`git reset` または手動 rebase を検討する」
- pre-push hook のツール不足 → 「不足しているツールをインストールするか、利用可能な環境で同期を実行する」
- その他 → 出力の notes フィールドを引用する

### 4. 古い "Merge upstream changes" PR のクローズ

ステップ3で `OK` と報告されたリポジトリについて、"Merge upstream changes" というタイトルのオープンな GitHub PR がないか確認し、あればクローズする。同期処理で直接マージ・push 済みのため不要になっているからだ：

```bash
cd ~/develop/<repo>
gh pr list --state open --search "Merge upstream changes in:title" --json number --jq '.[].number'
```

返された各 PR 番号をクローズする：

```bash
gh pr close <number>
```

## 補足

- `scripts/sync-upstream.sh` は `upstream/main` から pull してマージし、`mise.toml` が存在する場合は `mise run setup` を実行して更新されたツールをインストールしてから `origin/main` に push する。その後 `sync-upstream-*` ブランチをローカル・リモート両方から削除し、`git fetch --prune` を実行する
- `scripts/sync-all.sh` は git 操作の競合を避けるためリポジトリを逐次実行し、失敗してもループを中断しない
