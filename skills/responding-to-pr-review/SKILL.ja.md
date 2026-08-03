---
name: responding-to-pr-review
description: "GitHub Pull Request のレビューコメントを取得し、各コメントの正確性とベストプラクティスへの適合性を批判的に評価する。妥当な提案のみをソースコードまたはドキュメントに反映する。修正適用後は PR が承認されるまでポーリングを続け、新しいコメントが来るたびにレビューサイクルを再開する。ユーザーが PR の URL を提示してレビューフィードバックを適用・実装するよう求めた場合、または承認されるまで繰り返し対応したい場合に使用する。"
translated_from: SKILL.md
---

# Responding to PR Review

このスキルは GitHub PR のレビューコメントを取得し、各コメントの妥当性を判断したうえで
有効なものをコードベースに反映し、各コメントに修正コミットのハッシュまたは判断理由を返信する。
コメントは誤りを含んでいたり、古いプラクティスを反映している場合があるため、
コードを変更する前に必ず評価を行う。

## ワークフロー

### Step 1：PR コメントの取得

`OWNER/REPO` と `PR_NUMBER` を以下の優先順位で決定する：

- **PR の URL が与えられた場合**：URL から `OWNER/REPO` と `PR_NUMBER` をパースする。
- **`OWNER/REPO` と `PR_NUMBER` が明示された場合**：そのまま使用する。
- **それ以外**：カレントディレクトリから自動検出する：

  ```bash
  gh repo view --json nameWithOwner --jq .nameWithOwner  # OWNER/REPO
  gh pr view --json number --jq .number                  # PR_NUMBER
  ```

  `gh pr view` が失敗した場合（カレントブランチに対応する PR が見つからない）は、
  PR の URL または番号をユーザーに確認する。

その後、以下を実行する：

```bash
gh pr-review review view <PR_NUMBER> -R <OWNER/REPO>
```

`reviews` 配列を含む JSON オブジェクトが出力される。すべてのインラインレビューコメントを
展開するには以下を使う：

```bash
gh pr-review review view <PR_NUMBER> -R <OWNER/REPO> | jq '[.reviews[]?.comments[]?]'
```

各コメントには以下のフィールドが含まれる：

- `thread_id`：GraphQL スレッドノード ID（`PRRT_...` 形式）。返信時に使用
- `path`・`line`：インラインコメントのファイルと行番号
- `author_login`：レビュアーの GitHub ログイン名
- `body`：コメント本文
- `is_resolved`：GitHub 上でスレッドが resolved 済みの場合 `true`
- `is_outdated`：diff が変わりコメントの参照先が失効した場合 `true`
- `thread_comments`：スレッド内にすでに投稿された返信の配列

### Step 2：対応済みコメントのスキップ

内容を評価する前に、以下のいずれかに該当するコメントはスキップする：

- **Resolved**（`is_resolved: true`）：GitHub 上でスレッドが resolved 済み
- **Outdated**（`is_outdated: true`）：diff が変わりコメントの参照先が失効
- **返信がある**（`thread_comments` 配列が空でない）：すでに誰かが対応済み

対応済みとしてスキップしたコメントは最終サマリーに記録するが、返信はしない。

### Step 3：残りのコメントの評価とグルーピング

残ったコメントごとに、`path`:`line` で指定されたファイルと周辺のコンテキストを
読み込み、以下を判断する：

**以下をすべて満たす場合に適用する：**

- 使用している言語・フレームワークに対して技術的に正確な提案である。
- 現在のベストプラクティスに沿っている（廃止されたパターンでない）。
- 既存のコードスタイルおよびプロジェクトの規約と一致している。
- 正確性・明瞭性・パフォーマンス・セキュリティの向上に寄与する（単なる好みでない）。

**以下のいずれかに該当する場合はスキップし、理由を説明する：**

- 事実誤認を含む（誤った API、誤った動作）。
- 廃止または時代遅れのアプローチを推奨している。
- 明確なメリットなしにプロジェクトの規約と矛盾する。
- 客観的な改善を伴わない純粋なスタイルの好みによる。

**適用前に関連コメントをグルーピングする：**

複数箇所で同じ問題を指摘しているコメント（例：3 つのファイルで「`os.path` の代わりに
`pathlib` を使う」と言及）は、1 つの論理的な修正として扱う。それらを 1 つのコミットに
まとめ、全箇所を一度に修正したうえで、グループに属する各コメントに返信する。

### Step 4：ユーザーへの確認

変更を加える前に、全体の対応計画を提示してユーザーの承認を得る：

```text
## レビュー対応計画

**適用予定（N 件）:**
- [グループ] src/foo.py:42, src/bar.py:17：`os.path` を `pathlib.Path` に置き換え
- src/baz.py:10：null チェックの追加

**スキップ：変更なし（N 件）:**
- docs/api.md:7：削除済みの API (`v1/endpoint`) を使用する提案

**対応済み：何もしない（N 件）:**
- src/qux.py:5：既存の返信あり

進めてよいですか？
```

ユーザーが承認するまで一切の変更を加えない。
特定のコメントのスキップや判断の見直しを求められた場合は計画を修正し、再度確認する。

### Step 5：適用・コミット・プッシュ・返信（コメント（グループ）ごとに 1 コミット）

