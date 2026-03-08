---
name: creating-pull-request
description: "gh CLI を使って現在のブランチから GitHub Pull Request を作成する。git status・diff・コミット履歴を調査して簡潔な PR タイトルと本文を作成し、ブランチをプッシュして PR を開く。ユーザーが PR の作成、プルリクエストのオープン、またはレビュー用の変更の提出を求めた際に使用する。"
translated_from: SKILL.md
---

# Creating Pull Request

現在のブランチから GitHub Pull Request を作成するワークフロー。

## ベースブランチ

ユーザーが明示的に指定しない限り、`main` をベースブランチとして使用する。
以降、`BASE` と呼ぶ。

## ワークフロー

### Step 1: ブランチ情報の収集

以下のコマンドを並行して実行する:

```bash
git status
git diff HEAD
git log BASE...HEAD --oneline
git diff BASE...HEAD
```

以下の情報を把握するために使用する:

- 変更されたファイル（ステージ済み・未ステージ）
- BASE から分岐して以降のこのブランチ上のすべてのコミット
- ベースブランチとのフル差分

### Step 2: プッシュの要否の判断

現在のブランチがリモートを追跡しているか、最新かどうかを確認する:

```bash
git status -sb
```

ブランチに upstream がない、またはリモートより先行している場合はプッシュする:

```bash
git push -u origin HEAD
```

### Step 3: PR タイトルと本文の作成

**タイトル**: 変更内容を要約した 1 文（70 文字以内）。
プロジェクトが conventional commits を使用している場合は、タイプのプレフィックスを付ける（`feat:`、`fix:`、`chore:` など）。

**本文**: まず PR テンプレートを確認する:

```bash
cat .github/pull_request_template.md 2>/dev/null || cat .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null
```

- テンプレートが存在する場合は、そのすべてのセクションを埋める。省略しない。
- テンプレートが存在しない場合は、以下のフォールバックを使用する:

```markdown
## Checklist

- [ ] Status checks are passing
- [ ] Target branch is correct

## Summary

## Reason for change

## Changes

## Notes
```

### Step 4: PR の作成

フォーマットを保持するために heredoc で本文を渡す:

```bash
gh pr create --base BASE --title "..." --body "$(cat <<'EOF'
<filled body here>
EOF
)"
```

完了したら PR の URL をユーザーに返す。

## 注意事項

- 最新のコミットだけでなく、ブランチ上の**すべての**コミットを必ず分析する。
- ユーザーから明示的な要求がない限り、force-push しない。
