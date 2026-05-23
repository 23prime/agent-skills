#!/usr/bin/env bash
# Approve and merge PRs listed in OUTPUT_FILE (one "owner/repo/pr_number" per line)
set -euo pipefail

OUTPUT_FILE="${OUTPUT_FILE:-/tmp/merge-bot-ok-prs.txt}"

if [[ ! -f "$OUTPUT_FILE" ]]; then
  echo "No OK PR list found at $OUTPUT_FILE. Run check.sh first."
  exit 1
fi

mapfile -t ok_prs < "$OUTPUT_FILE"

if [[ ${#ok_prs[@]} -eq 0 ]]; then
  echo "No PRs to merge."
  exit 0
fi

echo "=== Approving and Merging ${#ok_prs[@]} PR(s) ==="
echo ""

for entry in "${ok_prs[@]}"; do
  repo="${entry%/*}"
  pr_number="${entry##*/}"

  echo "--- $repo#$pr_number ---"

  echo "  Approving..."
  gh pr review "$pr_number" --repo "$repo" --approve --body "LGTM" 2>&1 | sed 's/^/  /'

  echo "  Merging..."
  gh pr merge "$pr_number" --repo "$repo" --merge 2>&1 | sed 's/^/  /'

  echo "  Done."
  echo ""
done

echo "All done."
rm -f "$OUTPUT_FILE"
