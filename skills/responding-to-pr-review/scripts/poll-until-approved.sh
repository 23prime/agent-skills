#!/usr/bin/env bash
# Usage: poll-until-approved.sh <PR_NUMBER> <OWNER/REPO>
# Polls until the PR is approved or TIMEOUT_HOURS have elapsed.
# Exit codes:
#   0 - approved
#   1 - timed out after TIMEOUT_HOURS
#   2 - found a brand-new unresolved thread (never replied to) -> restart from Step 1
#   3 - found a thread we already replied to that has stayed unresolved for
#       STALL_TIMEOUT_MIN minutes -> needs a decision from the user
set -euo pipefail

PR_NUMBER="${1:?PR_NUMBER required}"
REPO="${2:?OWNER/REPO required}"

readonly POLL_INTERVAL_SEC=60                                         # 1 minute
readonly TIMEOUT_HOURS=4
readonly MAX_ATTEMPTS=$(( TIMEOUT_HOURS * 60 * 60 / POLL_INTERVAL_SEC ))
readonly STALL_TIMEOUT_MIN=5
readonly STALL_TIMEOUT_SEC=$(( STALL_TIMEOUT_MIN * 60 ))

declare -A stalled_since

for i in $(seq 1 "$MAX_ATTEMPTS"); do
  sleep "$POLL_INTERVAL_SEC"

  DECISION=$(gh pr view "$PR_NUMBER" -R "$REPO" \
    --json reviewDecision --jq .reviewDecision)
  [ "$DECISION" = "APPROVED" ] && { echo "PR approved!"; exit 0; }

  THREADS=$(gh pr-review review view "$PR_NUMBER" -R "$REPO")

  NEW=$(echo "$THREADS" | jq '[.reviews[]?.comments[]?
         | select(.is_resolved == false
                  and .is_outdated == false
                  and (.thread_comments | length) == 0)]
        | length')
  [ "$NEW" -gt 0 ] && { echo "Found $NEW new comment(s), restarting."; exit 2; }

  # Threads we already replied to (thread_comments non-empty) that are still
  # unresolved: CodeRabbit sometimes doesn't auto-resolve after our reply.
  CANDIDATES=$(echo "$THREADS" | jq -c '[.reviews[]?.comments[]?
         | select(.is_resolved == false
                  and .is_outdated == false
                  and (.thread_comments | length) > 0)
         | {thread_id, path, line,
            latest_author: (.thread_comments[-1].author_login // ""),
            latest_body: (.thread_comments[-1].body // "")}]')

  CANDIDATE_IDS=$(echo "$CANDIDATES" | jq -r '.[].thread_id')

  # Drop bookkeeping for threads that resolved or dropped out since last check.
  for id in "${!stalled_since[@]}"; do
    if ! grep -qxF "$id" <<<"$CANDIDATE_IDS"; then
      unset "stalled_since[$id]"
    fi
  done

  NOW=$(date +%s)
  STUCK="[]"
  while IFS= read -r item; do
    [ -z "$item" ] && continue
    id=$(echo "$item" | jq -r '.thread_id')
    if [ -z "${stalled_since[$id]:-}" ]; then
      stalled_since[$id]=$NOW
    elif (( NOW - stalled_since[$id] >= STALL_TIMEOUT_SEC )); then
      STUCK=$(echo "$STUCK" | jq --argjson item "$item" '. + [$item]')
    fi
  done < <(echo "$CANDIDATES" | jq -c '.[]')

  STUCK_COUNT=$(echo "$STUCK" | jq 'length')
  if [ "$STUCK_COUNT" -gt 0 ]; then
    echo "Found $STUCK_COUNT thread(s) unresolved ${STALL_TIMEOUT_MIN}+ min after our reply:"
    echo "$STUCK" | jq .
    exit 3
  fi
done

echo "Timed out after ${TIMEOUT_HOURS} hours without approval."
exit 1
