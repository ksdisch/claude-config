# paper-gloss Annotations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a highlight-and-note annotation layer to every paper-gloss HTML page — select text, highlight it, attach a note, persist in `localStorage`, and export to both Obsidian-ready Markdown and re-importable JSON — built into `/paper-gloss` for new pages and retrofittable onto the 6 already-published pages via a new `--annotate` mode.

**Architecture:** The annotation runtime is a fixed asset pair (`assets/annotations.css` + `assets/annotations.js`) with zero per-paper content — both new-page generation and the retrofit embed the same bytes via one deterministic, idempotent injector script (`scripts/inject_annotations.py`), which also stamps stable `data-pg-block` markers on block elements and a paper slug on `<body>`. Anchoring is W3C TextQuoteSelector-style (exact quote + prefix/suffix context) with a block-marker hint, so annotations survive the math/figure retrofits, which never rewrite prose. Deterministic work lives in the Python script with unit tests; the skill prose only orchestrates.

**Tech Stack:** Vanilla JS + CSS (no libraries — artifact CSP forbids external loads anyway), Python 3 stdlib (`re`, `json`, `argparse`, `unittest`) for the injector, Playwright MCP for functional validation, the Artifact `downloads` capability (`window.claude.downloads.save`) for export.

**Spec:** No separate spec doc — the *Settled decisions* section below is the spec, distilled from the 2026-07-27/28 planning sessions (decisions Kyle approved: `localStorage` primary + export/import guaranteed fallback; annotations are **both** page-persistent and Obsidian-exported, equal weight).

---

## Settled decisions

### D1 — Built into `/paper-gloss` (Phase 2 + a new `--annotate` mode); no new skill

The annotation layer, unlike figures, has **no per-paper content at build time** — it is a
fixed runtime block parameterized only by a slug. `/paper-figures` earned separate skillhood
because figure harvesting is a multi-phase pipeline (source discovery, browser capture,
budgets, a human gate). Annotations need exactly two things: embed a static block at
generation, and inject the same block into existing pages. Both are paper-gloss-shaped:
generation slots into Phase 2, and the retrofit mirrors the existing RETROFIT mode pattern
(`--retrofit` repairs math; `--annotate` adds annotations). One skill means one doc-sync
row edit and no new discovery burden. The growth risk to the already-612-line SKILL.md is
contained by keeping the runtime in assets and the mechanics in the injector — the SKILL.md
additions are orchestration prose only.

### D2 — Anchoring: exact quote + prefix/suffix context, with a paragraph-id hint

Each annotation stores `{exact, prefix, suffix, pid, offset}`:

- `exact` — the highlighted text, verbatim.
- `prefix`/`suffix` — up to 32 characters of surrounding text **within the same block**.
- `pid` — the block marker of the enclosing element (`data-pg-block="pg-p-NNNN"`), stamped
  by the injector on every `<p>`, `<li>`, `<dd>`, and `<h1>`–`<h6>` **regardless of any
  existing `id`, which is left untouched**. A dedicated attribute, not the `id`, because
  ids are already taken: 0 of 592 `<p>` carry one on the jacobian-lens page, but **77 of
  its 79 headings and all 9 footnote `<p>`s do** — keying the anchor set off `id` would
  exclude every heading from annotation and collapse `sectionOf()` (and with it the
  Markdown export's section grouping) to the paper title. Stamping is both a
  generation-side addition and part of the retrofit injection.
- `offset` — character offset of the quote within the block's `textContent`, used only as a
  tiebreaker score, never as the primary key.

**Re-anchoring order:** (1) exact match inside the `pid` block, scored by prefix/suffix when
multiple hits; (2) exact match in any other block, same scoring — this heals pid drift;
(3) no match anywhere → the annotation is an **orphan**: kept in the panel under
"Unanchored", exportable, never silently dropped.

Why quote-first rather than offset-first: the two existing retrofit modes (math, figures)
change DOM *inside* paragraphs — TeX → MathML changes a span's `textContent` — so offsets
are brittle, but both modes operate under a hard "never rewrite prose" contract, which is
exactly the guarantee quote matching needs. Known residual risk, stated rather than hidden:
a quote that *includes math text* can orphan after a later math retrofit changes that text.
The orphan section is the designed landing place for that case.

Highlights are **single-block** in v1 — a selection spanning two paragraphs doesn't offer
the toolbar. Cross-block anchoring triples the anchoring surface for a rare gesture; if it
turns out to matter in practice it's a clean follow-up.

### D3 — Storage: `localStorage`, key `pg-annotations:<slug>`, versioned schema

```json
{
  "v": 1,
  "slug": "<paper-slug>",
  "title": "<document.title>",
  "annotations": [
    {
      "id": "a-m4k2x9-7f3",
      "exact": "the highlighted text",
      "prefix": "up to 32 chars before ",
      "suffix": " up to 32 chars after",
      "pid": "pg-p-0042",
      "offset": 118,
      "note": "optional note text",
      "section": "nearest preceding heading text",
      "created": "2026-07-28T18:00:00.000Z"
    }
  ]
}
```

Origin isolation already prevents cross-paper collisions between artifacts (each artifact
runs on its own `https://<uuid>.frame.claudeusercontent.com` origin — verified by probe);
the slug key exists for the local-file case and to make export files self-describing.
Write-through on every mutation; `try/catch` around all storage calls so private mode or a
full quota degrades to in-memory (the session still works, the export path still works).

**Storage lifecycle facts the UI must surface honestly** (verified in the prior session's
probe): a `--retrofit`/`--annotate` redeploy keeps the URL → keeps the origin → **keeps
annotations**; a fresh publish mints a new origin → starts empty; the local `file://` copy
is a third origin — annotations never transfer between local file and artifact except by
export/import. The panel carries a permanent one-line hint: *"Notes live in this browser
only — export to keep them safe."* — and the hint flips to an explicit ⚠️ not-saved
warning the moment a storage write fails: partitioned/blocked iframe storage on
`claudeusercontent.com` is a live path, not a theoretical one, and a badge that counts up
while nothing persists would be the dishonest UI this section forbids.

**Cross-device sync and shared annotations are off the table, not deferred.** The only
artifact capabilities available are `downloads` and `mcp` — there is no storage/state
capability, so no design in this plan should pretend a sync backend might appear.

### D4 — Export: both Markdown and JSON, both first-class (Kyle's call, 2026-07-28)

- `<slug>-annotations.md` — Obsidian-ready: YAML frontmatter (paper, url, exported, tags),
  then annotations grouped under `##` section headings in document order, each as a
  blockquote + note.
- `<slug>-annotations.json` — the full payload above plus `kind`, `url`, `exported`;
  lossless and re-importable.

**Primary path:** `window.claude.downloads.save({filename, data})` under
`capabilities: {downloads: true}`. Both `md` and `json` are in the base extension allowlist
(runtime contract 0.1.15). One undecided prompt at a time → two separate export buttons,
each its own prompt. Error handling per the typed contract: `declined` → do nothing, never
auto-retry; anything else (including `unavailable` and absent `window.claude.downloads`,
which is every `file://` open) → a copy-to-clipboard fallback dialog showing the full text.
**Import** needs no capability: `<input type="file">` + `FileReader`, merged as a union by
annotation id (duplicates skipped and counted).

**Publish-call change:** paper-gloss currently publishes with NO capabilities. Phase 4
gains `capabilities: {downloads: true}`, and — critical for the retrofit — the `--annotate`
republish must pass it **explicitly**: omitting `capabilities` carries forward the stored
declaration, and the 6 existing artifacts have none stored.

### D5 — Surface coordination: annotations self-coordinate; existing runtime code is never edited

Annotations add a 4th surface family (selection toolbar, note editor, annotations panel) to
the existing three (gloss popover, glossary panel, figure lightbox). The one-surface-at-a-time
contract extends **without editing any existing page's scripts**:

- **Opening any annotation surface closes the others:** the module prefers the exported
  hooks — `window.closeGlossSurfaces` (which paper-figures retrofits export),
  `window.closeGlossPopover`, `window.closeGlossPanel`, `window.closeFigureLightbox`, each
  guarded with `typeof === 'function'` — and **falls back to driving the surfaces' own
  markup by id** (`#gloss-popover`, `#gloss-panel`, `#gloss-backdrop`, `#figure-lightbox`
  hidden; `aria-expanded` reset on `#gloss-panel-toggle`). The fallback is load-bearing,
  not belt-and-suspenders: measured against the six retrofit targets, **five export no
  hooks at all** and jacobian-lens exports only `closeGlossSurfaces` +
  `closeFigureLightbox` — the per-surface hooks exist only on pages generated after this
  plan's SKILL.md amendment. (Same layered pattern as `paper-figures`' `inject_html.py`,
  which hit this exact problem first.)
- **Other surfaces opening close the annotation UI:** the module's own delegated document
  listener watches for clicks on `.gloss-term`, `#gloss-panel-toggle`, and
  `.paper-figure img` and closes itself first. This is what makes retrofitted pages —
  whose gloss/lightbox code predates annotations and will never call into it — obey the
  rule with zero modification.
