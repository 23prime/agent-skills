---
name: implementing-pr-review
description: "GitHub Pull Request のレビューコメントを取得し、各コメントの正確性とベストプラクティスへの適合性を批判的に評価する。妥当な提案のみをソースコードまたはドキュメントに反映する。ユーザーが PR の URL を提示してレビューフィードバックを適用・実装するよう求めた際に使用する。"
translated_from: SKILL.md
---

# Implementing PR Review

このスキルは GitHub PR のレビューコメントを取得し、各コメントの妥当性を判断したうえで
有効なものをコードベースに反映し、各コメントに修正コミットのハッシュまたは判断理由を返信する。
コメントは誤りを含んでいたり、古いプラクティスを反映している場合があるため、
コードを変更する前に必ず評価を行う。

## ワークフロー

### Step 1 — PR コメントの取得

PR の URL または `OWNER/REPO PR_NUMBER` 形式でスクリプトを実行する:

```bash
uv run python fetch_pr_comments.py <PR_URL>
# または
uv run python fetch_pr_comments.py owner/repo 42
```

スクリプトは以下の 3 つのセクションを含む JSON を出力する:

- `pr` — タイトル、URL、本文
- `review_comments` — インラインコードコメント（ファイル + 行番号 + diff hunk）
- `issue_comments` — 一般的なディスカッションコメント

### Step 2 — 対応済みコメントのスキップ

内容を評価する前に、以下のいずれかに該当するコメントはスキップする:

- **Resolved**（`resolved: true`）— GitHub 上でスレッドが resolved 済み
- **返信がある**（`replies` 配列が空でない）— 返信の内容に関わらず、すでに誰かが対応済みとして扱う
- **Outdated**（`outdated: true`）— diff が変わりコメントの参照先が失効しているため対応不要

対応済みとしてスキップしたコメントは最終サマリーに記録するが、返信はしない。

### Step 3 — 残りのコメントの評価とグルーピング

残ったコメントごとに、参照先のファイルと周辺のコンテキストを読み込み、以下を判断する:

**以下をすべて満たす場合に適用する:**

- 使用している言語・フレームワークに対して技術的に正確な提案である
- 現在のベストプラクティスに沿っている（廃止されたパターンでない）
- 既存のコードスタイルおよびプロジェクトの規約と一致している
- 正確性・明瞭性・パフォーマンス・セキュリティの向上に寄与する（単なる好みでない）

**以下のいずれかに該当する場合はスキップし、理由を説明する:**

- 事実誤認を含む（誤った API、誤った動作）
- 廃止または時代遅れのアプローチを推奨している
- 明確なメリットなしにプロジェクトの規約と矛盾する
- 客観的な改善を伴わない純粋なスタイルの好みによるもの

**適用前に関連コメントをグルーピングする:**

複数箇所で同じ問題を指摘しているコメント（例: 3 つのファイルで「`os.path` の代わりに
`pathlib` を使う」と言及）は、1 つの論理的な修正として扱う。それらを 1 つのコミットに
まとめ、全箇所を一度に修正したうえで、グループに属する各コメントに返信する。

### Step 4 — ユーザーへの確認

変更を加える前に、全体の対応計画を提示してユーザーの承認を得る:

```text
## レビュー対応計画

**適用予定（N 件）:**
- [グループ] src/foo.py:42, src/bar.py:17 — `os.path` を `pathlib.Path` に置き換え
- src/baz.py:10 — null チェックの追加

**スキップ — 変更なし（N 件）:**
- docs/api.md:7 — 削除済みの API (`v1/endpoint`) を使用する提案

**対応済み — 何もしない（N 件）:**
- src/qux.py:5 — 既存の返信あり

進めてよいですか？
```

ユーザーが承認するまで一切の変更を加えない。
特定のコメントのスキップや判断の見直しを求められた場合は計画を修正し、再度確認する。

### Step 5 — 適用・コミット・プッシュ・返信（コメント（グループ）ごとに 1 コミット）

受け入れたコメントまたはグループごとに以下を実行する:

1. 対象ファイル全体を読み込みコンテキストを把握する
2. フィードバックを満たす最小限の変更を適用する — コメントの範囲を超えた
   周辺コードのリファクタリングは行わない
3. PR コメントの内容を参照した簡潔なメッセージでコミットする:

   ```bash
   git add <changed files>
   git commit -m "<what was done>" -m "Addresses review comment: <short quote>"
   ```

4. コミット直後にプッシュする:

   ```bash
   git push
   ```

5. `git rev-parse HEAD` で取得した完全なコミットハッシュを使い、
   このコミットに属するすべての PR コメントに返信する:

   ```bash
   uv run python reply_review_comment.py \
     <owner/repo> <comment_id> "fixed by <commit_hash>"
   ```

   `issue_comments` は GitHub API がスレッド返信をサポートしないため、
   元のコメントを引用した新規 PR コメントを投稿する:

   ```bash
   uv run python post_pr_comment.py \
     <owner/repo> <pr_number> "> @<author>: <original comment body>\n\nfixed by <commit_hash>"
   ```

適用 → コミット → プッシュ → 返信 のループを、独立したコメント（またはグループ）ごとに
次へ進む前に完了させる。

**スキップ**したコメントに対しては、直ちに理由を返信する:

```bash
uv run python reply_review_comment.py \
  <owner/repo> <comment_id> "No change: <one-sentence reason>"
```

`issue_comments` の場合は元のコメントを引用した新規 PR コメントを投稿する:

```bash
uv run python post_pr_comment.py \
  <owner/repo> <pr_number> "> @<author>: <original comment body>\n\nNo change: <one-sentence reason>"
```

### Step 6 — サマリーの報告

すべてのコメントを処理し終えたら、1 コメントにつき 1 行で出力する:

- Applied (commit `abc1234`): `src/foo.py:42` — `os.path` を `pathlib.Path` に置き換え
- Applied (commit `abc1234`): `src/bar.py:17` — 上記と同じ修正、グループ化済み
- Skipped (no change): `docs/api.md:7` — 削除済みの API (`v1/endpoint`) を使用する提案
- Already handled: `src/baz.py:5` — 既存の返信あり（対応不要）

## 備考

- `review_comments`（インライン）には `diff_hunk`、`path`、`line` が含まれ、
  ファイル内の正確な位置の特定に使用する
- `issue_comments` は一般的なディスカッションのため、明確で実行可能なコード・
  ドキュメントの変更を求める内容のみ対応する
- `gh` CLI（`gh auth login`）と `uv` が必要
- 開始前に作業ブランチがリモートにプッシュ済みであることを確認する
  （プッシュしたコミットが PR 上で可視になるため）
