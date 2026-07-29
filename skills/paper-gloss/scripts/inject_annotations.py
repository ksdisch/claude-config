#!/usr/bin/env python3
"""Inject the paper-gloss annotation layer into a glossed HTML page.

Usage:
    python3 inject_annotations.py <glossed.html> [--slug SLUG] [-o out.html]
    python3 inject_annotations.py --check <glossed.html>

What it does (all idempotent — a second run is a byte-identical no-op):
  1. Stamps data-pg-block="pg-p-NNNN" on every <p>, <li>, <dd>, <h1>-<h6> that
     lacks the marker. A dedicated attribute, never the id: most headings and
     all footnotes on real pages already carry ids, which stay untouched.
     Markers are opaque anchors — uniqueness and stability matter, order does
     not (the runtime sorts by DOM position, never by marker number).
  2. Sets data-pg-slug="<slug>" on <body> (slug defaults to the filename minus
     its -eli5-glossed.html suffix).
  3. Embeds assets/annotations.css and assets/annotations.js as
     sentinel-guarded blocks (<style id="pg-annot-css"> before </head>,
     <script id="pg-annot-js"> before </body>). Re-running REPLACES the blocks,
     so asset upgrades are one re-run away.

--check verifies all three on an already-injected page and exits non-zero
listing every problem. It never modifies the file.
"""
import argparse
import os
import re
import sys

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

BLOCK_OPEN = re.compile(r"<(?P<tag>p|li|dd|h[1-6])(?P<attrs>(?:\s[^>]*)?)>", re.I)
# The marker is its own attribute — existing ids stay untouched (77 of 79
# headings and all 9 footnote <p>s on the flagship page already carry ids).
# \s prefix, not \b, so substrings of other attribute names never match.
HAS_MARKER = re.compile(r"\sdata-pg-block\s*=", re.I)
PG_BLOCK = re.compile(r'data-pg-block="pg-p-(\d+)"')
BODY_OPEN = re.compile(r"<body(?P<attrs>(?:\s[^>]*)?)>", re.I)
SLUG_ATTR = re.compile(r'\s*data-pg-slug="[^"]*"')
# Block-lookalikes inside <script> spans (the runtime JS builds '<h2>…' strings,
# and GLOSS_TERMS expansions are arbitrary prose) must never be stamped or
# counted — same blanking discipline as check_math.py's verbatim regions.
SCRIPT_SPAN = re.compile(r"<script\b.*?</script>", re.S | re.I)
CSS_BLOCK = re.compile(r'\n?<style id="pg-annot-css">.*?</style>\n?', re.S)
JS_BLOCK = re.compile(r'\n?<script id="pg-annot-js">.*?</script>\n?', re.S)


def _outside_scripts(doc, transform):
    """Apply transform(text) to every span of doc not inside a <script>."""
    out, last = [], 0
    for m in SCRIPT_SPAN.finditer(doc):
        out.append(transform(doc[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(transform(doc[last:]))
    return "".join(out)


def stamp_ids(doc):
    """Add data-pg-block markers to unmarked block elements. Returns (doc, added)."""
    counter = max((int(n) for n in PG_BLOCK.findall(doc)), default=0)
    added = 0

    def repl(m):
        nonlocal counter, added
        attrs = m.group("attrs") or ""
        if HAS_MARKER.search(attrs):
            return m.group(0)
        counter += 1
        added += 1
        return f'<{m.group("tag")} data-pg-block="pg-p-{counter:04d}"{attrs}>'

    return _outside_scripts(doc, lambda seg: BLOCK_OPEN.sub(repl, seg)), added


def derive_slug(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    if stem.endswith("-eli5-glossed"):
        stem = stem[: -len("-eli5-glossed")]
    return stem


def set_slug(doc, slug):
    def repl(m):
        attrs = SLUG_ATTR.sub("", m.group("attrs") or "")
        return f'<body data-pg-slug="{slug}"{attrs}>'

    return BODY_OPEN.sub(repl, doc, count=1)


def embed_assets(doc, css, js):
    doc = CSS_BLOCK.sub("\n", doc)
    doc = JS_BLOCK.sub("\n", doc)
    css_block = f'<style id="pg-annot-css">\n{css}\n</style>\n'
    js_block = f'<script id="pg-annot-js">\n{js}\n</script>\n'
    doc = doc.replace("</head>", css_block + "</head>", 1)
    doc = doc.replace("</body>", js_block + "</body>", 1)
    return doc


def check_page(doc):
    """Return a list of problems; empty means the page is fully injected."""
    problems = []
    if doc.count('<style id="pg-annot-css">') != 1:
        problems.append('expected exactly one <style id="pg-annot-css"> block')
    if doc.count('<script id="pg-annot-js">') != 1:
        problems.append('expected exactly one <script id="pg-annot-js"> block')
    if 'data-pg-slug="' not in doc:
        problems.append("<body> is missing data-pg-slug")
    prose_only = SCRIPT_SPAN.sub("", doc)
    unstamped = sum(
        1
        for m in BLOCK_OPEN.finditer(prose_only)
        if not HAS_MARKER.search(m.group("attrs") or "")
    )
    if unstamped:
        problems.append(f"{unstamped} block element(s) left unstamped")
    if "closeAnnotationUI" not in doc:
        problems.append("runtime JS missing (no closeAnnotationUI in page)")
    return problems


def load_assets():
    with open(os.path.join(ASSETS, "annotations.css"), encoding="utf-8") as fh:
        css = fh.read().strip()
    with open(os.path.join(ASSETS, "annotations.js"), encoding="utf-8") as fh:
        js = fh.read().strip()
    return css, js


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("page")
    ap.add_argument("--slug")
    ap.add_argument("-o", "--out")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    with open(args.page, encoding="utf-8") as fh:
        doc = fh.read()

    if args.check:
        problems = check_page(doc)
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        print(("clean" if not problems else f"{len(problems)} problem(s)"),
              file=sys.stderr)
        return 1 if problems else 0

    css, js = load_assets()
    doc, added = stamp_ids(doc)
    doc = set_slug(doc, args.slug or derive_slug(args.page))
    doc = embed_assets(doc, css, js)

    # Never write a half-injected page: a missing </head> or </body> anchor
    # makes embed_assets a silent no-op, and the default write is in-place.
    problems = check_page(doc)
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        print("aborting: injection did not produce a valid page; nothing written",
              file=sys.stderr)
        return 1

    out_path = args.out or args.page
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"stamped {added} new block marker(s); wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