受け入れたコメントまたはグループごとに以下を実行する：

1. 対象ファイル全体を読み込みコンテキストを把握する。
2. フィードバックを満たす最小限の変更を適用する：コメントの範囲を超えた
   周辺コードのリファクタリングは行わない。
3. PR コメントの内容を参照した簡潔なメッセージでコミットする：

   ```bash
   git add <changed files>
   git commit -m "<what was done>" -m "Addresses review comment: <short quote>"
   ```

4. コミット直後にプッシュする：

   ```bash
   git push
   ```

5. **別の** Bash ツール呼び出しでコミットハッシュを取得する（`$()` コマンド置換は
   使わない：`git rev-parse HEAD` を単独で実行し、その出力をリテラル文字列として
   次の呼び出しに埋め込む）：

   ```bash
   git rev-parse HEAD
   ```

   その後、このコミットに属するすべての PR コメントに返信する：

   ```bash
   gh pr-review comments reply <PR_NUMBER> -R <OWNER/REPO> \
     --thread-id <thread_id> --body "fixed by <commit_hash>"
   ```

適用 → コミット → プッシュ → 返信 のループを、独立したコメント（またはグループ）ごとに
次へ進む前に完了させる。

**スキップ**したコメントに対しては、直ちに理由を返信する：

```bash
gh pr-review comments reply <PR_NUMBER> -R <OWNER/REPO> \
  --thread-id <thread_id> --body "No change: <one-sentence reason>"
```

### Step 6：サマリーの報告

すべてのコメントを処理し終えたら、1 コメントにつき 1 行で出力する：

- Applied (commit `abc1234`): `src/foo.py:42`：`os.path` を `pathlib.Path` に置き換え
- Applied (commit `abc1234`): `src/bar.py:17`：上記と同じ修正、グループ化済み
- Skipped (no change): `docs/api.md:7`：削除済みの API (`v1/endpoint`) を使用する提案
- Already handled: `src/baz.py:5`：既存の返信あり（対応不要）

### Step 7：GitHub Copilot のレビュースレッドを resolve する

サマリー出力後、同じ PR を対象に `resolving-pr-conversations` スキルを呼び出す。
対象は GitHub Copilot のみ（スコープ `[1]`）とする。すでに判明している `OWNER/REPO` と
`PR_NUMBER` を渡すことで PR の検出をスキップし、スコープ選択もデフォルトの `[1]` で進める。

### Step 8：承認チェックとループ

スレッドの resolve 後、PR の承認状況を確認する：

```bash
gh pr view <PR_NUMBER> -R <OWNER/REPO> --json reviewDecision --jq .reviewDecision
```

- **`APPROVED`**：PR が承認済み。このスキルはここで完了し、呼び出し元に
  制御を返す。
- **それ以外**：バンドルされたポーリングスクリプトを実行する：

  ```bash
  # Bash ツールの10分タイムアウトを回避するため run_in_background: true で実行する
  as-poll-until-approved <PR_NUMBER> <OWNER/REPO>
  ```

  スクリプトは 1 分ごとに最大 4 時間ポーリングする。終了コード：

  - `0`：PR が承認された。このスキルは完了。
  - `1`：4 時間でタイムアウト。ユーザーに報告して終了する。
  - `2`：新しい未解決コメント（未返信）を検出。Step 1 から再開する。
  - `3`：すでに返信済みのスレッドが5分以上未解決のまま。例えば CodeRabbit
    が返信後に自動 resolve しなかったケース。以下の通り対応し、単純に
    再開・待機し続けない。

  **終了コード `3` の場合：** スクリプトは stuck しているスレッド
  （`thread_id`、`path`、`line`、直近の返信の投稿者・本文）を出力する。
  これをユーザーに提示する。直近の返信には CodeRabbit の新しい指摘が
  含まれている可能性があるため、その内容も併せて示し、次のアクションを
  提案する：

  - 直近の返信が resolve を伴わない単なる確認応答であれば、この PR に対して
    `resolving-pr-conversations` スキルをスコープ `[2]`（全レビュアー対象）
    で実行することを提案する。すでにこちらの返信が修正内容を明記している
    ため、そのスキルの判定ルールにより自動 resolve される。
  - 直近の返信が新しい実質的な指摘であれば、新規レビューコメントとして
    扱い、Step 1 から再開する。

  ユーザーの判断を待ってから実行する。resolve（または Step 1 からの再開後
  再びこのステップに到達した場合）の後、`as-poll-until-approved` で
  ポーリングを再開する。

## 備考

- `path` と `line` でファイルの正確な位置を特定し、ファイルを直接読み込んで
  周辺のコンテキストを確認する（`diff_hunk` は提供されない）。
- `gh pr-review review view` はインラインレビュースレッドのみを返す。
  PR 全体へのディスカッションコメントは含まれない。
- `gh` CLI（`gh auth login`）と `gh-pr-review` 拡張
  （`gh extension install agynio/gh-pr-review`）が必要。
- 開始前に作業ブランチがリモートにプッシュ済みであることを確認する
  （プッシュしたコミットが PR 上で可視になるため）。
- `as-poll-until-approved` が `$PATH` 上にあることが前提。
  `linking-skill-scripts` スキルを一度実行してセットアップする。