- **New public contract point:** the module assigns `window.closeAnnotationUI` (one
  function closing toolbar + editor + panel + fallback dialog), so any *future* surface can
  coordinate explicitly.

**`skills/paper-figures/SKILL.md` needs a documentation-only edit** (Task 9): a short note
in its Phase 6 lightbox contract paragraph stating that pages carrying the annotation layer
coordinate themselves via delegation and expose `window.closeAnnotationUI` — no change to
`inject_html.py` or its `LIGHTBOX_JS`. Its frontmatter description is untouched, so no
doc-sync edit fires for it.

**Selection vs. gloss-click collision:** the toolbar appears only on `mouseup` with a
non-collapsed selection; a plain click on a `.gloss-term` button has a collapsed selection
and behaves exactly as today. Highlights wrap **text-node segments, never element tags**,
so a highlight crossing a gloss button leaves the button intact; a click landing on a
highlight segment *inside* a gloss button defers to the gloss popover (the button wins).
Marks are never injected into math (`.math`, `<math>`, `pre.equation`) — same never-wrap
discipline as term-wrapping; anchoring still works because quotes match against
`textContent`, the marks just skip those segments.

### D6 — Retrofit scope: all 6 published pages, jacobian-lens first

| # | Page | Notes |
|---|---|---|
| 1 | `~/Projects/jacobian-lens/verbalizable-representations-global-workspace-language-models-eli5-glossed.html` | **At repo ROOT**, not docs/papers/. Has figures + lightbox → the full coordination test. Validation slice. |
| 2 | `~/Projects/ghost-patch/docs/papers/ghost-patch-eli5-glossed.html` | |
| 3 | `~/Projects/forge-gap/docs/papers/forge-gap-eli5-glossed.html` | |
| 4 | `~/Projects/lossy-wall/docs/papers/lossy-wall-eli5-glossed.html` | |
| 5 | `~/Projects/dim-stage/docs/paper/global-workspace-readable-small-language-models-eli5-glossed.html` | `docs/paper/` — singular, not a typo |
| 6 | `~/Projects/decay-pin/docs/papers/decay-pin-eli5-glossed.html` | |

Each retrofit redeploys to the page's **existing** Artifact URL (found via
`Artifact(action:"list")`, matched by title). A page whose URL can't be confidently matched
gets its file delivered and the ambiguity flagged to Kyle — never a fresh publish, which
would orphan the old link. No annotations exist anywhere today, so ordering carries no
data risk; jacobian-lens goes first because it exercises every surface.

The eli5 **markdown is untouched** by all of this — annotations are an HTML-page feature.

---

## File Structure

| File | Responsibility |
|---|---|
| `skills/paper-gloss/assets/annotations.css` | Runtime styles: marks, toolbar, editor, panel, fallback dialog — self-sufficient `--pg-annot-*` variables with light defaults, dark media query, and both `data-theme` overrides |
| `skills/paper-gloss/assets/annotations.js` | Runtime: storage, anchor capture/re-anchor, mark rendering, selection toolbar, note editor, panel, export (downloads + fallback), import, surface coordination |
| `skills/paper-gloss/scripts/inject_annotations.py` | Stamp `data-pg-block` markers + body slug, embed both assets at sentinel-guarded seams (replace-on-rerun), `--check` mode asserting page invariants, self-check before any write |
| `skills/paper-gloss/scripts/tests/test_inject_annotations.py` | Unit tests for the injector |
| Modify: `skills/paper-gloss/SKILL.md` | `--annotate` arg, Phase 2 injection step, Phase 3 bullets, Phase 4 capabilities, new ANNOTATE mode section, description update |
| Modify: `docs/command-skill-reference.md` (paper-gloss row) | Same commit as the description change — `scripts/check-doc-sync.py` runs at pre-push |
| Modify: `docs/usage-playbook.md` (paper-gloss card) | Same commit, same reason |
| Modify: `skills/paper-figures/SKILL.md` | Two-sentence contract note in the Phase 6 lightbox paragraph; description unchanged |

No script imports another; the injector reads the assets from its sibling `assets/` dir so
the generation path and the retrofit path embed byte-identical runtime.

**Branch:** `feat/paper-gloss-annotations` (create fresh off pulled `main`).

---

## Stage 0 — Scaffolding

### Task 0: Create the assets directory

**Files:**
- Create: `skills/paper-gloss/assets/` (directory)

- [ ] **Step 1: Create the directory and confirm the existing test runner still passes**

```bash
cd /Users/kyledisch/Projects/claude-config
mkdir -p skills/paper-gloss/assets
cd skills/paper-gloss/scripts && python3 -m unittest discover -s tests -v
```

Expected: the existing check_math/convert_math tests run and end `OK` (baseline before we
add anything).

No commit yet — an empty directory isn't tracked by git; it lands with Task 1.

---

## Stage 1 — The injector

### Task 1: `inject_annotations.py` — stamp ids, set slug, embed assets, check

**Files:**
- Create: `skills/paper-gloss/scripts/inject_annotations.py`
- Test: `skills/paper-gloss/scripts/tests/test_inject_annotations.py`

- [ ] **Step 1: Write the failing test**

Create `skills/paper-gloss/scripts/tests/test_inject_annotations.py`:

```python
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inject_annotations import (  # noqa: E402
    check_page,
    derive_slug,
    embed_assets,
    set_slug,
    stamp_ids,
)

FIXTURE = """<!doctype html>
<html><head><title>T</title><style>:root { --fg: #111; }</style></head>
<body>
<h2>Heading</h2>
<p>alpha paragraph</p>
<p id="keep-me">beta paragraph</p>
<pre class="equation" data-math-verbatim="1">$x$</pre>
<ul><li>an item</li></ul>
<dl><dt><span class="math"><i>Q</i></span></dt><dd>the queries</dd></dl>
</body></html>
"""


class TestStampIds(unittest.TestCase):
    def setUp(self):
        self.out, self.added = stamp_ids(FIXTURE)

    def test_stamps_every_block(self):
        # h2, BOTH p (including the one carrying its own id), li, dd
        self.assertEqual(self.added, 5)
        for frag in ('<h2 data-pg-block="pg-p-0001">',
                     '<p data-pg-block="pg-p-0002">',
                     '<p data-pg-block="pg-p-0003" id="keep-me">',
                     '<li data-pg-block="pg-p-0004">',
                     '<dd data-pg-block="pg-p-0005">'):
            self.assertIn(frag, self.out)

    def test_existing_id_preserved(self):
        # ids are never the marker: real pages have 77/79 headings and all
        # footnotes already carrying ids, and those must stay annotatable
        self.assertIn('id="keep-me"', self.out)

    def test_pre_is_not_stamped(self):
        self.assertIn('<pre class="equation" data-math-verbatim="1">', self.out)
        self.assertNotIn('<pre data-pg-block=', self.out)

    def test_dt_is_not_stamped(self):
        self.assertIn("<dt>", self.out)

    def test_idempotent(self):
        again, added = stamp_ids(self.out)
        self.assertEqual(added, 0)
        self.assertEqual(again, self.out)

    def test_numbering_continues_past_existing_markers(self):
        doc = '<body><p data-pg-block="pg-p-0007">a</p><p>b</p></body>'
        out, added = stamp_ids(doc)
        self.assertEqual(added, 1)
        self.assertIn('<p data-pg-block="pg-p-0008">b</p>', out)

    def test_ignores_block_lookalikes_inside_scripts(self):
        # The runtime JS (and GLOSS_TERMS) contain strings like '<h2>…</h2>';
        # stamping inside a <script> span would corrupt the JS and break
        # idempotency on a second run.
        doc = ('<body><script>var s = "<p>fake</p><h2>x</h2>";</script>'
               '<p>real</p></body>')
        out, added = stamp_ids(doc)
        self.assertEqual(added, 1)
        self.assertIn('<script>var s = "<p>fake</p><h2>x</h2>";</script>', out)
        self.assertIn('<p data-pg-block="pg-p-0001">real</p>', out)


class TestSlug(unittest.TestCase):
    def test_derive_slug(self):
        self.assertEqual(
            derive_slug("/x/y/forge-gap-eli5-glossed.html"), "forge-gap"
        )

    def test_derive_slug_without_suffix_uses_stem(self):
        self.assertEqual(derive_slug("/x/oddball.html"), "oddball")

    def test_set_slug_adds_attribute(self):
        out = set_slug("<body>\n<p>x</p></body>", "forge-gap")
        self.assertIn('<body data-pg-slug="forge-gap">', out)

    def test_set_slug_replaces_existing(self):
        out = set_slug('<body data-pg-slug="old" class="c">x</body>', "new")
        self.assertIn('data-pg-slug="new"', out)
        self.assertNotIn('data-pg-slug="old"', out)
        self.assertIn('class="c"', out)


class TestEmbed(unittest.TestCase):
    CSS = ".pg-hl { background: gold; }"
    JS = "window.closeAnnotationUI = function () {};"

    def test_embeds_both_blocks_once(self):
        out = embed_assets(FIXTURE, self.CSS, self.JS)
        self.assertEqual(out.count('<style id="pg-annot-css">'), 1)
        self.assertEqual(out.count('<script id="pg-annot-js">'), 1)
        self.assertLess(out.index("pg-annot-css"), out.index("</head>"))
        self.assertLess(out.index("pg-annot-js"), out.index("</body>"))

    def test_rerun_replaces_not_duplicates(self):
        once = embed_assets(FIXTURE, self.CSS, self.JS)
        twice = embed_assets(once, ".pg-hl { background: red; }", self.JS)
        self.assertEqual(twice.count('<style id="pg-annot-css">'), 1)
        self.assertIn("background: red", twice)
        self.assertNotIn("background: gold", twice)


class TestCheck(unittest.TestCase):
    CSS = ".pg-hl { background: gold; }"
    JS = "window.closeAnnotationUI = function () {};"

    def full(self):
        out, _ = stamp_ids(FIXTURE)
        out = set_slug(out, "t-paper")
        return embed_assets(out, self.CSS, self.JS)

    def test_clean_page_passes(self):
        self.assertEqual(check_page(self.full()), [])

    def test_raw_page_fails_with_named_problems(self):
        problems = check_page(FIXTURE)
        joined = " ".join(problems)
        self.assertIn("pg-annot-css", joined)
        self.assertIn("pg-annot-js", joined)
        self.assertIn("data-pg-slug", joined)
        self.assertIn("unstamped", joined)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-gloss/scripts && python3 -m unittest tests.test_inject_annotations -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'inject_annotations'`

