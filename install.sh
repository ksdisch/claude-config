#!/usr/bin/env bash
# Install this repo's Claude Code content into ~/.claude by symlinking.
# Idempotent: re-running is safe. Any existing real (non-symlink) target is
# backed up to <name>.pre-claude-config.<timestamp> before linking.
#
#   git clone git@github.com:ksdisch/claude-config.git ~/Projects/claude-config
#   ~/Projects/claude-config/install.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CL="$HOME/.claude"
mkdir -p "$CL"

# Warn when linking from a non-integration branch: ~/.claude will reflect
# unmerged work on this branch until it lands on main.
branch="$(git -C "$REPO" branch --show-current 2>/dev/null || true)"
if [ -n "$branch" ] && [ "$branch" != "main" ] && [ "$branch" != "master" ]; then
  echo "⚠️  WARNING: linking ~/.claude from branch '$branch' (not main)."
  echo "    Your live Claude Code config now reflects unmerged work on this branch."
  echo
fi

# Link every git-tracked top-level entry EXCEPT repo-meta/docs (DENY). Sourcing
# the set from `git ls-tree` (not a raw `ls`) means anything untracked or
# gitignored — secrets, *.bak backups, machine-local files — can NEVER be linked
# into ~/.claude. Add new top-level docs/meta files to DENY so they aren't linked.
DENY=(.gitignore README.md install.sh BACKLOG.md docs)
LINKS=()
while IFS= read -r name; do
  for d in "${DENY[@]}"; do [ "$name" = "$d" ] && continue 2; done
  LINKS+=("$name")
done < <(git -C "$REPO" ls-tree --name-only HEAD)

if [ "${#LINKS[@]}" -eq 0 ]; then
  echo "error: no git-tracked items to link — run install.sh from inside the git checkout." >&2
  exit 1
fi

for item in "${LINKS[@]}"; do
  src="$REPO/$item"
  dst="$CL/$item"
  [ -e "$src" ] || { echo "– skip $item (not in repo)"; continue; }

  if [ -L "$dst" ]; then
    cur="$(readlink "$dst")"
    if [ "$cur" = "$src" ]; then echo "✓ $item already linked"; continue; fi
    echo "› relinking $item (was -> $cur)"; rm "$dst"
  elif [ -e "$dst" ]; then
    bak="$dst.pre-claude-config.$(date +%Y%m%d-%H%M%S)"
    echo "› backing up existing $item -> $(basename "$bak")"
    mv "$dst" "$bak"
  fi

  ln -s "$src" "$dst"
  echo "✓ linked $item -> $src"
done

echo
echo "Done. ~/.claude now points at $REPO"
