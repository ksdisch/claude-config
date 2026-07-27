#!/usr/bin/env python3
"""Join the ledger, the captured files, and the Tier 1 checks into contact-sheet entries.

Usage:
    python3 entries.py <ledger.json> <figures-dir> [--checks checks.json] [-o entries.json]

`contactsheet.py` consumes a flat JSON array of
`{"num": N, "path": "...", "caption": "...", "verdict": "...", "reason": "..."}`,
but that shape lives in three places: captions come from the ledger, paths from
the figures directory, and verdicts from the Tier 1 checks. This composes them.

Every ledger slot produces an entry, so an uncaptured figure still appears on
the sheet as `missing` rather than silently vanishing from the review.
"""
import argparse
import json
import os
import re
import sys

FIG_FILE = re.compile(r"^fig-(?P<num>\d+)\.(?:png|jpe?g)$", re.I)


def index_figures(figures_dir):
    """Map figure number -> path for fig-NN.{png,jpg} files in figures_dir."""
    found = {}
    if not os.path.isdir(figures_dir):
        return found
    for name in sorted(os.listdir(figures_dir)):
        m = FIG_FILE.match(name)
        if not m:
            continue
        found[int(m.group("num"))] = os.path.join(figures_dir, name)
    return found


def index_checks(checks):
    """Map figure number -> (verdict, reason) from a checks.py payload."""
    verdicts = {}
    for r in (checks or {}).get("results", []):
        m = FIG_FILE.match(os.path.basename(r.get("path", "")))
        if not m:
            continue
        verdicts[int(m.group("num"))] = (
            r.get("verdict", "pass"),
            r.get("reason", ""),
        )
    return verdicts


def build_entries(figures, captured, verdicts):
    entries = []
    for fig in figures:
        num = fig["num"]
        path = captured.get(num)
        if path is None:
            verdict, reason = "missing", fig.get("skip_reason", "")
        else:
            verdict, reason = verdicts.get(num, ("pass", ""))
        entries.append(
            {
                "num": num,
                "path": path,
                "caption": fig.get("caption", ""),
                "verdict": verdict,
                "reason": reason,
            }
        )
    return entries


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ledger")
    ap.add_argument("figures_dir")
    ap.add_argument("--checks", default=None)
    ap.add_argument("-o", "--out", default="-")
    args = ap.parse_args(argv)

    with open(args.ledger, encoding="utf-8") as fh:
        figures = json.load(fh)["figures"]

    checks = None
    if args.checks:
        with open(args.checks, encoding="utf-8") as fh:
            checks = json.load(fh)

    entries = build_entries(
        figures, index_figures(args.figures_dir), index_checks(checks)
    )

    payload = json.dumps(entries, indent=2, ensure_ascii=False)
    if args.out == "-":
        print(payload)
    else:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(payload + "\n")

    counts = {}
    for e in entries:
        counts[e["verdict"]] = counts.get(e["verdict"], 0) + 1
    print(
        f"{len(entries)} entries: "
        + ", ".join(f"{n} {v}" for v, n in sorted(counts.items())),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
