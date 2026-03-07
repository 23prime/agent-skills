---
name: converting-pdf-to-markdown
description: markitdown を使って PDF ファイルを Markdown に変換する。PDF を Markdown に変換したい、PDF からテキストを抽出したい、PDF ドキュメントを読みやすい Markdown 形式に変換したい場合に使用する。
translated_from: SKILL.md
---

# PDF から Markdown への変換

Microsoft の markitdown ライブラリを使った軽量な PDF → Markdown 変換。

## 前提条件

- [uv](https://docs.astral.sh/uv/) がインストールされていること。

スクリプトは PEP 723 インラインメタデータで依存関係を宣言しており、`uv run` で実行するため、
手動でのパッケージインストールは不要。

## ワークフロー

### ステップ 1: ページ数と目次の確認

変換前に目次抽出スクリプトを実行する:

```bash
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/extract_toc.py" input.pdf
```

出力は `page_count`（ページ数）と `toc`（レベル・タイトル・ページを含むブックマークエントリ）を含む JSON。

### ステップ 2: 分割の要否を判断

- **100 ページ以下**: ファイル全体を変換する。ステップ 3 へ進む。
- **100 ページ超かつ目次あり**: 目次の構造をユーザーに提示し、トップレベルの見出しで分割することを推奨する。ユーザーの確認後、以下で分割する:

```bash
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/split_pdf.py" input.pdf
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/split_pdf.py" input.pdf -o output_dir/
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/split_pdf.py" input.pdf -l 2  # レベル 2 見出しで分割
```

番号付き PDF ファイル（例: `01-introduction.pdf`）がサブディレクトリに作成される。各パートをステップ 3 で個別に変換する。

- **100 ページ超かつ目次なし**: 自動分割用のブックマークがない旨をユーザーに伝える。そのまま変換するか、手動でページ範囲を指定するよう促す。

### ステップ 3: 変換

```bash
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/convert_pdf.py" input.pdf
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/convert_pdf.py" input.pdf -o output.md
```

デフォルトの出力先は同ディレクトリの `input.md`。カスタムパスを指定する場合は `-o` を使用する。

### ステップ 4: 改行の整理

PDF のテキストは表示上の折り返しで不要な改行が入る。変換後は必ず整理スクリプトを実行する:

```bash
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/clean_linebreaks.py" output.md
uv run "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/converting-pdf-to-markdown/scripts/clean_linebreaks.py" output.md -o cleaned.md
```

`-o` を省略した場合はファイルを上書き。見出し・リスト・コードブロック・テーブル・段落区切りを保持しながら、折り返し行を結合する。

### ステップ 5: レビュー

出力結果を確認する:

- 見出しの崩れや書式のアーティファクト
- 不要なページ番号やヘッダー・フッター
- テーブルの書式の問題
