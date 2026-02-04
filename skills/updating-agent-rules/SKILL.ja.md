---
name: updating-agent-rules
description: リポジトリの現在の状態に基づいて AGENTS.md を更新する。リポジトリの設定、構造、ツールが変更され、AGENTS.md にその変更を反映する必要がある場合に使用する。
translated_from: SKILL.md
---

# Updating Agent Rules

## 概要

リポジトリにおける AI コーディングエージェント向け指示の唯一の情報源 (SSoT) である AGENTS.md を更新するスキル。他のエージェントルールファイル (CLAUDE.md, .github/copilot-instructions.md) は `@AGENTS.md` のようなディレクティブで AGENTS.md を参照しているため、AGENTS.md を正確に保つだけですべてのエージェントが同期される。

## ワークフロー

### 1. 現在の状態を収集する

以下のファイルを読み、何が変更されたかを把握する:

- `AGENTS.md` — 現在のエージェントルール
- `pyproject.toml` — プロジェクトメタデータ、依存関係、Python バージョン
- `mise.toml` — ツールとタスク
- `lefthook.yml` — git フック
- `.editorconfig` — コードスタイル設定
- `.markdownlint-cli2.jsonc` — Markdown lint ルール
- `README.md` — プロジェクトの説明とセットアップ手順

また、`skills/` をスキャンし、Skill Workflow セクションに影響する新規または削除されたスキルがないか確認する。

### 2. 差分を特定する

現在の AGENTS.md の内容を収集した状態と比較する。注目すべき点:

- **Project Overview** — 説明、リンク
- **Setup** — 前提条件、コマンド
- **Skill Structure** — ディレクトリ構成の規約
- **Skill Workflow** — 作成/バリデーション/パッケージングのコマンド
- **Validation Rules** — 命名規則、frontmatter の要件
- **Code Style** — フォーマット、インデント、lint ルール

### 3. 更新を適用する

AGENTS.md を現在の状態に合わせて編集する。以下の原則に従う:

- 簡潔に保つ — AI エージェントにとって自明でなく有用な情報のみ記載する
- 個々のファイルを読めば容易にわかる情報を繰り返さない
- 一般的な開発アドバイスを追加しない
- 構造的な変更が正当化されない限り、既存のセクション構成を維持する
- リポジトリの他の部分と同じコードスタイルを使用する（リストにはダッシュ、強調にはアスタリスク）

### 4. 参照を検証する

AGENTS.md を参照しているファイルが正しく機能していることを確認する:

- `CLAUDE.md` に `@AGENTS.md` が含まれていること
- `.github/copilot-instructions.md` に `@AGENTS.md` が含まれていること

これらのファイルが存在しない、または内容が古い場合は更新する。
