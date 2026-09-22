#!/usr/bin/env python3
"""Install the wayfinder-map Stop hook into ~/.claude/settings.json. One-shot, idempotent.

    python3 install_hook.py              back up, then append the hook unless it is already there
    python3 install_hook.py --dry-run    print the resulting Stop array; write nothing
    python3 install_hook.py --settings <file> [--backups <dir>]   for tests

The hook re-renders any stale `map.html` under `<cwd>/.scratch/*/` at the end of
every turn. It is the backstop; sessions still run the renderer after each
claim, resolve, or new ticket.

The settings file is machine-local and hand-maintained, so this backs it up
first, writes atomically (temp file then rename), leaves every other key
untouched, and refuses to touch a file it cannot parse.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

COMMAND = "python3 ~/.claude/skills/wayfinder-map/scripts/render_map.py --hook"
ENTRY = {"hooks": [{"type": "command", "command": COMMAND}]}


def installed(stop: list) -> bool:
    return any(
        isinstance(group, dict) and any(
            isinstance(h, dict) and h.get("command") == COMMAND for h in group.get("hooks", [])
        )
        for group in stop
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Install the wayfinder-map Stop hook.")
    ap.add_argument("--settings", type=Path, default=Path.home() / ".claude" / "settings.json")
    ap.add_argument("--backups", type=Path, default=Path.home() / ".claude" / "hooks" / "backups")
    ap.add_argument("--dry-run", action="store_true", help="print the resulting Stop array; write nothing")
    args = ap.parse_args(argv)

    try:
        settings = json.loads(args.settings.read_text(encoding="utf-8")) if args.settings.exists() else {}
    except ValueError as e:
        print(f"{args.settings} is not valid JSON ({e}); nothing touched", file=sys.stderr)
        return 1
    if not isinstance(settings, dict):
        print(f"{args.settings} is not a JSON object; nothing touched", file=sys.stderr)
        return 1

    stop = settings.setdefault("hooks", {}).setdefault("Stop", [])
    if installed(stop):
        print(f"wayfinder-map Stop hook already installed in {args.settings}; nothing changed")
        return 0
    stop.append(ENTRY)

    if args.dry_run:
        print(json.dumps(stop, indent=2, ensure_ascii=False))
        return 0

    if args.settings.exists():
        args.backups.mkdir(parents=True, exist_ok=True)
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = args.backups / f"settings.json.{stamp}"
        shutil.copy2(args.settings, backup)
        print(f"backed up to {backup}")

    args.settings.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=args.settings.parent, prefix=".settings.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(settings, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, args.settings)
    print(f"installed wayfinder-map Stop hook in {args.settings}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
