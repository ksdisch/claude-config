#!/usr/bin/env python3
"""Tier 1 programmatic checks on captured figure images.

Usage:
    python3 checks.py <figures-dir> [-o checks.json]

The dominant failure mode for browser-captured figures is a JS visualization
that never rendered, producing a blank or near-uniform image. PNG compression
makes that cheap to detect without decoding pixels: a blank image compresses to
almost nothing per pixel.

Calibrated against real data:
    blank 900x600 PNG        0.0046 bytes/px
    sparse text-content crop 0.0269 bytes/px
Data visualizations sit above the sparse-text case, so 0.010 separates blank
from real. 0.010-0.020 is a grey zone: flagged for human review, never
auto-rejected.
"""
import argparse
import hashlib
import json
import os
import struct
import sys
from collections import defaultdict

BLANK_MAX_BPP = 0.010
GREY_MAX_BPP = 0.020
MIN_EDGE_PX = 40
MAX_ASPECT = 20.0


def png_dimensions(path):
    """Return (width, height) from a PNG's IHDR chunk."""
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    return struct.unpack(">II", head[16:24])


def check_capture(path):
    """Classify one capture as pass / review / fail.

    An unreadable or non-PNG file is exactly the bad capture this gate exists
    to catch — a failed download leaves a zero-byte file, and a 404 leaves an
    HTML body under a .png name. It is reported as a failing figure, never
    raised: one bad file must not abort the run and discard every other
    figure's verdict.
    """
    # Every filesystem read here is inside the guard, not just the PNG parse: a
    # dangling symlink fails os.path.getsize too, and aborting on it would break
    # the same promise this docstring makes.
    try:
        size = os.path.getsize(path)
        width, height = png_dimensions(path)
    except (ValueError, struct.error, OSError) as exc:
        return {
            "path": path,
            "bytes": os.path.getsize(path) if os.path.exists(path) else 0,
            "width": 0,
            "height": 0,
            "bytes_per_px": 0.0,
            "verdict": "fail",
            "reason": f"unreadable or not a PNG ({exc.__class__.__name__})",
        }
    bpp = size / (width * height) if width and height else 0.0
    result = {
        "path": path,
        "bytes": size,
        "width": width,
        "height": height,
        "bytes_per_px": round(bpp, 5),
    }

    if width < MIN_EDGE_PX or height < MIN_EDGE_PX:
        result.update(verdict="fail", reason=f"degenerate dimensions {width}x{height}")
        return result

    aspect = max(width / height, height / width)
    if aspect > MAX_ASPECT:
        result.update(verdict="fail", reason=f"implausible aspect ratio {aspect:.1f}:1")
        return result

    if bpp < BLANK_MAX_BPP:
        result.update(
            verdict="fail",
            reason=f"blank or unrendered ({bpp:.5f} bytes/px < {BLANK_MAX_BPP})",
        )
        return result

    if bpp < GREY_MAX_BPP:
        result.update(
            verdict="review",
            reason=f"sparse ({bpp:.5f} bytes/px) — needs a human look",
        )
        return result

    result.update(verdict="pass", reason="")
    return result


def find_duplicates(paths):
    """Return groups of paths whose bytes are identical (wrong-element capture).

    Unreadable files are skipped rather than raised on — they are already a
    failure by their own verdict, and one of them must not abort the run.
    """
    by_hash = defaultdict(list)
    for p in paths:
        try:
            with open(p, "rb") as fh:
                blob = fh.read()
        except OSError:
            continue
        if not blob:
            continue  # every failed download is zero bytes; that is not a
            # wrong-element capture, and grouping them steals the real reason
        by_hash[hashlib.sha256(blob).hexdigest()].append(p)
    return [group for group in by_hash.values() if len(group) > 1]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("figures_dir")
    ap.add_argument("-o", "--out", default="-")
    args = ap.parse_args(argv)

    paths = sorted(
        os.path.join(args.figures_dir, f)
        for f in os.listdir(args.figures_dir)
        if f.lower().endswith(".png")
    )
    results = [check_capture(p) for p in paths]
    dupes = find_duplicates(paths)
    for group in dupes:
        for p in group:
            for r in results:
                # Never overwrite a more specific reason. "byte-identical"
                # tells the operator the selector matched the wrong element;
                # saying that about a file that simply failed to download sends
                # them after the wrong remedy.
                if r["path"] == p and not r["reason"]:
                    r["verdict"] = "fail"
                    r["reason"] = "byte-identical to another capture"

    payload = {
        "checked": len(results),
        "passed": sum(1 for r in results if r["verdict"] == "pass"),
        "review": sum(1 for r in results if r["verdict"] == "review"),
        "failed": sum(1 for r in results if r["verdict"] == "fail"),
        "duplicate_groups": [[os.path.basename(p) for p in g] for g in dupes],
        "results": results,
    }
    text = json.dumps(payload, indent=2)
    if args.out == "-":
        print(text)
    else:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    print(
        f"{payload['checked']} checked: {payload['passed']} pass, "
        f"{payload['review']} review, {payload['failed']} fail",
        file=sys.stderr,
    )
    return 1 if payload["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