- [ ] **Step 3: Write the implementation**

Create `skills/paper-gloss/scripts/inject_annotations.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-gloss/scripts && python3 -m unittest tests.test_inject_annotations -v`
Expected: `Ran 15 tests` … `OK`

- [ ] **Step 5: Run the whole paper-gloss suite (no collateral damage)**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-gloss/scripts && python3 -m unittest discover -s tests -v`
Expected: all tests (existing + 15 new) end `OK`.

- [ ] **Step 6: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-gloss/scripts/inject_annotations.py skills/paper-gloss/scripts/tests/test_inject_annotations.py
git commit -m "feat(paper-gloss): add the annotation-layer injector with id stamping"
```

Note: `load_assets()` will fail until Stage 2/3 land the asset files — the unit tests
deliberately test the pure functions and never call it.

---

## Stage 2 — The stylesheet asset

### Task 2: `assets/annotations.css`

**Files:**
- Create: `skills/paper-gloss/assets/annotations.css`

- [ ] **Step 1: Write the stylesheet**

All values through `--pg-annot-*` variables the block defines itself (host pages define
their own variable sets with unknown names, so the layer must be self-sufficient), with the
same two override layers as the page: dark media query, then `data-theme` attributes which
must win in both directions.

```css
:root {
  --pg-hl-bg: rgba(255, 213, 79, 0.45);
  --pg-hl-noted: rgba(217, 119, 6, 0.9);
  --pg-annot-bg: #ffffff;
  --pg-annot-fg: #1f1f1f;
  --pg-annot-border: #cfcfcf;
  --pg-annot-accent: #b45309;
  --pg-annot-muted: #6b6b6b;
  --pg-annot-backdrop: rgba(0, 0, 0, 0.35);
  --pg-annot-flash: rgba(255, 167, 38, 0.55);
}
@media (prefers-color-scheme: dark) {
  :root {
    --pg-hl-bg: rgba(202, 138, 4, 0.38);
    --pg-hl-noted: rgba(245, 158, 11, 0.9);
    --pg-annot-bg: #232323;
    --pg-annot-fg: #e8e8e8;
    --pg-annot-border: #484848;
    --pg-annot-accent: #f59e0b;
    --pg-annot-muted: #9a9a9a;
    --pg-annot-backdrop: rgba(0, 0, 0, 0.55);
    --pg-annot-flash: rgba(245, 158, 11, 0.45);
  }
}
:root[data-theme="dark"] {
  --pg-hl-bg: rgba(202, 138, 4, 0.38);
  --pg-hl-noted: rgba(245, 158, 11, 0.9);
  --pg-annot-bg: #232323;
  --pg-annot-fg: #e8e8e8;
  --pg-annot-border: #484848;
  --pg-annot-accent: #f59e0b;
  --pg-annot-muted: #9a9a9a;
  --pg-annot-backdrop: rgba(0, 0, 0, 0.55);
  --pg-annot-flash: rgba(245, 158, 11, 0.45);
}
:root[data-theme="light"] {
  --pg-hl-bg: rgba(255, 213, 79, 0.45);
  --pg-hl-noted: rgba(217, 119, 6, 0.9);
  --pg-annot-bg: #ffffff;
  --pg-annot-fg: #1f1f1f;
  --pg-annot-border: #cfcfcf;
  --pg-annot-accent: #b45309;
  --pg-annot-muted: #6b6b6b;
  --pg-annot-backdrop: rgba(0, 0, 0, 0.35);
  --pg-annot-flash: rgba(255, 167, 38, 0.55);
}

mark.pg-hl {
  background: var(--pg-hl-bg);
  color: inherit;
  padding: 0;
  border-radius: 2px;
}
mark.pg-hl--noted { border-bottom: 2px solid var(--pg-hl-noted); }
mark.pg-hl--flash { animation: pg-annot-flash 1.2s ease-out; }
@keyframes pg-annot-flash {
  0% { background: var(--pg-annot-flash); }
  100% { background: var(--pg-hl-bg); }
}

.pg-annot-ui, .pg-annot-ui * { box-sizing: border-box; }
.pg-annot-ui button {
  font: inherit;
  color: inherit;
  background: none;
  border: none;
  cursor: pointer;
}

.pg-annot-toolbar {
  position: absolute;
  z-index: 1200;
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem;
  background: var(--pg-annot-bg);
  color: var(--pg-annot-fg);
  border: 1px solid var(--pg-annot-border);
  border-radius: 8px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
}
.pg-annot-toolbar button {
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.85rem;
}
.pg-annot-toolbar button:hover { background: var(--pg-hl-bg); }

.pg-annot-editor,
.pg-annot-fallback {
  position: absolute;
  z-index: 1200;
  width: min(360px, 92vw);
  padding: 0.75rem;
  background: var(--pg-annot-bg);
  color: var(--pg-annot-fg);
  border: 1px solid var(--pg-annot-border);
  border-radius: 10px;
  box-shadow: 0 6px 22px rgba(0, 0, 0, 0.22);
}
.pg-annot-fallback { position: fixed; top: 15vh; left: 50%; transform: translateX(-50%); }
.pg-annot-editor-quote {
  font-size: 0.82rem;
  color: var(--pg-annot-muted);
  border-left: 3px solid var(--pg-hl-noted);
  padding-left: 0.5rem;
  margin-bottom: 0.5rem;
  max-height: 4.6em;
  overflow: hidden;
}
.pg-annot-editor textarea,
.pg-annot-fallback textarea {
  width: 100%;
  font: inherit;
  font-size: 0.9rem;
  color: var(--pg-annot-fg);
  background: var(--pg-annot-bg);
  border: 1px solid var(--pg-annot-border);
  border-radius: 6px;
  padding: 0.4rem;
  resize: vertical;
}
.pg-annot-fallback textarea { height: 10rem; }
.pg-annot-actions {
  display: flex;
  gap: 0.4rem;
  justify-content: flex-end;
  margin-top: 0.5rem;
}
.pg-annot-actions button {
  padding: 0.3rem 0.7rem;
  border-radius: 6px;
  font-size: 0.85rem;
  border: 1px solid var(--pg-annot-border);
}
.pg-annot-actions button[data-act="save"] {
  background: var(--pg-annot-accent);
  color: #fff;
  border-color: var(--pg-annot-accent);
}

.pg-annot-toggle {
  position: fixed;
  top: 3.4rem;
  right: 1rem;
  /* below the figure lightbox (1000) so an open figure covers the pill; the
     runtime hides the toggle entirely while the annotation panel is open */
  z-index: 900;
  padding: 0.35rem 0.7rem;
  background: var(--pg-annot-bg);
  color: var(--pg-annot-fg);
  border: 1px solid var(--pg-annot-border);
  border-radius: 999px;
  font-size: 0.85rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.pg-annot-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1190;
  background: var(--pg-annot-backdrop);
}
.pg-annot-panel {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 1195;
  width: min(420px, 90vw);
  height: 100%;
  overflow-y: auto;
  padding: 1rem;
  background: var(--pg-annot-bg);
  color: var(--pg-annot-fg);
  border-left: 1px solid var(--pg-annot-border);
}
.pg-annot-panel h2 { margin: 0 0 0.25rem; font-size: 1.1rem; }
.pg-annot-panel-close {
  position: absolute;
  top: 0.6rem;
  right: 0.8rem;
  font-size: 1.3rem;
  line-height: 1;
}
.pg-annot-hint {
  font-size: 0.78rem;
  color: var(--pg-annot-muted);
  margin: 0.25rem 0 0.75rem;
}
.pg-annot-status { font-size: 0.8rem; color: var(--pg-annot-accent); min-height: 1.2em; }
.pg-annot-list, .pg-annot-orphans ol {
  list-style: none;
  margin: 0.5rem 0 0;
  padding: 0;
}
.pg-annot-list li, .pg-annot-orphans li {
  border-top: 1px solid var(--pg-annot-border);
  padding: 0.6rem 0;
}
.pg-annot-item-section {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--pg-annot-muted);
}
.pg-annot-item-quote {
  font-size: 0.85rem;
  border-left: 3px solid var(--pg-hl-noted);
  padding-left: 0.5rem;
  margin: 0.25rem 0;
}
.pg-annot-item-note { font-size: 0.85rem; white-space: pre-wrap; }
.pg-annot-item-actions { display: flex; gap: 0.6rem; margin-top: 0.3rem; }
.pg-annot-item-actions button {
  font-size: 0.78rem;
  color: var(--pg-annot-accent);
  padding: 0;
}
.pg-annot-orphans h3 { font-size: 0.9rem; margin: 1rem 0 0; }
```

