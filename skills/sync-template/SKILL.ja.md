---
name: sync-template
description: 各テンプレート派生リポジトリに対して `git sync-upstream --push` を実行し同期する。テンプレートリポジトリの同期、複数リポジトリへの sync-upstream 実行、upstream の変更を派生リポジトリに反映する際に使用する。
translated_from: SKILL.md
---

# Sync Template

テンプレート派生リポジトリを順に処理し、`git sync-upstream --push` を実行する。失敗はスキップして最後に結果を報告する。

## ワークフロー

### 1. 同期対象の読み込み

`skills/sync-template/sync_targets.txt` からリポジトリ名の一覧を読み込む（1行1件、`#` コメントと空行は無視）。

`sync_targets.txt` が存在しない場合は、`skills/sync-template/sync_targets.example.txt` を `skills/sync-template/sync_targets.txt` にコピーして編集するようユーザーに伝え、処理を停止する。

### 2. 各リポジトリの同期実行

リポジトリ名ごとに同期スクリプトを実行する:

```bash
./skills/sync-template/scripts/sync-upstream.sh ~/develop/<repo-name>
```

出力の混在や git 操作の競合を避けるため、**逐次実行**する（並列不可）。

### 3. 結果の報告

全リポジトリの処理が完了したら、サマリーテーブルを報告する:

| Repository | Result      | Notes                          |
|------------|-------------|--------------------------------|
| repo-name  | OK / FAILED | 失敗時はエラーメッセージを記載 |

失敗したリポジトリには、エラー出力をもとに推奨アクションを付記する:

- マージコンフリクト → "`~/develop/<repo>` で手動解消してから push する"
- 認証/SSH エラー → "リモートへの SSH キーのアクセスを確認する"
- 履歴の乖離 → "`git log` を確認し、`git reset` または手動 rebase を検討する"
- その他 → 出力の最終エラー行を引用する

## 補足

- `scripts/sync-upstream.sh` は `upstream/main` から pull してマージし、`origin/main` に push する。その後 `sync-upstream-*` ブランチをローカル・リモート両方から削除し、`git fetch --prune` を実行する
- スクリプトが非ゼロの終了コードを返した場合はそのリポジトリを失敗とし、次へ進む
- 失敗してもループを中断しない
