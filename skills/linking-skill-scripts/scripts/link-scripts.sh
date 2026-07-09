#!/usr/bin/env bash
# Usage: link-scripts.sh [target_dir]
# Symlinks every skills/*/scripts/*.sh in this repo into target_dir
# (default ~/.local/bin) as as-<name> (no .sh extension), so skills can
# invoke them via PATH instead of expanding CLAUDE_CONFIG_DIR paths.
# Removes stale as-* symlinks in target_dir that point back into this
# repo but whose source script no longer exists. Never touches as-*
# entries that point elsewhere.
set -euo pipefail
shopt -s nullglob

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TARGET_DIR="${1:-$HOME/.local/bin}"

mkdir -p "$TARGET_DIR"

wanted_links=""
for src in "$REPO_ROOT"/skills/*/scripts/*.sh; do
  name="$(basename "$src" .sh)"
  link="$TARGET_DIR/as-$name"
  wanted_links="$wanted_links$link"$'\n'
  ln -sf "$src" "$link"
  echo "linked: $link -> $src"
done

for link in "$TARGET_DIR"/as-*; do
  [ -L "$link" ] || continue
  case "$wanted_links" in
    *"$link"$'\n'*) continue ;;
  esac
  resolved="$(readlink "$link")"
  case "$resolved" in
    "$REPO_ROOT"/skills/*/scripts/*.sh)
      rm -f "$link"
      echo "removed stale: $link"
      ;;
  esac
done

case ":$PATH:" in
  *":$TARGET_DIR:"*) ;;
  *) echo "warning: $TARGET_DIR is not on your PATH. Add it in your shell profile (e.g. export PATH=\"$TARGET_DIR:\$PATH\")." ;;
esac
