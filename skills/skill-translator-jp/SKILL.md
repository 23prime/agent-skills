---
name: skill-translator-jp
description: "Translate a skill's SKILL.md into Japanese and output it as SKILL.ja.md. This skill should be used when users want to translate a skill into Japanese, localize skills for Japanese speakers, or create Japanese versions of skills."
---

# Skill Translator JP

エージェントスキルの SKILL.md を日本語に翻訳し、`SKILL.ja.md` として同ディレクトリに出力する。

## 翻訳対象と範囲

| 対象 | 翻訳するか |
| ------ | ----------- |
| YAML frontmatter の `name` | しない（英語のまま） |
| YAML frontmatter の `description` | する |
| SKILL.md 本文（instructions） | する |
| `references/` 内のファイル | しない |
| `scripts/` 内のファイル | しない |
| `assets/` 内のファイル | しない |

## ワークフロー

1. ユーザーから翻訳対象のスキルパスを受け取る（例: `skills/skill-creator`）
2. 対象の SKILL.md を読み込む
3. 以下の翻訳ルールに従って翻訳する
4. 同ディレクトリに `SKILL.ja.md` として書き出す
5. `mise fix-md` コマンドで `SKILL.ja.md` を自動修正し、エラーが残っている場合 `mise check-md` をパスするまで修正する
6. ユーザーに完了を報告し、翻訳内容の確認を促す

## 翻訳ルール

### 全般

- 自然で読みやすい日本語にする。機械翻訳調の不自然な表現を避ける
- 技術用語で一般的にカタカナや英語のまま使われるものはそのまま残す
  - 例: YAML, frontmatter, Claude, API, MCP, スクリプト, テンプレート, Markdown
- コードブロック内のコード・コマンド・ファイルパスは翻訳しない
- コードブロック内のコメントは日本語に翻訳する
- Markdown の構造（見出しレベル、リスト、リンク等）をそのまま維持する
- 原文にないコンテンツを追加しない。意味を正確に保つ

### YAML Frontmatter の扱い

- `name`: 英語のまま維持する
- `description`: 日本語に翻訳する。英語の description は削除し、日本語のみ記載する
- `translated_from`: `SKILL.md` を値として追加する。翻訳元ファイルを示すカスタムフィールド

### 文体

- 「だ・である」調（常体）を基本とする
- 箇条書きの項目は体言止めも可
- 元の SKILL.md が命令形（imperative）で書かれている場合、「〜する」「〜を行う」のような表現にする
- 「してください」「しましょう」などの丁寧語は使わない