- [ ] **Step 2: Sanity-check the two-layer theme contract**

Run: `python3 -c "
css = open('/Users/kyledisch/Projects/claude-config/skills/paper-gloss/assets/annotations.css').read()
import re
blocks = {
  'root': re.search(r'^:root \{(.*?)\}', css, re.S).group(1),
  'media': re.search(r'prefers-color-scheme: dark.*?\{.*?:root \{(.*?)\}', css, re.S).group(1),
  'dark': re.search(r':root\[data-theme=\"dark\"\] \{(.*?)\}', css, re.S).group(1),
  'light': re.search(r':root\[data-theme=\"light\"\] \{(.*?)\}', css, re.S).group(1),
}
names = {k: set(re.findall(r'(--[\w-]+):', v)) for k, v in blocks.items()}
assert names['root'] == names['media'] == names['dark'] == names['light'], names
print('theme blocks define identical variable sets:', len(names['root']), 'vars')
"`
Expected: `theme blocks define identical variable sets: 9 vars`

- [ ] **Step 3: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-gloss/assets/annotations.css
git commit -m "feat(paper-gloss): annotation-layer stylesheet with two-layer theming"
```

---

## Stage 3 — The runtime asset

### Task 3: `assets/annotations.js`

**Files:**
- Create: `skills/paper-gloss/assets/annotations.js`

- [ ] **Step 1: Write the runtime**

Complete file — every design rule from *Settled decisions* is realized here (anchoring in
`captureTarget`/`locate`, never-mark-math in `markRange`, surface coordination in the
delegated click listener and `closeOtherSurfaces`, export contract in `saveFile`):

```js
(function () {
  'use strict';
  if (window.__pgAnnotInit) return;
  window.__pgAnnotInit = true;

  /* ---------- config ---------- */
  var SLUG = document.body.getAttribute('data-pg-slug') || 'paper';
  var KEY = 'pg-annotations:' + SLUG;
  var CTX = 32;
  var EXCLUDE = 'script,style,.math,math,pre.equation,' +
    '#gloss-popover,#gloss-panel,#gloss-backdrop,#figure-lightbox,.pg-annot-ui';

  /* ---------- storage ---------- */
  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) {
        var p = JSON.parse(raw);
        if (p && p.v === 1 && Array.isArray(p.annotations)) return p;
      }
    } catch (e) { /* private mode or corrupt payload: start empty */ }
    return { v: 1, slug: SLUG, title: document.title, annotations: [] };
  }
  var storageOk = true;
  function persist() {
    // Never silent: partitioned iframe storage is a live path, and a badge
    // that counts up while nothing persists is the lie D3 forbids.
    try {
      localStorage.setItem(KEY, JSON.stringify(store));
      storageOk = true;
    } catch (e) {
      storageOk = false;
    }
    updateHint();
  }
  function updateHint() {
    var h = panel && panel.querySelector('.pg-annot-hint');
    if (!h) return;
    h.textContent = storageOk
      ? 'Notes live in this browser only — export to keep them safe.'
      : '⚠️ Not saved in this browser (storage unavailable) — export before you close this tab.';
  }
  var store = load();
  var posCache = {};   // id -> {bi, start} for document-order sorting
  var orphans = [];    // ids that failed to re-anchor this session

  function newId() {
    return 'a-' + Date.now().toString(36) + '-' +
      Math.random().toString(36).slice(2, 6);
  }
  function byId(id) {
    for (var i = 0; i < store.annotations.length; i++) {
      if (store.annotations[i].id === id) return store.annotations[i];
    }
    return null;
  }

  /* ---------- anchoring ---------- */
  function allBlocks() {
    return Array.prototype.slice.call(
      document.querySelectorAll('[data-pg-block]'));
  }
  function blockOf(node) {
    var el = node.nodeType === 1 ? node : node.parentElement;
    return el ? el.closest('[data-pg-block]') : null;
  }
  function sectionOf(block) {
    var bs = allBlocks(), i = bs.indexOf(block);
    for (var k = i; k >= 0; k--) {
      if (/^H[1-6]$/.test(bs[k].tagName)) return bs[k].textContent.trim();
    }
    return '';
  }
  function offsetIn(block, container, offset) {
    var r = document.createRange();
    r.selectNodeContents(block);
    r.setEnd(container, offset);
    return r.toString().length;
  }
  function captureTarget(range) {
    var b1 = blockOf(range.startContainer);
    var b2 = blockOf(range.endContainer);
    if (!b1 || b1 !== b2) return null;   // v1: single-block highlights only
    var text = b1.textContent;
    var start = offsetIn(b1, range.startContainer, range.startOffset);
    var exact = range.toString();
    if (!exact.trim()) return null;
    return {
      pid: b1.getAttribute('data-pg-block'),
      exact: exact,
      prefix: text.slice(Math.max(0, start - CTX), start),
      suffix: text.slice(start + exact.length, start + exact.length + CTX),
      offset: start,
      section: sectionOf(b1)
    };
  }
  function indexesOf(hay, needle) {
    var out = [], i = hay.indexOf(needle);
    while (i !== -1) { out.push(i); i = hay.indexOf(needle, i + 1); }
    return out;
  }
  function scoreAt(text, i, a) {
    var s = 0;
    if (a.prefix &&
        text.slice(Math.max(0, i - a.prefix.length), i) === a.prefix) s += 2;
    if (a.suffix &&
        text.slice(i + a.exact.length,
                   i + a.exact.length + a.suffix.length) === a.suffix) s += 2;
    if (typeof a.offset === 'number') {
      s -= Math.min(1, Math.abs(i - a.offset) / 1000);
    }
    return s;
  }
  function locate(a) {
    var candidates = [];
    var own = a.pid &&
      document.querySelector('[data-pg-block="' + a.pid + '"]');
    if (own) candidates.push(own);
    allBlocks().forEach(function (b) { if (b !== own) candidates.push(b); });
    for (var k = 0; k < candidates.length; k++) {
      var b = candidates[k], text = b.textContent;
      var hits = indexesOf(text, a.exact);
      if (!hits.length) continue;
      var best = hits[0], bestScore = -Infinity;
      for (var h = 0; h < hits.length; h++) {
        var s = scoreAt(text, hits[h], a);
        if (s > bestScore) { bestScore = s; best = hits[h]; }
      }
      return { block: b, start: best, end: best + a.exact.length };
    }
    return null;
  }

  /* ---------- mark rendering ---------- */
  function markRange(block, start, end, id, noted) {
    var walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT, null);
    var pos = 0, node, jobs = [];
    while ((node = walker.nextNode())) {
      var len = node.nodeValue.length;
      var nStart = pos, nEnd = pos + len;
      pos = nEnd;
      if (nEnd <= start || nStart >= end) continue;
      if (node.parentElement && node.parentElement.closest(EXCLUDE)) continue;
      jobs.push({
        node: node,
        from: Math.max(start, nStart) - nStart,
        to: Math.min(end, nEnd) - nStart
      });
    }
    jobs.forEach(function (j) {
      var target = j.node;
      if (j.from > 0) target = target.splitText(j.from);
      if (j.to - j.from < target.nodeValue.length) target.splitText(j.to - j.from);
      var m = document.createElement('mark');
      m.className = 'pg-hl' + (noted ? ' pg-hl--noted' : '');
      m.setAttribute('data-annot-id', id);
      target.parentNode.insertBefore(m, target);
      m.appendChild(target);
    });
    return jobs.length;
  }
  function unmark(id) {
    var marks = document.querySelectorAll(
      'mark.pg-hl[data-annot-id="' + id + '"]');
    Array.prototype.forEach.call(marks, function (m) {
      var parent = m.parentNode;
      while (m.firstChild) parent.insertBefore(m.firstChild, m);
      parent.removeChild(m);
      parent.normalize();
    });
  }
  function renderAnnotation(a, blockIndex) {
    var loc = locate(a);
    if (!loc) { orphans.push(a.id); return; }
    var made = markRange(loc.block, loc.start, loc.end, a.id, !!a.note);
    if (!made) {
      // quote matched, but every segment sits in excluded content (math,
      // chrome): no mark exists to jump to, so file it as unanchored rather
      // than letting a ghost row with a dead Jump button count as anchored
      orphans.push(a.id);
      return;
    }
    var marker = loc.block.getAttribute('data-pg-block');
    if (a.pid !== marker) a.pid = marker;  // heal drift
    posCache[a.id] = { bi: blockIndex.get(loc.block), start: loc.start };
  }
  function renderAll() {
    Array.prototype.forEach.call(
      document.querySelectorAll('mark.pg-hl'),
      function (m) {
        var parent = m.parentNode;
        while (m.firstChild) parent.insertBefore(m.firstChild, m);
        parent.removeChild(m);
      });
    posCache = {};
    orphans = [];
    var blockIndex = new Map();
    allBlocks().forEach(function (b, i) { blockIndex.set(b, i); });
    store.annotations.forEach(function (a) { renderAnnotation(a, blockIndex); });
    persist();  // pids may have healed
  }
  function ordered() {
    return store.annotations.slice().sort(function (x, y) {
      var px = posCache[x.id], py = posCache[y.id];
      if (px && py) return (px.bi - py.bi) || (px.start - py.start);
      if (px) return -1;
      if (py) return 1;
      return (x.created || '').localeCompare(y.created || '');
    });
  }

  /* ---------- surface coordination ---------- */
  function closeOtherSurfaces() {
    // Prefer the hooks a post-amendment page exports; the six retrofit
    // targets mostly predate them (five export nothing, jacobian-lens only
    // closeGlossSurfaces + closeFigureLightbox), so also drive the surfaces'
    // own markup by id — same layered pattern as paper-figures' lightbox.
    ['closeGlossSurfaces', 'closeGlossPopover', 'closeGlossPanel',
     'closeFigureLightbox'].forEach(function (fn) {
      if (typeof window[fn] === 'function') window[fn]();
    });
    ['gloss-popover', 'gloss-panel', 'gloss-backdrop', 'figure-lightbox']
      .forEach(function (id) {
        var n = document.getElementById(id);
        if (n && !n.hidden) n.hidden = true;
      });
    var gt = document.getElementById('gloss-panel-toggle');
    if (gt) gt.setAttribute('aria-expanded', 'false');
  }
  function closeAnnotationUI() {
    hideToolbar();
    closeEditor(false);
    closePanel();
    fallback.hidden = true;
  }
  window.closeAnnotationUI = closeAnnotationUI;

  /* ---------- UI construction ---------- */
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  var toolbar = el('div', 'pg-annot-toolbar pg-annot-ui',
    '<button type="button" data-act="hl">Highlight</button>' +
    '<button type="button" data-act="note">Note</button>');
  toolbar.hidden = true;

  var editor = el('div', 'pg-annot-editor pg-annot-ui',
    '<div class="pg-annot-editor-quote"></div>' +
    '<textarea rows="4" placeholder="Add a note…"></textarea>' +
    '<div class="pg-annot-actions">' +
    '<button type="button" data-act="delete">Delete</button>' +
    '<button type="button" data-act="cancel">Cancel</button>' +
    '<button type="button" data-act="save">Save</button></div>');
  editor.hidden = true;

  var toggle = el('button', 'pg-annot-toggle pg-annot-ui');
  toggle.type = 'button';
  toggle.setAttribute('aria-expanded', 'false');

  var backdrop = el('div', 'pg-annot-backdrop pg-annot-ui');
  backdrop.hidden = true;

  var panel = el('aside', 'pg-annot-panel pg-annot-ui',
    '<button type="button" class="pg-annot-panel-close" aria-label="Close">×</button>' +
    '<h2>Annotations</h2>' +
    '<div class="pg-annot-hint">Notes live in this browser only — export to keep them safe.</div>' +
    '<div class="pg-annot-actions" style="justify-content:flex-start">' +
    '<button type="button" data-act="export-md">Export Markdown</button>' +
    '<button type="button" data-act="export-json">Export JSON</button>' +
    '<button type="button" data-act="import">Import</button>' +
    '<input type="file" accept=".json,application/json" hidden></div>' +
    '<div class="pg-annot-status"></div>' +
    '<ol class="pg-annot-list"></ol>' +
    '<div class="pg-annot-orphans" hidden><h3>Unanchored</h3><ol></ol></div>');
  panel.hidden = true;

  var fallback = el('div', 'pg-annot-fallback pg-annot-ui',
    '<p class="pg-annot-fallback-msg"></p>' +
    '<textarea readonly></textarea>' +
    '<div class="pg-annot-actions">' +
    '<button type="button" data-act="copy">Copy</button>' +
    '<button type="button" data-act="close">Close</button></div>');
  fallback.hidden = true;

  [toolbar, editor, toggle, backdrop, panel, fallback].forEach(function (n) {
    document.body.appendChild(n);
  });

  function updateBadge() {
    toggle.textContent = '✏️ Notes (' + store.annotations.length + ')';
  }
  function status(msg) {
    panel.querySelector('.pg-annot-status').textContent = msg || '';
  }

  /* ---------- toolbar ---------- */
  function hideToolbar() { toolbar.hidden = true; }
  function placeAt(node, rect) {
    node.style.left = Math.max(8, Math.min(
      window.scrollX + rect.left,
      window.scrollX + document.documentElement.clientWidth - node.offsetWidth - 8
    )) + 'px';
    node.style.top = (window.scrollY + rect.top - node.offsetHeight - 8) + 'px';
  }
  function maybeShowToolbar() {
    var sel = window.getSelection();
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) { hideToolbar(); return; }
    var range = sel.getRangeAt(0);
    var anchor = range.startContainer.nodeType === 1 ?
      range.startContainer : range.startContainer.parentElement;
    if (anchor && anchor.closest('.pg-annot-ui')) return;
    if (!captureTarget(range)) { hideToolbar(); return; }
    toolbar.hidden = false;
    placeAt(toolbar, range.getBoundingClientRect());
  }
  document.addEventListener('mouseup', function () {
    setTimeout(maybeShowToolbar, 0);
  });
  // Touch selection (long-press handles) and keyboard selection (Shift+arrows)
  // don't reliably emit mouseup — selectionchange is the path that covers them.
  var selTimer = null;
  document.addEventListener('selectionchange', function () {
    clearTimeout(selTimer);
    selTimer = setTimeout(maybeShowToolbar, 250);
  });
  toolbar.addEventListener('mousedown', function (e) { e.preventDefault(); });
  toolbar.addEventListener('click', function (e) {
    var btn = e.target.closest('button');
    if (!btn) return;
    var sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) { hideToolbar(); return; }
    var target = captureTarget(sel.getRangeAt(0));
    hideToolbar();
    if (!target) return;
    sel.removeAllRanges();
    var a = {
      id: newId(), exact: target.exact, prefix: target.prefix,
      suffix: target.suffix, pid: target.pid, offset: target.offset,
      note: '', section: target.section,
      created: new Date().toISOString()
    };
    store.annotations.push(a);
    persist();
    renderAll();
    updateBadge();
    if (btn.getAttribute('data-act') === 'note') openEditor(a.id, true);
  });

  /* ---------- editor ---------- */
  var editorState = { id: null, fresh: false };
  function openEditor(id, fresh) {
    var a = byId(id);
    if (!a) return;
    closeOtherSurfaces();
    closePanel();
    hideToolbar();
    editorState = { id: id, fresh: !!fresh };
    editor.querySelector('.pg-annot-editor-quote').textContent =
      a.exact.length > 200 ? a.exact.slice(0, 200) + '…' : a.exact;
    editor.querySelector('textarea').value = a.note || '';
    editor.hidden = false;
    var m = document.querySelector('mark.pg-hl[data-annot-id="' + id + '"]');
    if (m) placeAt(editor, m.getBoundingClientRect());
    else { editor.style.left = '50%'; editor.style.top = (window.scrollY + 120) + 'px'; }
    editor.querySelector('textarea').focus();
  }
  function removeAnnotation(id) {
    unmark(id);
    store.annotations = store.annotations.filter(function (a) { return a.id !== id; });
    delete posCache[id];
    persist();
    updateBadge();
  }
  function closeEditor(commit) {
    // Closing without commit DISMISSES — it never deletes. "Highlight →
    // start a note → click a jargon term to check it" is the page's most
    // natural gesture and must not destroy the highlight; only the explicit
    // Cancel button discards a fresh one (below).
    if (editor.hidden) return;
    var a = byId(editorState.id);
    if (a && commit) {
      a.note = editor.querySelector('textarea').value.trim();
      persist();
      renderAll();
    }
    editor.hidden = true;
    editorState = { id: null, fresh: false };
  }
  editor.addEventListener('click', function (e) {
    var btn = e.target.closest('button');
    if (!btn) return;
    var act = btn.getAttribute('data-act');
    if (act === 'save') closeEditor(true);
    else if (act === 'cancel') {
      var wasFresh = editorState.fresh, freshId = editorState.id;
      closeEditor(false);
      var fa = byId(freshId);
      if (wasFresh && fa && !fa.note) removeAnnotation(freshId);
    }
    else if (act === 'delete') {
      var id = editorState.id;
      editorState = { id: null, fresh: false };
      editor.hidden = true;
      removeAnnotation(id);
      refreshPanelList();
    }
  });

  /* ---------- panel ---------- */
  function openPanel() {
    closeOtherSurfaces();
    hideToolbar();
    closeEditor(false);
    refreshPanelList();
    panel.hidden = false;
    backdrop.hidden = false;
    // hide the toggle while the panel is open: its z-index sits below the
    // lightbox and the backdrop by design, so it must not be the close control
    toggle.hidden = true;
    toggle.setAttribute('aria-expanded', 'true');
  }
  function closePanel() {
    panel.hidden = true;
    backdrop.hidden = true;
    toggle.hidden = false;
    toggle.setAttribute('aria-expanded', 'false');
  }
  function itemFor(a, anchored) {
    var li = document.createElement('li');
    var sec = el('div', 'pg-annot-item-section');
    sec.textContent = a.section || '';
    var q = el('blockquote', 'pg-annot-item-quote');
    q.textContent = a.exact.length > 140 ? a.exact.slice(0, 140) + '…' : a.exact;
    var note = el('div', 'pg-annot-item-note');
    note.textContent = a.note || '';
    var actions = el('div', 'pg-annot-item-actions');
    if (anchored) {
      var jump = el('button', '', 'Jump'); jump.type = 'button';
      jump.addEventListener('click', function () {
        closePanel();
        var m = document.querySelector('mark.pg-hl[data-annot-id="' + a.id + '"]');
        if (!m) return;
        m.scrollIntoView({ block: 'center' });
        m.classList.add('pg-hl--flash');
        setTimeout(function () { m.classList.remove('pg-hl--flash'); }, 1300);
      });
      actions.appendChild(jump);
    }
    var edit = el('button', '', 'Edit'); edit.type = 'button';
    edit.addEventListener('click', function () { openEditor(a.id, false); });
    var del = el('button', '', 'Delete'); del.type = 'button';
    del.addEventListener('click', function () {
      removeAnnotation(a.id);
      refreshPanelList();
    });
    actions.appendChild(edit);
    actions.appendChild(del);
    li.appendChild(sec); li.appendChild(q);
    if (a.note) li.appendChild(note);
    li.appendChild(actions);
    return li;
  }
  function refreshPanelList() {
    var list = panel.querySelector('.pg-annot-list');
    var orphanBox = panel.querySelector('.pg-annot-orphans');
    var orphanList = orphanBox.querySelector('ol');
    list.innerHTML = '';
    orphanList.innerHTML = '';
    ordered().forEach(function (a) {
      if (orphans.indexOf(a.id) === -1) list.appendChild(itemFor(a, true));
      else orphanList.appendChild(itemFor(a, false));
    });
    orphanBox.hidden = orphanList.children.length === 0;
  }
  toggle.addEventListener('click', function () {
    if (panel.hidden) openPanel(); else closePanel();
  });
  panel.querySelector('.pg-annot-panel-close')
    .addEventListener('click', closePanel);
  backdrop.addEventListener('click', closePanel);

  /* ---------- export / import ---------- */
  function exportPayload() {
    return {
      v: 1, kind: 'paper-gloss-annotations', slug: SLUG,
      title: store.title || document.title, url: location.href,
      exported: new Date().toISOString(), annotations: ordered()
    };
  }
  function toMarkdown(p) {
    var lines = [
      '---',
      'paper: "' + p.title.replace(/"/g, '\\"') + '"',
      'url: "' + p.url + '"',
      'exported: ' + p.exported,
      'tags: [paper-annotations]',
      '---',
      '',
      '# Annotations — ' + p.title,
      ''
    ];
    var section = null;
    p.annotations.forEach(function (a) {
      var s = a.section || 'Untitled section';
      if (s !== section) { section = s; lines.push('## ' + s, ''); }
      lines.push('> ' + a.exact.replace(/\r?\n/g, ' '), '');
      if (a.note) lines.push(a.note, '');
    });
    return lines.join('\n');
  }
  function showFallback(filename, text, msg) {
    closeOtherSurfaces();
    fallback.querySelector('.pg-annot-fallback-msg').textContent =
      (msg || 'Saving isn’t available here.') +
      ' Copy the text below into a file named ' + filename + '.';
    fallback.querySelector('textarea').value = text;
    fallback.hidden = false;
  }
  fallback.addEventListener('click', function (e) {
    var btn = e.target.closest('button');
    if (!btn) return;
    if (btn.getAttribute('data-act') === 'close') { fallback.hidden = true; return; }
    var ta = fallback.querySelector('textarea');
    ta.select();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(ta.value).then(function () {
        btn.textContent = 'Copied ✓';
      }, function () { btn.textContent = 'Press ⌘C to copy'; });
    } else { btn.textContent = 'Press ⌘C to copy'; }
  });
  function saveFile(filename, text) {
    var dl = window.claude && window.claude.downloads;
    if (!dl) { showFallback(filename, text); return; }
    dl.save({ filename: filename, data: text }).then(function () {
      status('Saved ' + filename);
    }, function (err) {
      if (err && err.code === 'declined') return;  // viewer's call; no retry
      if (err && err.code === 'rate_limited') {
        showFallback(filename, text,
          'A download prompt was already open — copy instead, or try again shortly.');
        return;
      }
      showFallback(filename, text);
    });
  }
  function importPayload(text) {
    var p;
    try { p = JSON.parse(text); } catch (e) { status('Import failed: not valid JSON'); return; }
    if (!p || p.v !== 1 || !Array.isArray(p.annotations)) {
      status('Import failed: not an annotations export'); return;
    }
    var existing = {};
    store.annotations.forEach(function (a) { existing[a.id] = true; });
    var added = 0, skipped = 0;
    p.annotations.forEach(function (a) {
      if (a && a.id && !existing[a.id] && typeof a.exact === 'string') {
        store.annotations.push(a); existing[a.id] = true; added++;
      } else skipped++;
    });
    persist();
    renderAll();
    updateBadge();
    refreshPanelList();
    status('Imported ' + added + (skipped ? ' (skipped ' + skipped + ' duplicate/invalid)' : '') +
      (p.slug !== SLUG ? ' — note: export was from "' + p.slug + '"' : ''));
  }
  panel.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-act]');
    if (!btn) return;
    var act = btn.getAttribute('data-act');
    if (act === 'export-md') saveFile(SLUG + '-annotations.md', toMarkdown(exportPayload()));
    else if (act === 'export-json') saveFile(SLUG + '-annotations.json', JSON.stringify(exportPayload(), null, 2));
    else if (act === 'import') panel.querySelector('input[type="file"]').click();
  });
  panel.querySelector('input[type="file"]').addEventListener('change', function () {
    var f = this.files && this.files[0];
    this.value = '';
    if (!f) return;
    var reader = new FileReader();
    reader.onload = function () { importPayload(String(reader.result)); };
    reader.readAsText(f);
  });

  /* ---------- global coordination listeners ---------- */
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    // another surface is opening: get out of its way (their own handlers run too)
    if (t.closest('.gloss-term') || t.closest('#gloss-panel-toggle') ||
        t.closest('.paper-figure img')) {
      closeAnnotationUI();
      return;
    }
    if (t.closest('.pg-annot-ui')) return;
    var m = t.closest('mark.pg-hl');
    if (m && !m.closest('.gloss-term')) {   // a highlight inside a gloss button defers to the popover
      closeOtherSurfaces();
      openEditor(m.getAttribute('data-annot-id'), false);
      return;
    }
    hideToolbar();
    closeEditor(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAnnotationUI();
  });

  /* ---------- init ---------- */
  renderAll();
  updateBadge();
})();
```

- [ ] **Step 2: Syntax-check without a browser**

`node` isn't a guaranteed local dependency; use Python's built-in check that the injector
can at least embed it, then rely on Stage 5 for real execution:

```bash
cd /Users/kyledisch/Projects/claude-config/skills/paper-gloss
python3 - <<'EOF'
js = open('assets/annotations.js').read()
assert js.count('(') == js.count(')'), 'paren mismatch'
assert js.count('{') == js.count('}'), 'brace mismatch'
assert '</script' not in js.lower(), 'must not contain a script-closing tag'
assert 'closeAnnotationUI' in js
print('balance + embed-safety checks pass;', len(js.splitlines()), 'lines')
EOF
```
Expected: `balance + embed-safety checks pass; ...`. (The `</script` check matters: the
asset is embedded inside a `<script>` block, where that byte sequence would truncate it.)

- [ ] **Step 3: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-gloss/assets/annotations.js
git commit -m "feat(paper-gloss): annotation runtime — anchoring, marks, panel, export/import"
```

