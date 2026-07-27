#!/usr/bin/env python3
"""Inject harvested figures into a paper-eli5 markdown file.

Usage:
    python3 inject.py md <in.md> <out.md> <images.json>

images.json maps figure number (as a string key) to a path relative to the
markdown file, e.g. {"1": "figures/paper/fig-01.png"}.

Only placeholder lines change. Caption lines, prose, and the total line count
are untouched, so paper-eli5's structural verification still holds.
"""
import argparse
import json
import re
import sys

PLACEHOLDER = re.compile(
    r"^(?P<img>!)?\[Figure\s+(?P<num>\d+)\](?:\((?P<url>[^)]*)\))?$"
)


def inject_markdown(text, images):
    """Return text with each figure placeholder replaced by an image reference."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = PLACEHOLDER.match(line.strip())
        if not m:
            continue
        num = int(m.group("num"))
        path = images.get(num) or images.get(str(num))
        if not path:
            continue
        lines[i] = f"![Figure {num}]({path})"
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["md", "html"])
    ap.add_argument("infile")
    ap.add_argument("outfile")
    ap.add_argument("images")
    args = ap.parse_args(argv)

    with open(args.images, encoding="utf-8") as fh:
        images = {int(k): v for k, v in json.load(fh).items()}
    with open(args.infile, encoding="utf-8") as fh:
        text = fh.read()

    if args.mode == "md":
        out = inject_markdown(text, images)
    else:
        from inject_html import inject_html

        out = inject_html(text, images)

    with open(args.outfile, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"injected {len(images)} figures into {args.outfile}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
