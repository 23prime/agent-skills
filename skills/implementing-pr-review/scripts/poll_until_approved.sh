#!/usr/bin/env bash
# Usage: poll_until_approved.sh <PR_NUMBER> <OWNER/REPO>
# Polls until the PR is approved or TIMEOUT_HOURS have elapsed.
# Every MENTION_INTERVAL_MIN minutes, posts a comment asking @coderabbitai to approve.
set -euo pipefail

PR_NUMBER="${1:?PR_NUMBER required}"
REPO="${2:?OWNER/REPO required}"

readonly POLL_INTERVAL_SEC=60                                         # 1 minute
readonly TIMEOUT_HOURS=4
readonly MAX_ATTEMPTS=$(( TIMEOUT_HOURS * 60 * 60 / POLL_INTERVAL_SEC ))

for i in $(seq 1 "$MAX_ATTEMPTS"); do
  sleep "$POLL_INTERVAL_SEC"

  DECISION=$(gh pr view "$PR_NUMBER" -R "$REPO" \
    --json reviewDecision --jq .reviewDecision)
  [ "$DECISION" = "APPROVED" ] && { echo "PR approved!"; exit 0; }

  NEW=$(gh pr-review review view "$PR_NUMBER" -R "$REPO" \
    | jq '[.reviews[]?.comments[]?
           | select(.is_resolved == false
                    and .is_outdated == false
                    and (.thread_comments | length) == 0)]
          | length')
  [ "$NEW" -gt 0 ] && { echo "Found $NEW new comment(s), restarting."; exit 2; }
done

gh pr comment "$PR_NUMBER" -R "$REPO" --body "\`@coderabbitai\` resolve"
echo "Timed out after ${TIMEOUT_HOURS} hours without approval."
exit 1