---

## Stage 4 — Skill prose and doc sync

### Task 4: Amend `skills/paper-gloss/SKILL.md`

**Files:**
- Modify: `skills/paper-gloss/SKILL.md`
- Modify: `docs/command-skill-reference.md` (line ~118, the paper-gloss row)
- Modify: `docs/usage-playbook.md` (line ~697, the paper-gloss card)

All in ONE commit — the frontmatter description changes, which fires the doc-sync rule,
and `scripts/check-doc-sync.py` runs as the tracked pre-push hook.

- [ ] **Step 1: Parse `$ARGUMENTS` — add the annotate mode trigger**

After the `--retrofit` bullet, add:

```markdown
- **`--annotate <glossed.html> [artifact-url]`** → skip Phases 1–2 and run
  ANNOTATE mode (below): inject the annotation layer into an already-published
  page and redeploy it to the same Artifact URL.
```

- [ ] **Step 2: Phase 2 — add the annotation-layer step**

Add a subsection at the end of Phase 2 (after "Self-containment & theming"):

````markdown
### Annotation layer

After authoring the page, run the injector — never hand-copy the runtime:

```bash
python3 scripts/inject_annotations.py <file.html> --slug <slug>
```

It stamps `data-pg-block="pg-p-NNNN"` on every `<p>`, `<li>`, `<dd>`, and
heading (existing `id`s are never touched or reused), sets `data-pg-slug` on
`<body>`, and embeds `assets/annotations.css` + `assets/annotations.js` as
sentinel-guarded blocks. The layer gives the reader select-to-highlight,
per-highlight notes, a fixed **✏️ Notes (N)** panel (below the Glossary
toggle), export to Markdown/JSON, and JSON import. Everything persists in
`localStorage` under `pg-annotations:<slug>`.

