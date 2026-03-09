---
name: resolving-pr-conversations
description: "返信内容を分析して GitHub PR レビューの会話を resolve するスキル。返信のないスレッドはそのまま放置し、返信済みスレッドは修正済み・意図的スキップが明確な場合は自動 resolve、曖昧な場合はユーザーに確認する。PR レビューのスレッドを整理したいとき（GitHub Copilot レビュー後など）に使用する。"
translated_from: SKILL.md
---

# PR 会話の Resolve

このスキルは GitHub PR のレビュースレッドを調査し、対応済みのスレッドを resolve する。
返信のないスレッドはそのまま放置する。

## ワークフロー

### Step 1 — PR を特定する

`OWNER/REPO` と `PR_NUMBER` を以下の手順で決定する:

- **PR URL が与えられた場合** — URL からパースする。
- **明示的に指定された場合** — そのまま使用する。
- **それ以外の場合** — カレントディレクトリから自動検出する:

  ```bash
  gh repo view --json nameWithOwner --jq .nameWithOwner  # OWNER/REPO
  gh pr view --json number --jq .number                  # PR_NUMBER
  ```

  `gh pr view` が失敗した場合は、PR の URL または番号をユーザーに尋ねる。

### Step 2 — 全レビュースレッドを取得する

```bash
gh pr-review review view <PR_NUMBER> -R <OWNER/REPO> \
  | jq '[.reviews[]?.comments[]? | {thread_id, path, line, author_login, body, is_resolved, is_outdated, thread_comments}]'
```

これにより全レビューのスレッドを単一の配列にフラット化する。各要素は以下のフィールドを持つ:

- `thread_id` — GraphQL ノード ID（`PRRT_…`）、resolve 時に必要
- `path`, `line` — インラインコメントのファイルと行番号
- `author_login` — レビュアーの GitHub ログイン名
- `body` — 元のコメントテキスト
- `is_resolved` — GitHub 上で resolve 済みの場合 `true`
- `is_outdated` — diff がこのコメントを追い越した場合 `true`
- `thread_comments` — スレッド内の返信配列

### Step 3 — 全スレッドを分類する

全スレッドに対して（レビュアー問わず）以下の判定ルールを順番に適用する:

| 条件 | 分類 |
| ---- | ---- |
| `is_resolved: true` | **resolve 済み** — スキップ |
| `thread_comments` が空 | **返信なし** — スキップ（そのまま放置） |
| 修正済みを明確に示す返信（例: "fixed in \<commit\>"、"addressed"、"修正しました"） | **自動 resolve** |
| 意図的スキップを明確に示す返信（例: "won't fix"、"by design"、"意図的です"、"対応しません"） | **自動 resolve** |
| 曖昧または不明確な返信 | **ユーザーに確認** |

「明確に示す」とは、返信本文に明確な意図が含まれていることを意味する。判断に迷う場合は **ユーザーに確認** に分類する。

### Step 4 — サマリ・対象範囲・計画をまとめて提示し、一度に確認する

ユーザーが判断に必要な情報をすべて1つのメッセージにまとめて提示し、一度の返答を待つ:

```text
未 resolve スレッド一覧（レビュアー別）:

copilot-pull-request-reviewer (1 件):
  - src/main.rs:73 — "`--json` フラグが親コマンドとサブコマンドで重複している"  [返信なし]

coderabbitai (2 件):
  - src/cmd/space.rs:175 — "project が None の場合のフォールバックをテストで明示..."  [自動 resolve: "fixed in abc1234"]
  - docs/api.md:7         — "Consider using pathlib here."                          [要確認: 返信 "ok" が曖昧]

---
対象レビュアー: [1] GitHub Copilot のみ（デフォルト） / [2] 全員

曖昧なスレッドを resolve しますか？（以下）
  - docs/api.md:7  Copilot: "Consider using pathlib here." / 返信: "ok"  [y/n]
```

ユーザーの返答（例: "1, y"）をまとめてパースする:

- 対象範囲の選択（1 または 2。省略時はデフォルトの 1）
- **ユーザーに確認** の各スレッドに対する y/n

変更要求があれば計画を修正して再提示する。

パース後、選択された対象範囲でスレッドをフィルタし、**ユーザーに確認** の回答を反映して resolve 対象の最終リストを確定する。

### Step 5 — 承認されたスレッドを resolve する

resolve が承認された各スレッドに対して、以下を実行する:

```bash
gh pr-review threads resolve <PR_NUMBER> -R <OWNER/REPO> --thread-id <thread_id>
```

コマンドがゼロ以外のステータスで終了した場合はエラーを報告し、残りのスレッドの処理を続ける。

### Step 6 — 結果サマリを出力する

全スレッドの処理後、1 スレッドにつき 1 行で出力する:

- Resolved: `src/foo.py:42` — "fixed in abc1234"
- Resolved: `src/bar.py:17` — "won't fix: intentional behaviour"
- Skipped (no reply): `src/qux.py:5`
- Already resolved: `src/baz.py:10`
- User declined to resolve: `docs/api.md:7`

## Notes

- `gh` CLI（`gh auth login`）および `gh-pr-review` 拡張機能が必要
  （`gh extension install agynio/gh-pr-review`）
- 取得されるのはインラインレビュースレッドのコメントのみ。PR レベルのディスカッションコメントは含まれない
- このスキルは新しい返信を投稿しない。既存スレッドの resolve のみを行う
- スレッドの resolve にはリポジトリへの書き込み権限が必要
