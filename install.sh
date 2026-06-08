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

LINKS=(commands skills agents CLAUDE.md statusline-command.sh)

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
