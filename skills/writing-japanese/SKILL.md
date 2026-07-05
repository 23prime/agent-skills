---
name: writing-japanese
description: Write and review Japanese prose in technical documents (README, design docs, SKILL.md) following consistent punctuation, half-width/full-width, and katakana loanword conventions. Use when writing or reviewing Japanese text.
---

# Writing Japanese

Write Japanese technical prose with consistent punctuation, half-width/full-width usage, and katakana loanword spelling.

## Rules

### Punctuation

- Add a closing period（句点）as a rule, including in list items and table cells.
- Omit the period when a line is a bare noun or ends in 体言止め (a listing of nouns, not a full sentence).
- Keep each sentence as short as possible. There is no fixed rule for comma（読点）placement.

### Prose style（文体）

- Use a consistent です・ます調 or だ・である調 within documents of the same kind in the repository. Do not mix the two within one document type.

### Spacing between Japanese and alphanumerics（分かち書き）

- Insert a space between Japanese text and adjacent half-width alphanumeric characters as a rule.

### Half-width and full-width

| Target | Rule |
| --- | --- |
| Alphanumeric characters | Half-width. |
| Symbols attached to alphanumerics (delimiters `-` `_` `+`, units `$` `%`, paths `/` `\`, others `#` `@` `&` `=` `~` `^` `\|` `<` `>`) | Half-width. |
| Symbols inside code blocks / inline code | Keep as-is, always half-width. |
| Punctuation and brackets within Japanese sentences (`！` `？` `：` `；` `（）` `「」` `【】` `『』` `…`) | Full-width. This includes short fragments, such as a colon after a list-item label (e.g. `あり：サーバー`, not `あり: サーバー`). |
| Quotations within Japanese sentences | Use `「」`, not `"` or `'`. |
| Dashes | Avoid. If unavoidable, use half-width `--`. |
| Range tilde | Use full-width `〜`. |

### Katakana loanwords

Follow [外来語の表記 留意事項その2（文化庁）](https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/gairai/honbun06.html).

- Write long vowels with the long vowel mark「ー」as a rule.
- Words ending in English -er / -or / -ar take an "a"-row long vowel with 「ー」as a rule, though established usage may omit it.
  - With「ー」: サーバー、ユーザー、メンテナー、コンピューター、エレベーター
  - Without「ー」by convention: コンテナ、ディレクトリ、フォルダ

## Review checklist

When reviewing existing Japanese text, check in this order:

1. Periods are present on sentences, and correctly omitted on 体言止め lines.
2. Sentences are kept short.
3. です・ます調 or だ・である調 is consistent within documents of the same kind.
4. Spaces are present between Japanese text and adjacent alphanumerics.
5. Half-width/full-width usage matches the table above.
6. Katakana loanwords follow the long-vowel conventions.
