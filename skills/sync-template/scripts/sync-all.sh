#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGETS_FILE="${1:-}"

if [[ -z "$TARGETS_FILE" ]]; then
  echo "Usage: $0 <targets-file>" >&2
  exit 1
fi

if [[ ! -f "$TARGETS_FILE" ]]; then
  echo "ERROR: targets file not found: $TARGETS_FILE" >&2
  exit 1
fi

declare -a REPOS=()
declare -a RESULTS=()
declare -a NOTES=()

while IFS= read -r line; do
  # strip comments and blank lines
  line="${line%%#*}"
  line="${line//[[:space:]]/}"
  [[ -z "$line" ]] && continue
  REPOS+=("$line")
done < "$TARGETS_FILE"

for repo in "${REPOS[@]}"; do
  repo_path="$HOME/develop/$repo"
  echo "--- Syncing $repo ---" >&2
  exit_code=0
  output=$("$SCRIPT_DIR/sync-upstream.sh" "$repo_path" 2>&1) || exit_code=$?

  if [[ $exit_code -eq 0 ]]; then
    RESULTS+=("OK")
    NOTES+=("")
  else
    RESULTS+=("FAILED")
    # pick the most informative error line
    if echo "$output" | grep -q "CONFLICT"; then
      NOTES+=("Merge conflict in $(echo "$output" | grep 'CONFLICT' | head -1 | awk '{print $NF}')")
    elif echo "$output" | grep -q "error: failed to push"; then
      last_hook_error=$(echo "$output" | grep "ERROR task failed" | head -1 || true)
      failing_cmd=$(echo "$output" | grep ": command not found" | head -1 | sed 's/.*: \(.*\): command not found/\1/' || true)
      if [[ -n "$failing_cmd" ]]; then
        NOTES+=("pre-push hook: \`$failing_cmd\` not found")
      else
        NOTES+=("$(echo "$output" | tail -1)")
      fi
    elif echo "$output" | grep -qi "permission denied\|could not read.*authentication"; then
      NOTES+=("Auth/SSH error")
    else
      NOTES+=("$(echo "$output" | tail -1)")
    fi
  fi
done

# output machine-readable results: REPO<TAB>RESULT<TAB>NOTES
echo "---RESULTS---"
for i in "${!REPOS[@]}"; do
  printf '%s\t%s\t%s\n' "${REPOS[$i]}" "${RESULTS[$i]}" "${NOTES[$i]}"
done
