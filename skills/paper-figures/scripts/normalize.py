#!/usr/bin/env python3
"""Resample captured figures to fit an adaptive total size budget.

Usage:
    python3 normalize.py <src-dir> <dst-dir> [--count N]

Full-resolution originals in <src-dir> are never modified. This writes
budget-fitting copies into <dst-dir> for base64 inlining into the HTML.

The budget is computed, not fixed:
    per_figure = min(PER_FIGURE_CAP, TOTAL_BUDGET / figure_count)
so a 94-figure paper gets ~64KB each while an 8-figure paper gets the full
250KB cap. Resampling uses macOS `sips`; no Pillow or ImageMagick required.
"""
import argparse
import os
import subprocess
import sys

TOTAL_BUDGET = 6 * 1024 * 1024
PER_FIGURE_CAP = 250_000
MAX_WIDTH = 1400
MIN_WIDTH = 600
WIDTH_STEPS = [1400, 1200, 1000, 900, 800, 700, 600]


def per_figure_budget(figure_count):
    """Bytes allowed per figure in the inlined HTML."""
    if figure_count <= 0:
        return PER_FIGURE_CAP
    return min(PER_FIGURE_CAP, TOTAL_BUDGET // figure_count)


def plan_width(source_width, budget_bytes):
    """Pick a starting width for a given per-figure budget."""
    target = min(source_width, MAX_WIDTH)
    # Roughly 0.08 bytes/px for a JPEG-encoded plot at q70; scale width down
    # until the projected size fits, then let the step-down loop refine.
    for w in WIDTH_STEPS:
        if w > target:
            continue
        projected = (w * w * 0.66) * 0.08  # assume ~2:3 aspect
        if projected <= budget_bytes:
            return w
    # No step fits the budget. Fall back to the narrowest step, but never wider
    # than the source: this is a downscaling tool, and enlarging a small figure
    # spends its byte budget on interpolated pixels and ships it blurrier than
    # the original already on disk.
    return min(target, MIN_WIDTH)


def sips_dimensions(path):
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
        capture_output=True, text=True, check=True,
    ).stdout
    dims = {}
    for line in out.splitlines():
        if "pixelWidth:" in line:
            dims["w"] = int(line.split(":")[1])
        elif "pixelHeight:" in line:
            dims["h"] = int(line.split(":")[1])
    return dims["w"], dims["h"]


def same_path(a, b):
    """True when two paths name the same file or directory on disk.

    `os.path.abspath` comparison is not this test: it resolves neither symlinks
    nor case, and this is macOS-only tooling whose default APFS volume is
    case-INSENSITIVE — so `figs` and `Figs` are one directory that abspath calls
    two. `samefile` compares device+inode. It raises when either side does not
    exist yet, which is the ordinary "writing a new output" case and means they
    cannot be the same file.
    """
    try:
        return os.path.samefile(a, b)
    except OSError:
        return os.path.abspath(a) == os.path.abspath(b)


def resample(src, dst, width, fmt, quality=None):
    if same_path(src, dst):
        raise ValueError(f"refusing to resample {src} onto itself")
    cmd = ["sips", "--resampleWidth", str(width), "-s", "format", fmt]
    if fmt == "jpeg" and quality:
        cmd += ["-s", "formatOptions", str(quality)]
    cmd += [src, "--out", dst]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    # `sips` exits 0 when its input is missing ("not a valid file - skipping"),
    # so check=True proves nothing. Verify an output actually appeared, or the
    # emitted manifest will describe a file that does not exist.
    if not os.path.exists(dst):
        raise RuntimeError(
            f"sips produced no output for {src}: "
            f"{(proc.stderr or b'').decode(errors='replace').strip()}"
        )
    return os.path.getsize(dst)


def normalize_one(src, dst_dir, budget):
    """Write a budget-fitting copy of src into dst_dir. Returns a record."""
    stem = os.path.splitext(os.path.basename(src))[0]
    sw, _ = sips_dimensions(src)
    width = plan_width(sw, budget)

    best = None
    for fmt, ext, q in (("png", "png", None), ("jpeg", "jpg", 70)):
        dst = os.path.join(dst_dir, f"{stem}.{ext}")
        size = resample(src, dst, width, fmt, q)
        if best is None or size < best[1]:
            if best is not None:
                os.remove(best[0])
            best = (dst, size, fmt, width)
        else:
            os.remove(dst)

    dst, size, fmt, width = best
    for step in [w for w in WIDTH_STEPS if w < width]:
        if size <= budget:
            break
        size = resample(src, dst, step, fmt, 70 if fmt == "jpeg" else None)
        width = step

    return {
        "source": os.path.basename(src),
        "output": os.path.basename(dst),
        "format": fmt,
        "width": width,
        "bytes": size,
        "budget": budget,
        "over_budget": size > budget,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src_dir")
    ap.add_argument("dst_dir")
    ap.add_argument("--count", type=int, default=0)
    args = ap.parse_args(argv)

    srcs = sorted(
        os.path.join(args.src_dir, f)
        for f in os.listdir(args.src_dir)
        if f.lower().endswith(".png")
    )
    count = args.count or len(srcs)
    budget = per_figure_budget(count)
    os.makedirs(args.dst_dir, exist_ok=True)

    # The full-resolution originals in src_dir are committed, are what the
    # injected markdown references by path, and are never regenerated. Writing
    # into the same directory resamples each one onto itself and then deletes
    # the loser of the png/jpeg comparison — silent, total, unrecoverable loss.
    # Checked after makedirs so both sides exist and `samefile` can see through
    # a symlinked or case-variant dst that abspath would call a different path.
    if same_path(args.src_dir, args.dst_dir):
        print(
            "error: dst_dir must differ from src_dir — normalizing in place would "
            "destroy the full-resolution originals",
            file=sys.stderr,
        )
        return 2

    records = [normalize_one(s, args.dst_dir, budget) for s in srcs]
    total = sum(r["bytes"] for r in records)
    over = [r["output"] for r in records if r["over_budget"]]

    print(f"budget {budget:,} B/figure across {count} figures", file=sys.stderr)
    print(f"total {total:,} B ({total / 1048576:.1f} MB)", file=sys.stderr)
    if over:
        print(f"over budget after step-down: {', '.join(over)}", file=sys.stderr)
    import json

    print(json.dumps({"budget": budget, "total_bytes": total, "figures": records}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
