---
name: merge-bot-prs
description: mise-upgrade-bot や renovate などのボットが作成した PR が GitHub 通知に溜まっており、CI の確認とまとめてマージが必要な場合に使用する。
translated_from: SKILL.md
---

# merge-bot-prs

GitHub 通知からボット PR を一括レビュー・マージする: 作成者でフィルタリングし、CI チェックがすべてパスしていることを確認し、ユーザーに確認を取った上で承認・マージする。

## ワークフロー

1. `check.sh` を実行 — 通知を取得し、ボット作成者でフィルタリングして CI ステータスを確認する
2. 結果レポートをユーザーに提示し、明示的な確認を待つ
3. `merge.sh` を実行 — 各 OK PR を承認（"LGTM"）してマージする

## スクリプト

### check.sh

```sh
# デフォルト: BOT_USER=mise-upgrade-bot[bot], OUTPUT_FILE=/tmp/merge-bot-ok-prs.txt
./skills/merge-bot-prs/scripts/check.sh

# ボットユーザーを変更する場合
BOT_USER=renovate[bot] ./skills/merge-bot-prs/scripts/check.sh
```

PR が **OK** となる条件: 作成者が `BOT_USER` と一致する、PR がオープンかつ未マージである、すべてのチェックが完了している、失敗したチェックがない（skipped/neutral は許容）。

### merge.sh

```sh
./skills/merge-bot-prs/scripts/merge.sh
```

## ユーザー確認ステップ

`check.sh` 完了後、以下の形式でレポートを提示し、`merge.sh` を実行する前にユーザーの確認を取る:

```text
Check results: 24 PRs found — 22 OK / 2 NG

OK (to be merged):
  Repository           | PR   | Title
  23prime/foo          | #12  | deps: Upgrade node to 26.2.0
  ...

NG (skipped):
  Repository           | PR   | Title                    | Reason
  23prime/bar          | #34  | deps: Upgrade lefthook   | CI failed=1
  ...

Proceed to approve and merge the 22 OK PRs?
```

ユーザーが明示的に確認した後にのみ処理を進める。
