#!/usr/bin/env bash
# Usage: clean_topic_branch.sh [branch]
# Switches to the default branch, pulls, and deletes the topic branch
# locally and remotely. If no branch is specified, uses the current branch.
set -euo pipefail

TOPIC="${1:-$(git rev-parse --abbrev-ref HEAD)}"
DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null \
  | sed 's|refs/remotes/origin/||')
DEFAULT="${DEFAULT:-main}"

if [ "$TOPIC" = "$DEFAULT" ]; then
  echo "Already on default branch '$DEFAULT', nothing to clean."
  exit 1
fi

echo "Switching to $DEFAULT..."
git checkout "$DEFAULT"
git pull

echo "Deleting local branch '$TOPIC'..."
git branch -d "$TOPIC"

echo "Deleting remote branch '$TOPIC' (if exists)..."
git push origin --delete "$TOPIC" 2>/dev/null || true
git fetch --prune

echo "Done."
