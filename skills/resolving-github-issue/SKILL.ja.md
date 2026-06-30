---
name: resolving-github-issue
description: GitHub Issue を要件確認から PR マージまで一気通貫で進めたいときに使用する。
translated_from: SKILL.md
---

# GitHub Issue の解決

GitHub Issue のライフサイクル全体をオーケストレーションする：明確化 → 計画 → 実装 → レビュー → マージ。
各ステップは専用スキルに委譲し、このスキルは順序と判断ポイントを定義する。

## ワークフロー

### 1. Issue をブラッシュアップする

`refining-github-issue` を Issue 番号または URL で呼び出す。
コードを書く前に意図・スコープ・受け入れ条件を明確にする。

### 2. 分解するか判断する

`decomposing-github-issue` を呼び出す。
単一 PR で十分なサイズなら分解をスキップして次へ進む。
分解が必要なら、各子 Issue についてステップ 3 以降を独立して実施する。

### 3. ブランチを作成する

Issue 番号とタイトルで `creating-branch` を呼び出す。
スキルが命名規則を自動検出し、デフォルトブランチを最新化してからブランチを作成する。

### 4. 実装する

受け入れ条件に従って作業する。実装方法はプロジェクトによる：
テスト実行、設定変更、コード編集 — Issue が求めるものを行う。

### 5. コミットする

論理的なまとまりの作業が完了したら `committing-changes` を呼び出す。
全ての受け入れ条件を満たすまでステップ 4〜5 を繰り返す。

### 6. 自己レビューする

PR を開く前に `reviewing-changes` を呼び出す。
問題が見つかれば修正し、`committing-changes` でコミットする。

### 7. PR を作成する

`creating-pull-request` を呼び出す。

### 8. レビューに対応する

`responding-to-pr-review` を呼び出し、PR がマージされるまで繰り返す。

## サブスキル一覧

| ステップ | スキル |
| -------- | ------ |
| 1 | `refining-github-issue` |
| 2 | `decomposing-github-issue` |
| 3 | `creating-branch` |
| 5 | `committing-changes` |
| 6 | `reviewing-changes` |
| 7 | `creating-pull-request` |
| 8 | `responding-to-pr-review` |

## 注意事項

- ステップ 1 を完了してからコードを書く — 受け入れ条件が不明なまま実装すると手戻りが発生する
- ステップ 2 は小さい Issue でも必ず呼び出す。分解が必要かどうかはスキルが判断する
- ステップ 4〜5 はステップ 6 に進む前に複数回繰り返すことがある
- PR レビューでスコープ拡大や新たな要件が発覚した場合はステップ 1 に戻る
