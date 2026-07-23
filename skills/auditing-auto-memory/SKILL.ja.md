---
name: auditing-auto-memory
description: 現在のプロジェクトの auto-memory ファイルをレビュー・整理・削減したいとき、陳腐化・矛盾・重複したエントリを確認したいときに使用する。
translated_from: SKILL.md
---

# Auto Memory の棚卸し

現在のプロジェクトの auto-memory ディレクトリをレビューし、もはや有効ではないエントリにフラグを立て、将来のセッションを誤らせる前にユーザーが整理できるようにする。このスキルは現在のプロジェクト自身のメモリのみを対象とし、他プロジェクトのメモリディレクトリには一切触れない。

## ワークフロー

### 1. メモリディレクトリを特定する

1. `settings.json` のいずれかのスコープで `autoMemoryDirectory` が設定されていれば、それを解決したうえで、そのディレクトリが現在のプロジェクト専用であることをユーザーに確認してから対象に含める — 共有設定や誤設定のパスだと他プロジェクトのメモリが混在する可能性があり、このスキルは他プロジェクトのメモリディレクトリに触れてはならない（概要を参照）。
2. そうでなければ、Claude Code と同じ方法で解決する: 現在の Git リポジトリから導出される `~/.claude/projects/<project>/memory/`（またはアクティブなプロファイルの相当ディレクトリ）を使う。

ディレクトリが存在しない、またはメモリファイルが1つもない場合は、棚卸しの対象がない旨をユーザーに伝えて終了する。

### 2. 収集する

ディレクトリ内の全メモリファイルと `MEMORY.md` を読み込む。各ファイルの frontmatter は `type`（`user`、`feedback`、`project`、`reference` のいずれか）を宣言している。

### 3. タイプ別に検証する

**`project`** — 毎回、全件レビューする:

- 本文中の具体的で検証可能な参照（ファイルパス、シンボル名、ブランチ名、コマンド名）を抽出し、それぞれを `grep`/`fd`/`git log` などで照合する。
- 「調査中」「暫定的に」「現時点では」のような婉曲的・時点限定的な表現は、参照が今も解決するかどうかに関わらず「要再確認」としてフラグを立てる。
- もはや解決しない参照（削除されたファイル、リネームされたシンボル、消えたブランチ）は「矛盾」としてフラグを立てる — 黙って削除しない。

**`user`、`feedback`、`reference`** — デフォルトでは信頼し、全件の再検証は行わない。次の場合のみフラグを立てる:

- **重複（superseded）** — メモリの内容がその後 `SKILL.md`、`CLAUDE.md`、`AGENTS.md`、`.claude/rules/*.md` のいずれかに正式化されており、メモリが冗長になっている。
- **矛盾（contradicted）** — 同じディレクトリ内の別のメモリファイルと内容が食い違っている。

`user`/`feedback`/`reference` の主張そのものが今も正しいかどうかは、この2つのチェックを超えて調査しない — それはこのスキルの対象外。

### 4. 検出結果を提示する

フラグが立った候補一覧のみを一括で提示する（チェックした全ファイルではない）。各項目について: ファイル、理由（矛盾／重複／陳腐化した表現／重複エントリ）、見つかった根拠、提案するアクション（削除、内容更新、統合、現状維持）を示す。

```text
## Auto-memory audit

Checked N files, M flagged.

1. project_sync_template_mise_lock.md — stale-language ("investigating")
   Proposed: ask user for current status, update or delete.

2. project_resolving_issue_model_split.md — superseded
   Now documented in skills/resolving-github-issue/SKILL.md.
   Proposed: delete.

Apply all? Reply with adjustments (keep an item, edit the action, override
the reason) or approve as-is.
```

ユーザーの返答を待ってから適用する。

### 5. 適用する

承認された各アクションについて:

- **削除** — メモリファイルを削除し、`MEMORY.md` から該当するポインタ行を削除する。
- **内容更新** — メモリファイルの本文（内容が変わった場合は frontmatter の `description` も）を編集し、一行要約が変わった場合は対応する `MEMORY.md` の行も更新する。
- **統合** — 内容を統合先のエントリに畳み込み、統合元のファイルとその `MEMORY.md` の行を削除する。
- **現状維持** — 変更しない。

解決したメモリディレクトリがこの Git リポジトリの内側にある場合（カスタムの `autoMemoryDirectory` がリポジトリ配下を指しているとあり得る）、変更はコミットせずユーザー自身の `committing-changes` ステップに委ねる。リポジトリの外側にある場合（デフォルトのケース）はコミット自体が不要。

### 6. 報告する

チェックしたファイル数、フラグが立った数、実施したアクションを1アクション1行で要約する。

## 注意事項

- `project` タイプのメモリは毎回全件チェックする。`user`/`feedback`/`reference` は矛盾または重複が見つかったときのみフラグを立て、内容の正しさそのものを再検証することはない。
- 一括承認とし、1件ずつの確認は行わない — 候補一覧を一度に提示する。
- ステップ4のユーザー承認なしに、メモリファイルを黙って削除・編集しない。
