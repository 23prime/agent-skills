---
name: finishing-pull-request
description: Pull Request が承認され、必須チェックの通過が見込まれる段階で、マージとトピックブランチの後片付けを行いたいときに使用する。
translated_from: SKILL.md
---

# Pull Request の仕上げ

承認済みの PR をマージし、トピックブランチを後片付けする。このスキルは PR が
すでに `APPROVED` であることを前提とする — レビューコメントの取得や評価は行わない。

## ワークフロー

### Step 1：PR をマージする

必須チェックがすべてパスするのを待つ：

```bash
gh pr checks <PR_NUMBER> -R <OWNER/REPO> --watch
```

チェックが失敗した場合はユーザーに報告して終了する。

チェックがパスしたら、マージ前にユーザーへ確認する：

```text
All checks passed. Merge PR #<PR_NUMBER>? [y/N]
```

承認された場合にマージを実行する：

```bash
gh pr merge <PR_NUMBER> -R <OWNER/REPO> --merge
```

### Step 2：トピックブランチをクリーンアップする

マージ後、トピックブランチをローカルとリモートから削除する：

```bash
as-clean-topic-branch
```

スクリプトはデフォルトブランチに切り替え、最新の変更を pull し、
トピックブランチをローカルとリモートの両方から削除する。

## 備考

- `as-clean-topic-branch` が `$PATH` 上にあることが前提。`linking-skill-scripts`
  スキルを一度実行してセットアップする。
