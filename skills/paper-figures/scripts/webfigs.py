#!/usr/bin/env python3
"""Enumerate figures on a source web page and classify each one.

Usage:
    python3 webfigs.py <page.html> <page-url> [-o manifest.json]

Figures are addressed by the data-fignum attribute, never by matching caption
text. A figure containing an <img> is 'static' (download it directly); one with
only a JS mount div is 'interactive' (needs a browser screenshot).
"""
import argparse
import html
import json
import re
import sys
from urllib.parse import urljoin

FIGURE = re.compile(r"<figure\b(?P<attrs>[^>]*)>(?P<inner>.*?)</figure>", re.S | re.I)
FIGNUM = re.compile(r'data-fignum="(\d+)"')
IMG_SRC = re.compile(r"<img\b[^>]*?\bsrc=\"(?P<src>[^\"]+)\"", re.S | re.I)
FIGCAPTION = re.compile(r"<figcaption\b[^>]*>(?P<text>.*?)</figcaption>", re.S | re.I)
FIG_NUM_SPAN = re.compile(
    r"<span\b[^>]*class=\"fig-num\"[^>]*>.*?</span>", re.S | re.I
)
TAG = re.compile(r"<[^>]+>")


def _caption_text(inner):
    m = FIGCAPTION.search(inner)
    if not m:
        return ""
    text = FIG_NUM_SPAN.sub("", m.group("text"))
    text = TAG.sub("", text)
    return html.unescape(text).strip()


def build_manifest(page_html, page_url):
    """Return a list of figure dicts, in document order."""
    figures = []
    for m in FIGURE.finditer(page_html):
        num_m = FIGNUM.search(m.group("attrs"))
        if not num_m:
            continue
        num = int(num_m.group(1))
        inner = m.group("inner")
        img = IMG_SRC.search(inner)
        figures.append(
            {
                "num": num,
                "kind": "static" if img else "interactive",
                "img_url": urljoin(page_url, img.group("src")) if img else None,
                "selector": f'figure[data-fignum="{num}"]',
                "caption": _caption_text(inner),
            }
        )
    return figures


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("page")
    ap.add_argument("url")
    ap.add_argument("-o", "--out", default="-")
    args = ap.parse_args(argv)

    with open(args.page, encoding="utf-8", errors="replace") as fh:
        figures = build_manifest(fh.read(), args.url)

    payload = json.dumps({"figures": figures}, indent=2, ensure_ascii=False)
    if args.out == "-":
        print(payload)
    else:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(payload + "\n")

    static = sum(1 for f in figures if f["kind"] == "static")
    print(
        f"{len(figures)} figures: {static} static, {len(figures) - static} interactive",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
