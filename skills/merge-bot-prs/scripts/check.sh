#!/usr/bin/env bash
# Check mise-upgrade-bot PRs from notifications: unmerged + all checks passing
set -euo pipefail

BOT_USER="${BOT_USER:-mise-upgrade-bot[bot]}"
OUTPUT_FILE="${OUTPUT_FILE:-/tmp/merge-bot-ok-prs.txt}"

echo "Fetching notifications..."
_tmp_notifications=$(mktemp)
trap 'rm -f "$_tmp_notifications"' EXIT
echo "[]" > "$_tmp_notifications"
page=1
while true; do
  page_data=$(gh api "notifications?all=true&per_page=100&page=$page")
  count=$(echo "$page_data" | jq 'length')
  jq -s '.[0] + .[1]' "$_tmp_notifications" <(echo "$page_data") > "${_tmp_notifications}.new"
  mv "${_tmp_notifications}.new" "$_tmp_notifications"
  [[ "$count" -lt 100 ]] && break
  page=$((page + 1))
done
notifications=$(cat "$_tmp_notifications")

pr_urls=$(echo "$notifications" | jq -r '
  .[] |
  select(.subject.type == "PullRequest") |
  .subject.url
' | sort -u)

if [[ -z "$pr_urls" ]]; then
  echo "No PR notifications found."
  exit 0
fi

echo ""
echo "=== $BOT_USER PR Check Results ==="
echo ""

ok_prs=()

while IFS= read -r api_url; do
  pr=$(gh api "$api_url" 2>/dev/null) || continue

  author=$(echo "$pr" | jq -r '.user.login')
  [[ "$author" != "$BOT_USER" ]] && continue

  repo=$(echo "$pr" | jq -r '.base.repo.full_name')
  pr_number=$(echo "$pr" | jq -r '.number')
  title=$(echo "$pr" | jq -r '.title')
  state=$(echo "$pr" | jq -r '.state')
  merged=$(echo "$pr" | jq -r '.merged')
  html_url=$(echo "$pr" | jq -r '.html_url')

  if [[ "$merged" == "true" || "$state" == "closed" ]]; then
    continue
  fi

  head_sha=$(echo "$pr" | jq -r '.head.sha')

  check_runs=$(gh api "repos/$repo/commits/$head_sha/check-runs" 2>/dev/null) || {
    echo "NG  [$repo#$pr_number] $title (failed to fetch checks)"
    echo "    $html_url"
    continue
  }

  total=$(echo "$check_runs" | jq '[.check_runs[] | select(.status == "completed")] | length')
  failed=$(echo "$check_runs" | jq '[.check_runs[] | select(.status == "completed" and .conclusion != "success" and .conclusion != "skipped" and .conclusion != "neutral")] | length')
  pending=$(echo "$check_runs" | jq '[.check_runs[] | select(.status != "completed")] | length')

  if [[ "$total" -gt 0 && "$failed" -eq 0 && "$pending" -eq 0 ]]; then
    echo "OK  [$repo#$pr_number] $title"
    echo "    $html_url"
    ok_prs+=("$repo/$pr_number")
  elif [[ "$total" -eq 0 ]]; then
    echo "NG  [$repo#$pr_number] $title (no completed checks)"
    echo "    $html_url"
  else
    echo "NG  [$repo#$pr_number] $title (failed=$failed, pending=$pending)"
    echo "    $html_url"
  fi
done <<< "$pr_urls"

echo ""

if [[ ${#ok_prs[@]} -eq 0 ]]; then
  echo "No OK PRs found."
  exit 0
fi

printf '%s\n' "${ok_prs[@]}" > "$OUTPUT_FILE"
echo "OK PRs saved to $OUTPUT_FILE (${#ok_prs[@]} PRs)"
