#!/usr/bin/env bash
# Pre-accept Claude Code's folder-trust dialog for one repo root, so worker sessions
# launched into that repo (or any worktree under it) register immediately instead of
# parking on the dialog. Writes exactly one key — projects.<root>.hasTrustDialogAccepted —
# in ~/.claude.json, the same key Claude Code writes when a human clicks "Yes, I trust".
# Authorized by Kyle for the orchestrate skill on 2026-09-08. Idempotent. Backs up first.
# Usage: pretrust.sh <abs repo root>
set -euo pipefail
root="${1:?abs repo root}"
[ -d "$root" ] || { echo "refusing: $root is not a directory" >&2; exit 1; }
[ "${root#/}" != "$root" ] || { echo "refusing: $root is not absolute" >&2; exit 1; }
git -C "$root" rev-parse --show-toplevel >/dev/null 2>&1 || { echo "refusing: $root is not inside a git repo" >&2; exit 1; }
cfg="$HOME/.claude.json"
[ -f "$cfg" ] || { echo "refusing: $cfg not found" >&2; exit 1; }
bak="${TMPDIR:-/tmp}/claude.json.bak-$(date +%s)"
cp "$cfg" "$bak"
python3 - "$cfg" "$root" <<'PY'
import json, sys
cfg, root = sys.argv[1:3]
d = json.load(open(cfg))
e = d.setdefault("projects", {}).setdefault(root, {})
if e.get("hasTrustDialogAccepted") is True:
    print(f"already trusted: {root}")
else:
    e["hasTrustDialogAccepted"] = True
    json.dump(d, open(cfg, "w"), indent=2)
    print(f"trusted: {root}")
PY
echo "backup: $bak"
