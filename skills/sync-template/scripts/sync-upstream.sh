#!/usr/bin/env bash
# Sync main branch from upstream and push to origin.
# Usage: sync-upstream.sh <repo-dir>

set -euo pipefail

REPO_DIR="${1:?Usage: sync-upstream.sh <repo-dir>}"

if [ ! -d "$REPO_DIR" ]; then
  echo "[ERROR] Directory not found: $REPO_DIR" >&2
  exit 1
fi

cd "$REPO_DIR"
echo "[INFO] Syncing $(basename "$REPO_DIR")..."

git pull origin main
git fetch upstream
git merge upstream/main
git push origin main

echo "[INFO] Cleaning up sync-upstream-* branches..."
# Delete local branches matching sync-upstream-*
git branch --list 'sync-upstream-*' | while read -r branch; do
  git branch -d "$branch" && echo "[INFO] Deleted local branch: $branch" || \
    git branch -D "$branch" && echo "[INFO] Force-deleted local branch: $branch"
done

# Delete remote branches matching sync-upstream-*
git branch -r --list 'origin/sync-upstream-*' | sed 's|origin/||' | while read -r branch; do
  git push origin --delete "$branch" && echo "[INFO] Deleted remote branch: $branch" || echo "[WARN] Could not delete remote branch: $branch (may already be gone)"
done

git fetch --prune
echo "[INFO] Done: $(basename "$REPO_DIR")"
