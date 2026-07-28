#!/usr/bin/env python3
"""Extract figure slots from a paper-eli5 markdown file into a JSON ledger.

Usage:
    python3 ledger.py <path-to-eli5.md> [-o ledger.json]

A figure slot is a line that is *only* a figure placeholder, in one of:
    [Figure 7]
    ![Figure 4](https://example.com/img.png)

An inline mention such as "(Figure 5)" inside a sentence is not a slot.
"""
import argparse
import json
import re
import sys

PLACEHOLDER = re.compile(
    r"^(?P<img>!)?\[Figure\s+(?P<num>\d+)\](?:\((?P<url>[^)]*)\))?$"
)
CAPTION = re.compile(r"^Figure\s+(?P<num>\d+):\s*(?P<text>.+)$")


def build_ledger(text):
    """Return a list of figure-slot dicts, in document order."""
    lines = text.split("\n")

    captions = {}
    for line in lines:
        m = CAPTION.match(line.strip())
        if m:
            captions.setdefault(int(m.group("num")), m.group("text").strip())

    entries = []
    for i, line in enumerate(lines):
        m = PLACEHOLDER.match(line.strip())
        if not m:
            continue
        num = int(m.group("num"))
        entries.append(
            {
                "num": num,
                "line": i,
                "raw": line,
                "existing_url": m.group("url") or None,
                "caption": captions.get(num, ""),
                "status": "pending",
            }
        )
    return entries


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("markdown")
    ap.add_argument("-o", "--out", default="-")
    args = ap.parse_args(argv)

    with open(args.markdown, encoding="utf-8") as fh:
        entries = build_ledger(fh.read())

    payload = json.dumps({"figures": entries}, indent=2, ensure_ascii=False)
    if args.out == "-":
        print(payload)
    else:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(payload + "\n")
    print(f"{len(entries)} figure slots", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