**Contract points** (extends the one-surface-at-a-time rule):
- The module assigns `window.closeAnnotationUI` and, when any of its surfaces
  open, closes the others: it calls whichever hooks the page exports
  (`window.closeGlossSurfaces` / `window.closeGlossPopover` /
  `window.closeGlossPanel` / `window.closeFigureLightbox`, each guarded) and
  falls back to hiding `#gloss-popover` / `#gloss-panel` / `#gloss-backdrop` /
  `#figure-lightbox` by id on pages that predate the hooks.
- It closes itself via its own delegated listener when a `.gloss-term`,
  `#gloss-panel-toggle`, or `.paper-figure img` click opens another surface —
  so pages whose gloss/lightbox code predates annotations still obey the rule
  with no edits to that code.
- Marks (`mark.pg-hl`) wrap text-node segments only, never element tags, and
  are never injected inside `.math`, `<math>`, or `pre.equation` — the same
  never-wrap discipline as term-wrapping.
````

- [ ] **Step 3: Phase 3 — add verification bullets**

Add to the Phase 3 checklist:

```markdown
- **Annotation layer present and idempotent:**
  `python3 scripts/inject_annotations.py --check <file.html>` exits clean, and
  a second injector run leaves the file byte-identical (`md5` before == after).
- **Annotation layer is inert to every check above:** block-marker stamping
  and the two sentinel blocks add zero `<p>` elements, zero `.gloss-term`
  buttons, and no external loads — if any earlier bullet moved after
  injection, the injector touched something it must not.
```

