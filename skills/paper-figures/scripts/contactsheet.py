#!/usr/bin/env python3
"""Build a throwaway contact sheet for reviewing captured figures.

Usage:
    python3 contactsheet.py <entries.json> <out.html> [--title "Paper title"]
                            [--max-width 320]

Thumbnails are inlined so the sheet is one portable file. It is never
committed — it exists only for the approval gate.

Captures are downscaled to --max-width before inlining. Inlining the originals
instead makes the sheet unusable at scale: on a 94-figure paper that produced a
26MB file, when the whole point of the sheet is to be small enough to send.
Resampling uses macOS `sips`; where it is unavailable the original is inlined
and the resulting size is reported so the caller is not surprised.
"""
import argparse
import base64
import html as htmllib
import json
import os
import shutil
import subprocess
import sys
import tempfile

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Figure contact sheet — {title}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 14px/1.5 -apple-system, system-ui, sans-serif; margin: 2rem; }}
  h1 {{ font-size: 1.3rem; }}
  .summary {{ margin-bottom: 1.5rem; opacity: 0.8; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }}
  .entry {{ border: 1px solid rgba(128,128,128,0.35); border-radius: 8px; padding: 0.75rem; }}
  .entry.fail {{ border-color: #d33; background: rgba(221,51,51,0.07); }}
  .entry.review {{ border-color: #e90; background: rgba(238,153,0,0.07); }}
  .entry.missing {{ border-color: #888; background: rgba(128,128,128,0.1); }}
  .entry img {{ max-width: 100%; height: auto; border-radius: 4px; display: block; }}
  .num {{ font-weight: 700; margin-bottom: 0.4rem; }}
  .cap {{ font-size: 0.82rem; opacity: 0.85; margin-top: 0.5rem; }}
  .flag {{ font-size: 0.8rem; color: #d33; margin-top: 0.4rem; font-weight: 600; }}
  .none {{ padding: 2rem; text-align: center; opacity: 0.6; font-style: italic; }}
</style></head><body>
<h1>Figure contact sheet — {title}</h1>
<div class="summary">{summary}</div>
<div class="grid">
{entries}
</div>
</body></html>
"""


def _inline(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as fh:
        blob = base64.b64encode(fh.read()).decode("ascii")
    return f"data:{MIME.get(ext, 'image/png')};base64,{blob}"


def thumb_uri(path, max_width=320, tmp_dir=None):
    """Inline a downscaled copy. Falls back to the original without sips."""
    if not max_width or tmp_dir is None or not shutil.which("sips"):
        return _inline(path)
    dst = os.path.join(tmp_dir, f"{abs(hash(path))}.jpg")
    try:
        subprocess.run(
            ["sips", "--resampleWidth", str(max_width), "-s", "format", "jpeg",
             "-s", "formatOptions", "60", path, "--out", dst],
            capture_output=True, check=True,
        )
    except (subprocess.CalledProcessError, OSError):
        return _inline(path)
    return _inline(dst) if os.path.exists(dst) else _inline(path)


def build_sheet(entries, title, max_width=320, tmp_dir=None):
    blocks = []
    for e in entries:
        verdict = e.get("verdict", "pass")
        cap = htmllib.escape(e.get("caption", ""))
        if e.get("path") and os.path.exists(e["path"]):
            body = (f'<img src="{thumb_uri(e["path"], max_width, tmp_dir)}" '
                    f'alt="Figure {e["num"]}">')
        else:
            body = '<div class="none">not captured</div>'
        flag = ""
        if e.get("reason"):
            flag = f'<div class="flag">{htmllib.escape(e["reason"])}</div>'
        blocks.append(
            f'<div class="entry {verdict}">'
            f'<div class="num">Figure {e["num"]}</div>'
            f"{body}{flag}"
            f'<div class="cap">{cap}</div>'
            f"</div>"
        )

    counts = {}
    for e in entries:
        counts[e.get("verdict", "pass")] = counts.get(e.get("verdict", "pass"), 0) + 1
    summary = f"{len(entries)} figures — " + ", ".join(
        f"{n} {v}" for v, n in sorted(counts.items())
    )
    return PAGE.format(
        title=htmllib.escape(title), summary=summary, entries="\n".join(blocks)
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("entries")
    ap.add_argument("out")
    ap.add_argument("--title", default="paper")
    ap.add_argument("--max-width", type=int, default=320,
                    help="thumbnail width before inlining; 0 inlines originals")
    args = ap.parse_args(argv)
    with open(args.entries, encoding="utf-8") as fh:
        entries = json.load(fh)
    if args.max_width and not shutil.which("sips"):
        print("warning: sips unavailable — inlining originals, sheet may be large",
              file=sys.stderr)
    with tempfile.TemporaryDirectory() as tmp:
        sheet = build_sheet(entries, args.title, args.max_width, tmp)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(sheet)
    print(f"wrote {args.out} ({os.path.getsize(args.out):,} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
