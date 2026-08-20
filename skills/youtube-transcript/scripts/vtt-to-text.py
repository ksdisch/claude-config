#!/usr/bin/env python3
"""Convert a WebVTT subtitle file into readable plain text.

    python3 vtt-to-text.py INPUT.vtt [-o OUTPUT.txt]
    python3 vtt-to-text.py INPUT.vtt --title-file TITLE.txt [--dir DIR]

With no `-o` and no `--title-file`, the text goes to stdout.

YouTube's auto-generated captions scroll: each cue repeats the tail of the cue
before it and appends a few new words, so a naive line dump reads every phrase
two or three times. This strips the caption machinery (header, cue timings,
NOTE/STYLE blocks, karaoke `<c>` tags, HTML entities) and then removes that
overlap.

Deduplication is **cue-aware**, not a sliding window over output lines: a line is
dropped only when the cue immediately before it already contained that same
line. That is exactly the shape rollup captions have — YouTube re-sends the
lines still on screen with each new cue — so it removes the overlap completely
while leaving everything else alone.

Both of the obvious alternatives are wrong, and each fails in a way that is
invisible in the output:

- **Whole-file dedup** removes the overlap but also deletes genuine repetition.
  A speaker who says "so that's the tradeoff" in minute 3 and again in minute 40
  loses the second one, and the transcript stops matching the video.
- **A fixed window over emitted lines** cannot be tuned to fit. A rollup cue
  carries several lines, so a repeat can sit two or three emitted lines back —
  window 1 leaves every phrase duplicated. Widen it to cover that and it starts
  eating the short utterances ("Yeah.", "Right.", "Exactly.") that legitimately
  recur a few lines apart all through any interview.

Cue boundaries sidestep the tradeoff because they are the structure the
duplication actually comes from.

`--no-dedup` turns it off for manual captions, which have no overlap to remove.

`--title-file` exists so a video title never has to become shell command text.
Titles are third-party-controlled and routinely contain `$`, backticks, and
quotes; passing one as a command-line literal is an injection waiting to happen.
Write it to a file (`yt-dlp --print "%(title)s" URL > title.txt`) and pass the
path — the title crosses as data, and the sanitizing happens here in Python.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

# A cue timing line, with optional trailing cue settings:
#   00:00:01.234 --> 00:00:03.456        yt-dlp
#   00:01.234 --> 00:03.456              Whisper, on anything under an hour
# The hours field is optional per the WebVTT spec and Whisper's WriteVTT omits
# it (`always_include_hours = False`), so requiring it silently yields zero cues
# on the one path this skill treats as expensive. Hours may exceed two digits.
TIMING = re.compile(r"^(?:\d{2,}:)?\d{1,2}:\d{2}[.,]\d{3}\s*-->\s")
# Inline caption markup: `<c>`, `</c.colorE5E5E5>`, `<00:00:02.480>`, `<v Bob>`.
TAG = re.compile(r"<[^>]*>")
# No pattern for `WEBVTT`/`Kind:`/`NOTE`/`STYLE`: those are recognized by position
# (before any timing line) rather than by text. Matching them by text is what let
# an ALL-CAPS caption cue beginning "NOTE THE DIFFERENCE" be swallowed whole.


def clean(line: str) -> str:
    """A caption line reduced to its words, or "" if nothing survives."""
    return html.unescape(TAG.sub("", line)).strip()


# Everything hazardous in a filename, a shell word, or both. Filesystem: `/`,
# `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`. Shell: backtick and `$` (execute inside
# double quotes), `'` (escapes single quotes), and `;&()[]{}!#~` (metacharacters
# if the name is ever left unquoted). Keeping the title off the command line is
# the real defence, but the output filename gets echoed into later commands, so
# it must be inert on its own.
UNSAFE = re.compile(r"""[/\\:*?"<>|`$'!#~;&(){}\[\]]""")


def safe_filename(title: str, fallback: str = "transcript") -> str:
    """A video title reduced to a filename stem that is inert in a shell word."""
    stem = re.sub(r"[\x00-\x1f\x7f]", "", title)
    stem = UNSAFE.sub("-", stem)
    stem = re.sub(r"-{2,}", "-", stem)
    stem = re.sub(r"\s+", " ", stem).strip(" .-")
    return stem[:120].strip(" .-") or fallback


def cues(vtt: str) -> list[list[str]]:
    """The VTT's cues, each as its list of cleaned payload lines.

    Cue boundaries are what deduplication keys on, so they are parsed rather
    than inferred: a cue opens on a timing line and runs to the next blank line.
    Anything before the first timing line is header and is dropped.
    """
    blocks: list[list[str]] = []
    current: list[str] | None = None

    for raw in vtt.splitlines():
        line = raw.strip()

        if not line:
            if current is not None:
                blocks.append(current)
                current = None
            continue

        if TIMING.match(line):
            # A new timing line inside an unterminated block still starts a cue.
            if current is not None:
                blocks.append(current)
            current = []
            continue

        if current is None:
            continue  # header region, NOTE/STYLE block, or a stray cue number

        text = clean(line)
        if text:
            current.append(text)

    if current is not None:
        blocks.append(current)

    return [b for b in blocks if b]


def to_text(vtt: str, dedup: bool = True) -> list[str]:
    """The spoken lines of a VTT file, in order, with scroll overlap removed."""
    out: list[str] = []
    previous: set[str] = set()

    for cue in cues(vtt):
        for text in cue:
            if dedup and text in previous:
                continue
            # A partial line settling into its full form ("so the thing" then
            # "so the thing is we keep shipping") is the same utterance twice.
            # Keep the longer one rather than emitting both.
            if dedup and out and text.startswith(out[-1]):
                out[-1] = text
                continue
            if dedup and out and out[-1].startswith(text):
                continue
            out.append(text)
        previous = set(cue)

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
        "--title-file",
        type=Path,
        help="file holding the video title; the output is named after it. Keeps the "
        "title off the command line, where a `$` or backtick in it would execute.",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("."),
        help="directory for the --title-file output (default: current directory)",
    )
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="emit every caption line. Right for manual captions, which have no "
        "scroll overlap to remove.",
    )
    args = parser.parse_args(argv)

    if not args.input.is_file():
        print(f"vtt-to-text: no such file: {args.input}", file=sys.stderr)
        return 1

    if args.title_file and args.output:
        print(
            "vtt-to-text: pass either -o or --title-file, not both.",
            file=sys.stderr,
        )
        return 1

    destination = args.output
    if args.title_file:
        if not args.title_file.is_file():
            print(f"vtt-to-text: no such title file: {args.title_file}", file=sys.stderr)
            return 1
        title = args.title_file.read_text(encoding="utf-8", errors="replace").strip()
        destination = args.dir / (safe_filename(title) + ".txt")

    lines = to_text(
        args.input.read_text(encoding="utf-8", errors="replace"),
        dedup=not args.no_dedup,
    )

    if not lines:
        print(
            f"vtt-to-text: {args.input} produced no text — it may be empty or not a "
            "VTT file. Nothing was written.",
            file=sys.stderr,
        )
        return 1

    body = "\n".join(lines) + "\n"
    if destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(body, encoding="utf-8")
        print(f"{destination}  ({len(lines)} lines)")
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