- [ ] **Step 4: Phase 4 — capabilities on the publish call, and the exception sentence**

In the "Publish via the `Artifact` tool" list, add after `file_path`:

```markdown
  - `capabilities: {downloads: true}` — the annotation layer's export buttons
    call `window.claude.downloads.save()`; without the declaration they fall
    back to copy-to-clipboard even on claude.ai.
```

**In the same list, rewrite the brand-new-artifact bullet** — as written it
denies ANNOTATE mode's existence and would instruct an `--annotate` run to
mint a fresh artifact and orphan the published link. Change its closing
sentence from:

> The single exception is RETROFIT mode below, which exists precisely to
> update a page in place.

to:

> The exceptions are RETROFIT and ANNOTATE modes below, both of which exist
> precisely to update a page in place.

- [ ] **Step 5: Add the ANNOTATE mode section**

Insert after the RETROFIT mode section, before "Definition of done":

```markdown
---

## ANNOTATE mode — add the annotation layer to an already-published page

For a glossed page that shipped before the annotation layer existed. Like
RETROFIT, it never re-reads the source paper and never re-runs Phase 1 — it
injects the layer and nothing else.

**Trigger:** `--annotate <glossed.html> [artifact-url]`, or Kyle asking to add
highlights/notes to an existing paper page.

1. **Baseline before touching anything:** record the `<p>` count and the
   `.gloss-term` tally per `data-term-id` (same counters as RETROFIT step 1).
2. **Inject:** `python3 scripts/inject_annotations.py <file.html>` (slug
   derives from the filename; pass `--slug` only to override). Re-running is
   safe — the sentinel blocks are replaced, not duplicated.
3. **Verify:** `--check` exits clean; second run byte-identical; `<p>` count
   **exactly unchanged**; `.gloss-term` per-id tally **exactly unchanged**
   (annotate touches no prose and no math — unlike RETROFIT there is no
   legitimate decrease); then the output-only Phase 3 bullets: *Well-formedness*,
   *Self-containment*, *Theming completeness* (the layer defines its own
   `--pg-annot-*` variables in all four theme blocks), *Math rendered*,
   *Artifact prerequisites*. The input-comparative bullets stay out of scope,
   same as RETROFIT.
4. **Republish in place:** `Artifact(url=<existing-url>, file_path=…,
   capabilities: {downloads: true})`. The capabilities argument is **not
   optional here**: these artifacts have no stored declaration, and omitting
   the field keeps none. Keeping the URL keeps the origin, which is what makes
   any annotations a reader has already stored survive the redeploy. Without a
   URL, ask rather than minting a new artifact and orphaning the old link.
5. **Git:** normal workflow in the page's own repo — branch, commit, push, PR,
   merge, brief Kyle.
6. **Report:** block markers stamped; baseline counters unchanged (state both numbers);
   Artifact URL redeployed to; storage key (`pg-annotations:<slug>`); and the
   reminder that local-file and artifact annotations are separate origins,
   bridged only by export/import.
```

- [ ] **Step 6: Update the frontmatter description**

In the `description:` line, after the sentence ending "…and a published claude.ai
Artifact link.", insert:

```
Every page carries an annotation layer — select text to highlight it, attach notes, and export to Obsidian-ready Markdown or re-importable JSON (localStorage-persistent per browser; export is the durability guarantee). An `--annotate` mode injects the layer into an already-published page and redeploys it to the same Artifact URL.
```

- [ ] **Step 7: Update the reference row and playbook card (same commit)**

`docs/command-skill-reference.md`, paper-gloss row: after "Delivers a `-glossed.html`
file and a published claude.ai Artifact link." insert:

```
Pages carry a highlight-and-note annotation layer with Markdown/JSON export.
```

and change the closing sentence to:

```
Run after `/paper-eli5`; `--retrofit` repairs math and `--annotate` adds the annotation layer to an already-published page at its existing URL.
```

`docs/usage-playbook.md`, paper-gloss card **Notes** bullet — append:

```
Highlights and notes persist per browser via localStorage; export to
Markdown/JSON is the durability guarantee (a fresh publish starts empty — only
`--retrofit`/`--annotate` redeploys keep stored notes). `--annotate` retrofits
the layer onto an existing page.
```

- [ ] **Step 8: Verify doc sync and commit**

```bash
cd /Users/kyledisch/Projects/claude-config
python3 scripts/check-doc-sync.py
git add skills/paper-gloss/SKILL.md docs/command-skill-reference.md docs/usage-playbook.md
git commit -m "feat(paper-gloss): annotation layer — Phase 2 injection, ANNOTATE mode, doc sync"
```
Expected: check exits clean before the commit.

### Task 5: Contract note in `skills/paper-figures/SKILL.md`

**Files:**
- Modify: `skills/paper-figures/SKILL.md` (Phase 6, the lightbox paragraph ending "…all converge on one close function.")

- [ ] **Step 1: Append two sentences to that paragraph**

```markdown
Pages carrying the paper-gloss annotation layer coordinate themselves: the
annotation module closes its own surfaces when a figure is clicked (via its
delegated listener) and exposes `window.closeAnnotationUI` for any future
surface that wants to close it explicitly — the lightbox needs no change.
```

- [ ] **Step 2: Commit** (description untouched → no doc-sync edit fires)

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/SKILL.md
git commit -m "docs(paper-figures): note the annotation layer's self-coordination contract"
```

---

## Stage 5 — Functional validation (local, Playwright)

### Task 6: Prove the runtime on the real jacobian-lens page

The jacobian-lens page is the hardest case: 592 `<p>`, 87 `<li>`, 43 `<dd>`, real gloss
terms, real figures with a lightbox. Everything runs on a **copy** — the real file is
touched in Stage 6.

- [ ] **Step 1: Inject into a copy and serve it**

```bash
mkdir -p /tmp/annot-test
cp /Users/kyledisch/Projects/jacobian-lens/verbalizable-representations-global-workspace-language-models-eli5-glossed.html /tmp/annot-test/index.html
cd /Users/kyledisch/Projects/claude-config/skills/paper-gloss/scripts
python3 inject_annotations.py /tmp/annot-test/index.html
python3 inject_annotations.py --check /tmp/annot-test/index.html
md5 /tmp/annot-test/index.html > /tmp/annot-test/md5.1
python3 inject_annotations.py /tmp/annot-test/index.html
md5 /tmp/annot-test/index.html > /tmp/annot-test/md5.2
diff /tmp/annot-test/md5.1 /tmp/annot-test/md5.2 && echo IDEMPOTENT
cd /tmp/annot-test && python3 -m http.server 8931 &
```
Expected: `--check` prints `clean`; `IDEMPOTENT` prints (localStorage needs http, not
`file://`, for reliable behavior — hence the server).

