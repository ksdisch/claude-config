#!/usr/bin/env bash
# Folder-trust check/pre-accept for one repo root, so worker sessions launched into that
# repo (or any worktree under it) register immediately instead of parking on Claude Code's
# folder-trust dialog. Root trust covers worktrees (verified 2026-09-08).
#
# Default mode only REPORTS: exit 0 "already trusted", exit 2 "untrusted". Nothing is written.
# --write pre-accepts: sets exactly one key — projects.<root>.hasTrustDialogAccepted — in
# ~/.claude.json, the same key a human's "Yes, I trust" click writes. The orchestrate skill
# runs --write only after Kyle confirms once for that root (never unattended). Backs up
# first; writes via a temp file + atomic rename so a concurrent writer or a crash cannot
# leave the file truncated.
# Usage: pretrust.sh <abs repo root> [--write]
set -euo pipefail
root="${1:?abs repo root}"; mode="${2:-check}"
[ "$mode" = "check" ] || [ "$mode" = "--write" ] || { echo "usage: pretrust.sh <abs repo root> [--write]" >&2; exit 1; }
[ -d "$root" ] || { echo "refusing: $root is not a directory" >&2; exit 1; }
[ "${root#/}" != "$root" ] || { echo "refusing: $root is not absolute" >&2; exit 1; }
git -C "$root" rev-parse --show-toplevel >/dev/null 2>&1 || { echo "refusing: $root is not inside a git repo" >&2; exit 1; }
cfg="$HOME/.claude.json"
[ -f "$cfg" ] || { echo "refusing: $cfg not found" >&2; exit 1; }
if python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get('projects',{}).get(sys.argv[2],{}).get('hasTrustDialogAccepted') is True else 2)" "$cfg" "$root"; then
  echo "already trusted: $root"; exit 0
fi
if [ "$mode" = "check" ]; then
  echo "untrusted: $root (re-run with --write after Kyle confirms)"; exit 2
fi
bak="${TMPDIR:-/tmp}/claude.json.bak-$(date +%s)-$$"
cp "$cfg" "$bak"
python3 - "$cfg" "$root" <<'PY'
import json, os, sys, tempfile
cfg, root = sys.argv[1:3]
d = json.load(open(cfg))
d.setdefault("projects", {}).setdefault(root, {})["hasTrustDialogAccepted"] = True
fd, tmp = tempfile.mkstemp(prefix=".claude.json.", dir=os.path.dirname(cfg))
with os.fdopen(fd, "w") as f:
    json.dump(d, f, indent=2)
os.chmod(tmp, os.stat(cfg).st_mode & 0o777)
os.replace(tmp, cfg)
print(f"trusted: {root}")
PY
echo "backup: $bak"
