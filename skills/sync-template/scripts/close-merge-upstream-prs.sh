#!/usr/bin/env bash
# Close stale "Merge upstream changes" PRs for repos already synced directly.
# Usage: close-merge-upstream-prs.sh <repo-name> [<repo-name> ...]

set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 <repo-name> [<repo-name> ...]" >&2
  exit 1
fi

declare -a REPOS=("$@")
declare -a RESULTS=()
declare -a NOTES=()

for repo in "${REPOS[@]}"; do
  repo_path="$HOME/develop/$repo"
  echo "--- Checking $repo ---" >&2

  numbers=$(cd "$repo_path" && gh pr list --state open --search "Merge upstream changes in:title" --json number --jq '.[].number')

  if [[ -z "$numbers" ]]; then
    RESULTS+=("NONE")
    NOTES+=("")
    continue
  fi

  closed=()
  while IFS= read -r number; do
    (cd "$repo_path" && gh pr close "$number" >/dev/null)
    closed+=("#$number")
  done <<< "$numbers"

  RESULTS+=("CLOSED")
  IFS=,; NOTES+=("${closed[*]}"); unset IFS
done

# output machine-readable results: REPO<TAB>RESULT<TAB>NOTES
echo "---RESULTS---"
for i in "${!REPOS[@]}"; do
  printf '%s\t%s\t%s\n' "${REPOS[$i]}" "${RESULTS[$i]}" "${NOTES[$i]}"
done
