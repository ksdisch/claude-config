#!/usr/bin/env python3
"""Convert a WebVTT subtitle file into readable plain text.

    python3 vtt-to-text.py INPUT.vtt [-o OUTPUT.txt]

With no `-o`, the text goes to stdout.

YouTube's auto-generated captions scroll: each cue repeats the tail of the cue
before it and appends a few new words, so a naive line dump reads every phrase
two or three times. This strips the caption machinery (header, cue timings,
NOTE/STYLE blocks, karaoke `<c>` tags, HTML entities) and then removes that
overlap.

Deduplication is deliberately **local** — a line is dropped only when it repeats
something in the last `--window` emitted lines (default 10), not when it repeats
anything anywhere in the file. Whole-file deduplication is the obvious approach
and it is wrong: a speaker who says "so that's the tradeoff" in minute 3 and
again in minute 40 loses the second one, silently, and the transcript stops
matching the video. Overlap duplicates are always adjacent, so a short window
catches them without touching genuine repetition.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

# `00:00:01.234 --> 00:00:03.456` with optional trailing cue settings.
TIMING = re.compile(r"^\d{1,2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s")
# Inline caption markup: `<c>`, `</c.colorE5E5E5>`, `<00:00:02.480>`, `<v Bob>`.
TAG = re.compile(r"<[^>]*>")
# `WEBVTT`, `Kind: captions`, `Language: en`, and the `NOTE`/`STYLE` block heads.
HEADER = re.compile(r"^(WEBVTT|Kind:|Language:|NOTE\b|STYLE\b|REGION\b)")


def clean(line: str) -> str:
    """A caption line reduced to its words, or "" if nothing survives."""
    return html.unescape(TAG.sub("", line)).strip()


def to_text(vtt: str, window: int = 10) -> list[str]:
    """The spoken lines of a VTT file, in order, with scroll overlap removed."""
    out: list[str] = []
    in_block = False  # inside a NOTE/STYLE block, which runs to a blank line

    for raw in vtt.splitlines():
        line = raw.strip()

        if not line:
            in_block = False
            continue
        if in_block:
            continue
        if HEADER.match(line):
            in_block = True
            continue
        if TIMING.match(line) or "-->" in line:
            continue
        # A bare integer on its own line is a cue number, not speech.
        if line.isdigit():
            continue

        text = clean(line)
        if not text:
            continue

        recent = out[-window:] if window > 0 else []
        if text in recent:
            continue
        # The scrolling window also emits strict prefixes of the next cue
        # ("so the thing" then "so the thing is"). Keep the longer one.
        if recent and recent[-1] and text.startswith(recent[-1]):
            out[-1] = text
            continue
        if recent and recent[-1].startswith(text):
            continue

        out.append(text)

    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("input", type=Path, help="the .vtt file to convert")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write here instead of stdout",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=10,
        help="how many recent lines to dedupe against (0 disables; default 10)",
    )
    args = parser.parse_args(argv)

    if not args.input.is_file():
        print(f"vtt-to-text: no such file: {args.input}", file=sys.stderr)
        return 1

    lines = to_text(args.input.read_text(encoding="utf-8", errors="replace"), args.window)

    if not lines:
        print(
            f"vtt-to-text: {args.input} produced no text — it may be empty or not a "
            "VTT file. Nothing was written.",
            file=sys.stderr,
        )
        return 1

    body = "\n".join(lines) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
        print(f"{args.output}  ({len(lines)} lines)")
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