- [ ] **Step 2: Load and check for console errors**

Playwright MCP: `browser_navigate` to `http://localhost:8931/index.html`, then
`browser_console_messages`.
Expected: zero errors; `document.querySelectorAll('[data-pg-block]').length` (via
`browser_evaluate`) = **801** (592 p + 87 li + 43 dd + 79 headings — measured on the real
page; a lower number means blocks were skipped, which is exactly the F2 defect class);
the ✏️ Notes (0) toggle visible top-right without overlapping the 📖 Glossary toggle
(screenshot).

- [ ] **Step 3: Highlight → persist across reload**

`browser_evaluate`:

```js
() => {
  const p = document.querySelector('p[data-pg-block]');
  const textNode = [...p.childNodes].find(n => n.nodeType === 3 && n.nodeValue.trim().length > 20);
  const r = document.createRange();
  r.setStart(textNode, 1); r.setEnd(textNode, 15);
  const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
  document.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
  return new Promise(res => setTimeout(() => {
    const tb = document.querySelector('.pg-annot-toolbar');
    const visible = tb && !tb.hidden;
    if (visible) tb.querySelector('[data-act="hl"]').click();
    res({toolbarVisible: visible, marks: document.querySelectorAll('mark.pg-hl').length,
         stored: !!localStorage.getItem('pg-annotations:' + document.body.dataset.pgSlug)});
  }, 50));
}
```
Expected: `{toolbarVisible: true, marks: 1, stored: true}`. Then `browser_navigate` (reload)
and evaluate `document.querySelectorAll('mark.pg-hl').length` → `1` (re-anchored from
storage), badge reads `✏️ Notes (1)`.

- [ ] **Step 4: Note flow + panel**

Click the mark (`browser_evaluate`: `document.querySelector('mark.pg-hl').click()`) →
editor visible; set the textarea value to `test note`, click `[data-act="save"]` → mark
gains class `pg-hl--noted`. Open the panel via the toggle → list shows 1 item with quote,
note, and Jump/Edit/Delete.

- [ ] **Step 5: Export fallback + import round-trip**

No `window.claude` exists on localhost, so **Export Markdown** must open the fallback
dialog; assert its textarea starts with `---`, contains `tags: [paper-annotations]`,
contains `> ` followed by the highlighted text, **and contains a `## <section>` line
naming the actual section heading the highlight sits under — not the paper title** (this
is the assertion that catches the heading-exclusion / section-collapse defect class).
**Export JSON** likewise; save that JSON text to `/tmp/annot-test/export.json` (via
evaluate return). Then Delete the annotation (panel), assert marks = 0 and badge (0);
Import via `browser_file_upload` with `/tmp/annot-test/export.json` → marks = 1 again,
status line says `Imported 1`.

- [ ] **Step 6: Surface coordination matrix**

Each row asserted via `browser_evaluate`:

Drive every row with `browser_evaluate` `.click()` calls — programmatic clicks bypass
overlay hit-testing, which is the point: rows test the coordination logic, not z-order.

| Action | Expected |
|---|---|
| Open annotation panel, then click a `.gloss-term` | annotation panel hidden, `#gloss-popover` not hidden |
| Open gloss glossary panel (`#gloss-panel-toggle`), then open the annotation panel via its toggle | `#gloss-panel` hidden — via `closeGlossSurfaces` on this page; the DOM fallback covers the five pages exporting no hooks — annotation panel visible |
| Open the note editor (click a mark), while `#gloss-popover` is open | popover hidden (hook or DOM fallback), editor visible |
| Open the note editor, then click a `.paper-figure img` | editor hidden, `#figure-lightbox` not hidden |
| With editor open, press Escape | editor hidden |
| Highlight text crossing a `.gloss-term` boundary | button still present in DOM, `mark.pg-hl` count ≥ 2 (segments), clicking the button still opens the popover |

- [ ] **Step 7: Never-mark-math**

Select a range that includes an inline `.math` span (build the Range around a paragraph
known to contain one), highlight, then assert:
`document.querySelectorAll('.math mark, math mark, pre.equation mark').length === 0`
while the annotation still stores and re-anchors after reload.

- [ ] **Step 8: Dark theme screenshot**

`browser_evaluate`: `document.documentElement.setAttribute('data-theme','dark')`, screenshot,
confirm marks/panel/toolbar legible; repeat with `'light'`. Kill the http server.

- [ ] **Step 9: Commit any fixes this stage forced**

```bash
cd /Users/kyledisch/Projects/claude-config
git add -A skills/paper-gloss
git commit -m "fix(paper-gloss): annotation runtime fixes from functional validation"
```
(Skip the commit if validation passed with zero changes.)

---

## Stage 6 — First real retrofit: jacobian-lens

### Task 7: `--annotate` the jacobian-lens page and republish in place

Follow the ANNOTATE mode section exactly as written in Task 4 — this run is its
acceptance test.

- [ ] **Step 1: Baseline** — `<p>` count (expect 592) and per-`data-term-id` tally on the real file.
- [ ] **Step 2: Inject + verify** — injector, `--check`, idempotency md5, baselines unchanged.
- [ ] **Step 3: Find the artifact URL** — `Artifact(action:"list")`, match by title
  ("Verbalizable Representations Form a Global Workspace in Language Models"). If no
  confident match: stop, deliver the file, ask Kyle. Never publish fresh.
- [ ] **Step 4: Republish** — `Artifact(url=<existing>, file_path=…, capabilities: {downloads: true})`,
  same title and favicon.
- [ ] **Step 5: Verify on the published artifact** (claude-in-chrome or Playwright on the
  live URL): highlight → reload → persists (this is the localStorage-on-artifact-origin
  proof on a real page); Export Markdown → the downloads confirmation prompt appears
  (accepting it is the viewer's choice — the prompt appearing is the pass condition).
- [ ] **Step 6: Git in the jacobian-lens repo** — branch `feat/annotation-layer`, commit the
  HTML, push, PR, merge per the global workflow, brief Kyle with the artifact URL and
  storage key.

---

## Stage 7 — Batch retrofit: the remaining 5 pages

### Task 8: Repeat Task 7 for pages 2–6 of the D6 table

For each of ghost-patch, forge-gap, lossy-wall, dim-stage (`docs/paper/` — singular),
decay-pin:

- [ ] **Step 1:** Baseline → inject → `--check` → idempotency → baselines unchanged.
- [ ] **Step 2:** Match the artifact URL by title from `Artifact(action:"list")`; ambiguous
  match → deliver the file, flag Kyle, skip the republish for that page.
- [ ] **Step 3:** Republish in place with `capabilities: {downloads: true}`.
- [ ] **Step 4:** Spot-check the live page (badge renders, one highlight persists a reload).
- [ ] **Step 5:** Branch/commit/PR/merge in that page's own repo; one-line brief per page.
- [ ] **Step 6:** Final report: 6-row table — page, block markers stamped, artifact URL, verified-live
  yes/no, flags.

---

## Follow-ups (explicitly NOT this plan)

- **Cross-device sync / shared annotations:** impossible today — `downloads` and `mcp` are
  the only artifact capabilities; no storage/state capability exists. Not deferred; off
  the table until the platform changes.
- **Direct-to-Obsidian push via the `mcp` capability** (e.g. a basic-memory connector
  writing straight into the vault): plausible follow-up, needs its own design pass and a
  viewer-consent story; export/import is the v1 bridge.
- **Cross-paragraph highlights**, **multi-color highlights**: cut from v1 by scope
  discipline; both are additive later.
- **Best-score `locate()` across blocks** (adversarial-review F9): today `locate()`
  returns the first block containing the quote; scoring across all candidate blocks (and
  orphaning on a zero context score) would make re-anchoring of short common phrases
  robust to pid drift. No live path today — pids only drift on regeneration, which mints
  a new origin and empty storage anyway.
- **Annotating the eli5 markdown**: different medium, different feature.

---

## Run-config note

Recommended: **Opus 5 · `high`** — well-specified build with real judgment in the runtime
edge cases (anchoring, selection, surface coordination); the plan carries complete code so
Fable-level design work is already done.

```
cd ~/Projects/claude-config && claude --model claude-opus-5 --effort high
```

First prompt: point the session at `docs/plans/2026-07-28-paper-gloss-annotations.md` and
execute task-by-task per the header note.
