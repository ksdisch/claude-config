# paper-figures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/paper-figures` skill that harvests real figure images from a paper's original source and injects them into an existing `-eli5.md` and `-eli5-glossed.html`, replacing `[Figure N]` placeholders — validated end-to-end against the 94-figure jacobian-lens paper.

**Architecture:** Deterministic work (parsing, classification, resizing, base64, checking) lives in small stdlib-only Python scripts under `skills/paper-figures/scripts/`, each with unit tests. `SKILL.md` is thin orchestration prose that calls those scripts and handles the judgement calls (crop correction, visual review, the approval gate). Scripts are the unit of testing; the skill is the unit of orchestration.

**Tech Stack:** Python 3 stdlib only (`re`, `json`, `zlib`, `struct`, `base64`, `hashlib`, `urllib`, `unittest`), macOS `sips` for resampling, poppler for PDF, Playwright MCP for browser capture. No pip installs, no external dependencies.

**Scope of THIS plan:** the **web** source backend only. The skill ships with PDF sources explicitly unsupported (it reports and stops). The PDF backend gets its own follow-up plan — the spec's Phase 2 PDF section and the verified `pdftoppm` crop mechanics carry over to it unchanged.

**Spec:** `docs/superpowers/specs/2026-07-27-paper-figures-design.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `skills/paper-figures/SKILL.md` | Orchestration prose: phases, gates, judgement calls, reporting |
| `skills/paper-figures/references/capture-recipes.md` | Exact shell/Playwright invocations, loaded on demand |
| `skills/paper-figures/scripts/ledger.py` | Parse `-eli5.md` → figure ledger JSON |
| `skills/paper-figures/scripts/webfigs.py` | Parse source page HTML → figure manifest (static vs interactive) |
| `skills/paper-figures/scripts/checks.py` | Tier 1 programmatic capture checks |
| `skills/paper-figures/scripts/normalize.py` | Adaptive per-figure budget + `sips` resampling |
| `skills/paper-figures/scripts/inject.py` | Markdown and HTML injection |
| `skills/paper-figures/scripts/contactsheet.py` | Build the review contact sheet |
| `skills/paper-figures/scripts/tests/test_*.py` | Unit tests, run via `python3 -m unittest` |

Each script is independently runnable as a CLI (`python3 ledger.py <args>`) and importable for tests. No script imports another — they communicate through JSON files on disk, so any stage can be re-run in isolation.

**Modified:** `skills/paper-gloss/SKILL.md`, `skills/paper-eli5/SKILL.md`, `docs/command-skill-reference.md`.

**Branch:** `feat/paper-figures` (already exists, spec committed at `37ed94c`).

---

## Stage 0 — Scaffolding

### Task 0: Create the skill directory and test runner

**Files:**
- Create: `skills/paper-figures/scripts/tests/__init__.py` (empty)

- [ ] **Step 1: Create directories**

```bash
cd /Users/kyledisch/Projects/claude-config
mkdir -p skills/paper-figures/scripts/tests skills/paper-figures/references
touch skills/paper-figures/scripts/tests/__init__.py
```

- [ ] **Step 2: Verify the test runner works on an empty suite**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: `Ran 0 tests in 0.000s` followed by `OK`

- [ ] **Step 3: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures
git commit -m "chore(paper-figures): scaffold skill directory and test suite"
```

---

## Stage 1 — Figure ledger

The ledger is the contract: one entry per figure slot in the eli5 markdown. Every later stage keys off `num`.

### Task 1: Parse figure slots out of an eli5 markdown file

**Files:**
- Create: `skills/paper-figures/scripts/ledger.py`
- Test: `skills/paper-figures/scripts/tests/test_ledger.py`

- [ ] **Step 1: Write the failing test**

Create `skills/paper-figures/scripts/tests/test_ledger.py`:

```python
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ledger import build_ledger  # noqa: E402

PLAIN = """\
Some prose paragraph.

[Figure 1]

Figure 1: Five functional properties of a global workspace.

More prose.
"""

WITH_IMAGE = """\
![Figure 4](https://example.com/png/img_abc.png)

Figure 4: The Jacobian lens.
"""


class TestBuildLedger(unittest.TestCase):
    def test_plain_placeholder(self):
        entries = build_ledger(PLAIN)
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e["num"], 1)
        self.assertIsNone(e["existing_url"])
        self.assertEqual(
            e["caption"], "Five functional properties of a global workspace."
        )

    def test_image_placeholder_keeps_url(self):
        entries = build_ledger(WITH_IMAGE)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["num"], 4)
        self.assertEqual(
            entries[0]["existing_url"], "https://example.com/png/img_abc.png"
        )
        self.assertEqual(entries[0]["caption"], "The Jacobian lens.")

    def test_line_index_points_at_placeholder(self):
        entries = build_ledger(PLAIN)
        self.assertEqual(PLAIN.split("\n")[entries[0]["line"]], "[Figure 1]")

    def test_inline_figure_reference_is_not_a_slot(self):
        # "(Figure 5)" inside prose must not create a ledger entry
        entries = build_ledger("We show this in prose (Figure 5) here.\n")
        self.assertEqual(entries, [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ledger'`

- [ ] **Step 3: Write the implementation**

Create `skills/paper-figures/scripts/ledger.py`:

```python
#!/usr/bin/env python3
"""Extract figure slots from a paper-eli5 markdown file into a JSON ledger.

Usage:
    python3 ledger.py <path-to-eli5.md> [-o ledger.json]

A figure slot is a line that is *only* a figure placeholder, in one of:
    [Figure 7]
    ![Figure 4](https://example.com/img.png)

An inline mention such as "(Figure 5)" inside a sentence is not a slot.
"""
import argparse
import json
import re
import sys

PLACEHOLDER = re.compile(
    r"^(?P<img>!)?\[Figure\s+(?P<num>\d+)\](?:\((?P<url>[^)]*)\))?$"
)
CAPTION = re.compile(r"^Figure\s+(?P<num>\d+):\s*(?P<text>.+)$")


def build_ledger(text):
    """Return a list of figure-slot dicts, in document order."""
    lines = text.split("\n")

    captions = {}
    for line in lines:
        m = CAPTION.match(line.strip())
        if m:
            captions.setdefault(int(m.group("num")), m.group("text").strip())

    entries = []
    for i, line in enumerate(lines):
        m = PLACEHOLDER.match(line.strip())
        if not m:
            continue
        num = int(m.group("num"))
        entries.append(
            {
                "num": num,
                "line": i,
                "raw": line,
                "existing_url": m.group("url") or None,
                "caption": captions.get(num, ""),
                "status": "pending",
            }
        )
    return entries


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("markdown")
    ap.add_argument("-o", "--out", default="-")
    args = ap.parse_args(argv)

    with open(args.markdown, encoding="utf-8") as fh:
        entries = build_ledger(fh.read())

    payload = json.dumps({"figures": entries}, indent=2, ensure_ascii=False)
    if args.out == "-":
        print(payload)
    else:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(payload + "\n")
    print(f"{len(entries)} figure slots", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: `Ran 4 tests` … `OK`

- [ ] **Step 5: Verify against the real 94-figure paper**

Run:
```bash
cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts
python3 ledger.py \
  /Users/kyledisch/Projects/jacobian-lens/verbalizable-representations-global-workspace-language-models-eli5.md \
  -o /tmp/ledger.json
python3 -c "
import json
d = json.load(open('/tmp/ledger.json'))['figures']
print(len(d), 'slots')
print('nums ok:', [f['num'] for f in d] == list(range(1, 95)))
print('with url:', sorted(f['num'] for f in d if f['existing_url']))
"
```
Expected:
```
94 figure slots
94 slots
nums ok: True
with url: [4, 47, 52, 53, 54, 57, 58, 59, 60, 73]
```

This is the real acceptance check — 94 slots numbered 1..94 with no gaps, and exactly those 10 already carrying a URL. Those 10 numbers are the same set that the live page marks up as static `<img>` figures (verified while writing the spec), so a mismatch here means the ledger parser is wrong.

**Consequence worth noting:** because paper-eli5 already preserved all 10 static URLs in the markdown, the static path never needs to re-discover them from the page — `webfigs.py` is only strictly required for the 84 interactive figures and as a cross-check on the 10.

- [ ] **Step 6: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/scripts/ledger.py skills/paper-figures/scripts/tests/test_ledger.py
git commit -m "feat(paper-figures): parse eli5 markdown into a figure ledger"
```

---

## Stage 2 — Web figure manifest

### Task 2: Enumerate and classify figures on the source page

**Files:**
- Create: `skills/paper-figures/scripts/webfigs.py`
- Test: `skills/paper-figures/scripts/tests/test_webfigs.py`

- [ ] **Step 1: Write the failing test**

Create `skills/paper-figures/scripts/tests/test_webfigs.py`:

```python
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfigs import build_manifest  # noqa: E402

PAGE = """\
<p>prose</p>
<figure data-fignum="1" id="fig-props" class='wide'><div class='intro-functional'></div>
<figcaption><span class="fig-num">Figure 1: </span>Five functional properties.</figcaption></figure>
<p>more prose</p>
<figure data-fignum="4" id="fig-jlens"><img src="./png/img_abc.png" alt="">
<figcaption><span class="fig-num">Figure 4: </span>The Jacobian lens.</figcaption></figure>
"""

BASE = "https://transformer-circuits.pub/2026/workspace/index.html"


class TestBuildManifest(unittest.TestCase):
    def setUp(self):
        self.figs = {f["num"]: f for f in build_manifest(PAGE, BASE)}

    def test_finds_every_figure(self):
        self.assertEqual(sorted(self.figs), [1, 4])

    def test_classifies_interactive(self):
        self.assertEqual(self.figs[1]["kind"], "interactive")
        self.assertIsNone(self.figs[1]["img_url"])

    def test_classifies_static_and_resolves_relative_url(self):
        self.assertEqual(self.figs[4]["kind"], "static")
        self.assertEqual(
            self.figs[4]["img_url"],
            "https://transformer-circuits.pub/2026/workspace/png/img_abc.png",
        )

    def test_selector_is_attribute_based(self):
        self.assertEqual(self.figs[1]["selector"], 'figure[data-fignum="1"]')

    def test_extracts_caption_without_the_fig_num_prefix(self):
        self.assertEqual(self.figs[1]["caption"], "Five functional properties.")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'webfigs'`

- [ ] **Step 3: Write the implementation**

Create `skills/paper-figures/scripts/webfigs.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: `Ran 9 tests` … `OK`

- [ ] **Step 5: Verify against the real page**

Run:
```bash
cd /tmp && curl -sL --max-time 60 "https://transformer-circuits.pub/2026/workspace/index.html" -o tcpub.html
cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts
python3 webfigs.py /tmp/tcpub.html "https://transformer-circuits.pub/2026/workspace/index.html" -o /tmp/manifest.json
python3 -c "import json;f=json.load(open('/tmp/manifest.json'))['figures'];s=[x['num'] for x in f if x['kind']=='static'];print(len(f),'figures');print('static:',s)"
```
Expected:
```
94 figures: 10 static, 84 interactive
94 figures
static: [4, 47, 52, 53, 54, 57, 58, 59, 60, 73]
```

Those exact 10 static figure numbers are the acceptance check — they were measured from the live page while writing the spec.

- [ ] **Step 6: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/scripts/webfigs.py skills/paper-figures/scripts/tests/test_webfigs.py
git commit -m "feat(paper-figures): enumerate and classify web figures by data-fignum"
```

---

## Stage 3 — Tier 1 capture checks

Calibration measured while writing the spec: a blank 900×600 PNG is **0.0046 bytes/px**; a real (sparse, text-heavy) content crop is **0.027 bytes/px**. Data visualizations sit well above the sparse-text case, so `0.010` cleanly separates blank from real, and `0.010–0.020` is a grey zone that escalates to visual review rather than being auto-rejected.

### Task 3: Detect unrendered, degenerate, and duplicate captures

**Files:**
- Create: `skills/paper-figures/scripts/checks.py`
- Test: `skills/paper-figures/scripts/tests/test_checks.py`

- [ ] **Step 1: Write the failing test**

Create `skills/paper-figures/scripts/tests/test_checks.py`:

```python
import os
import struct
import sys
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from checks import check_capture, png_dimensions  # noqa: E402


def write_png(path, w, h, rgb, noise=False):
    rows = []
    for y in range(h):
        if noise:
            px = b"".join(
                bytes(((x * 7 + y * 13) % 256, (x * 3) % 256, (y * 5) % 256))
                for x in range(w)
            )
        else:
            px = bytes(rgb) * w
        rows.append(b"\x00" + px)
    raw = b"".join(rows)

    def chunk(tag, data):
        body = tag + data
        return (
            struct.pack(">I", len(data))
            + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
        )

    blob = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    with open(path, "wb") as fh:
        fh.write(blob)
    return path


class TestChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.join(os.path.dirname(__file__), "_tmp")
        os.makedirs(self.tmp, exist_ok=True)

    def tearDown(self):
        for f in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, f))
        os.rmdir(self.tmp)

    def test_png_dimensions(self):
        p = write_png(os.path.join(self.tmp, "a.png"), 900, 600, (255, 255, 255))
        self.assertEqual(png_dimensions(p), (900, 600))

    def test_blank_image_fails(self):
        p = write_png(os.path.join(self.tmp, "blank.png"), 900, 600, (255, 255, 255))
        r = check_capture(p)
        self.assertEqual(r["verdict"], "fail")
        self.assertIn("blank", r["reason"])

    def test_dense_image_passes(self):
        p = write_png(os.path.join(self.tmp, "real.png"), 300, 200, None, noise=True)
        r = check_capture(p)
        self.assertEqual(r["verdict"], "pass")

    def test_degenerate_dimensions_fail(self):
        p = write_png(os.path.join(self.tmp, "thin.png"), 2, 600, (10, 20, 30))
        r = check_capture(p)
        self.assertEqual(r["verdict"], "fail")

    def test_duplicate_hashes_are_reported(self):
        from checks import find_duplicates

        a = write_png(os.path.join(self.tmp, "x.png"), 60, 40, (1, 2, 3))
        b = write_png(os.path.join(self.tmp, "y.png"), 60, 40, (1, 2, 3))
        c = write_png(os.path.join(self.tmp, "z.png"), 60, 40, (9, 9, 9))
        dupes = find_duplicates([a, b, c])
        self.assertEqual(len(dupes), 1)
        self.assertEqual(sorted(os.path.basename(p) for p in dupes[0]), ["x.png", "y.png"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'checks'`

- [ ] **Step 3: Write the implementation**

Create `skills/paper-figures/scripts/checks.py`:

```python
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
    """Classify one capture as pass / review / fail."""
    size = os.path.getsize(path)
    width, height = png_dimensions(path)
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
    """Return groups of paths whose bytes are identical (wrong-element capture)."""
    by_hash = defaultdict(list)
    for p in paths:
        with open(p, "rb") as fh:
            by_hash[hashlib.sha256(fh.read()).hexdigest()].append(p)
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
                if r["path"] == p:
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: `Ran 14 tests` … `OK`

- [ ] **Step 5: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/scripts/checks.py skills/paper-figures/scripts/tests/test_checks.py
git commit -m "feat(paper-figures): add tier-1 capture checks with calibrated blank detection"
```

---

## Stage 4 — Adaptive normalization

### Task 4: Compute the per-figure budget and resample to fit

**Files:**
- Create: `skills/paper-figures/scripts/normalize.py`
- Test: `skills/paper-figures/scripts/tests/test_normalize.py`

- [ ] **Step 1: Write the failing test**

Create `skills/paper-figures/scripts/tests/test_normalize.py`:

```python
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from normalize import per_figure_budget, plan_width  # noqa: E402


class TestBudget(unittest.TestCase):
    def test_many_figures_get_a_small_share(self):
        # 94 figures against a 6MB total -> ~64KB each
        b = per_figure_budget(94)
        self.assertGreater(b, 60_000)
        self.assertLess(b, 70_000)

    def test_few_figures_are_capped_not_inflated(self):
        # 8 figures would compute to 750KB; the per-figure cap holds it down
        self.assertEqual(per_figure_budget(8), 250_000)

    def test_single_figure_still_capped(self):
        self.assertEqual(per_figure_budget(1), 250_000)

    def test_zero_figures_does_not_divide_by_zero(self):
        self.assertEqual(per_figure_budget(0), 250_000)


class TestPlanWidth(unittest.TestCase):
    def test_never_upscales_beyond_source_width(self):
        self.assertEqual(plan_width(source_width=700, budget_bytes=250_000), 700)

    def test_wide_source_capped_at_max(self):
        self.assertEqual(plan_width(source_width=4000, budget_bytes=250_000), 1400)

    def test_small_budget_forces_a_narrower_width(self):
        w = plan_width(source_width=4000, budget_bytes=64_000)
        self.assertLessEqual(w, 1000)
        self.assertGreaterEqual(w, 600)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'normalize'`

- [ ] **Step 3: Write the implementation**

Create `skills/paper-figures/scripts/normalize.py`:

```python
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
import shutil
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
    return max(MIN_WIDTH, min(target, MIN_WIDTH))


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


def resample(src, dst, width, fmt, quality=None):
    cmd = ["sips", "--resampleWidth", str(width), "-s", "format", fmt]
    if fmt == "jpeg" and quality:
        cmd += ["-s", "formatOptions", str(quality)]
    cmd += [src, "--out", dst]
    subprocess.run(cmd, capture_output=True, check=True)
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: `Ran 21 tests` … `OK`

- [ ] **Step 5: Verify `sips` round-trips a real image**

Run:
```bash
cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts
mkdir -p /tmp/nsrc /tmp/ndst && cp /tmp/croptest-03.png /tmp/nsrc/fig-01.png
python3 normalize.py /tmp/nsrc /tmp/ndst --count 94 2>&1 | tail -20
ls -la /tmp/ndst/
```
Expected: a `fig-01.png` or `fig-01.jpg` in `/tmp/ndst/`, `budget 64,...  B/figure across 94 figures` on stderr, and the emitted JSON showing `over_budget: false`.

- [ ] **Step 6: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/scripts/normalize.py skills/paper-figures/scripts/tests/test_normalize.py
git commit -m "feat(paper-figures): adaptive per-figure size budget with sips resampling"
```

---

## Stage 5 — Markdown injection

### Task 5: Replace placeholder lines with image references

**Files:**
- Create: `skills/paper-figures/scripts/inject.py`
- Test: `skills/paper-figures/scripts/tests/test_inject_md.py`

- [ ] **Step 1: Write the failing test**

Create `skills/paper-figures/scripts/tests/test_inject_md.py`:

```python
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inject import inject_markdown  # noqa: E402

DOC = """\
Intro paragraph.

[Figure 1]

Figure 1: Five functional properties.

Body text mentioning (Figure 1) inline.

[Figure 2]

Figure 2: Second figure.
"""


class TestInjectMarkdown(unittest.TestCase):
    def setUp(self):
        self.images = {1: "figures/paper/fig-01.png", 2: "figures/paper/fig-02.png"}
        self.out = inject_markdown(DOC, self.images)

    def test_placeholders_become_images(self):
        self.assertIn("![Figure 1](figures/paper/fig-01.png)", self.out)
        self.assertIn("![Figure 2](figures/paper/fig-02.png)", self.out)

    def test_bare_placeholders_are_gone(self):
        self.assertNotIn("\n[Figure 1]\n", self.out)
        self.assertNotIn("\n[Figure 2]\n", self.out)

    def test_captions_untouched(self):
        self.assertIn("Figure 1: Five functional properties.", self.out)
        self.assertIn("Figure 2: Second figure.", self.out)

    def test_inline_mentions_untouched(self):
        self.assertIn("Body text mentioning (Figure 1) inline.", self.out)

    def test_line_count_unchanged(self):
        self.assertEqual(len(DOC.split("\n")), len(self.out.split("\n")))

    def test_missing_image_leaves_placeholder(self):
        out = inject_markdown(DOC, {1: "figures/paper/fig-01.png"})
        self.assertIn("![Figure 1](figures/paper/fig-01.png)", out)
        self.assertIn("[Figure 2]", out)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'inject'`

- [ ] **Step 3: Write the implementation**

Create `skills/paper-figures/scripts/inject.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: `Ran 27 tests` … `OK`

- [ ] **Step 5: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/scripts/inject.py skills/paper-figures/scripts/tests/test_inject_md.py
git commit -m "feat(paper-figures): inject figure images into eli5 markdown"
```

---

## Stage 6 — HTML injection

The existing placeholder shape in a glossed file (measured from the real output) is:

```html
<div class="figure-placeholder">[Figure 1] — Figure 1: Five functional properties…</div>
```

Note the caption already carries its own `Figure N:` prefix after the `] — ` separator, so the injector must strip the `[Figure N] — ` lead-in rather than emit it twice. Some placeholders also carry a trailing `<span class="img-note">(image available at …)</span>`, which must be dropped once a real image is present.

### Task 6: Replace placeholder divs with base64 figures

**Files:**
- Create: `skills/paper-figures/scripts/inject_html.py`
- Test: `skills/paper-figures/scripts/tests/test_inject_html.py`

- [ ] **Step 1: Write the failing test**

Create `skills/paper-figures/scripts/tests/test_inject_html.py`:

```python
import base64
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inject_html import caption_of, data_uri, inject_html  # noqa: E402

DOC = """\
<html><head><style>:root { --fg: #111; }</style></head><body>
<p>prose</p>
<div class="figure-placeholder">[Figure 1] — Figure 1: Five functional properties.</div>
<div class="figure-placeholder">[Figure 4] — Figure 4: The Jacobian lens. <span class="img-note">(image available at https://example.com/a.png)</span></div>
</body></html>
"""


class TestCaption(unittest.TestCase):
    def test_strips_the_bracket_lead_in(self):
        self.assertEqual(
            caption_of("[Figure 1] — Figure 1: Five functional properties."),
            "Figure 1: Five functional properties.",
        )

    def test_drops_the_img_note_span(self):
        raw = '[Figure 4] — Figure 4: The lens. <span class="img-note">(image available at http://x/a.png)</span>'
        self.assertEqual(caption_of(raw), "Figure 4: The lens.")


class TestDataURI(unittest.TestCase):
    def test_png_mime(self):
        path = os.path.join(os.path.dirname(__file__), "_u.png")
        with open(path, "wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n" + b"0" * 40)
        try:
            uri = data_uri(path)
            self.assertTrue(uri.startswith("data:image/png;base64,"))
            self.assertIn(base64.b64encode(b"\x89PNG")[:6].decode(), uri)
        finally:
            os.remove(path)

    def test_jpeg_mime(self):
        path = os.path.join(os.path.dirname(__file__), "_u.jpg")
        with open(path, "wb") as fh:
            fh.write(b"\xff\xd8\xff" + b"0" * 40)
        try:
            self.assertTrue(data_uri(path).startswith("data:image/jpeg;base64,"))
        finally:
            os.remove(path)


class TestInjectHTML(unittest.TestCase):
    def setUp(self):
        d = os.path.dirname(__file__)
        self.p1 = os.path.join(d, "_f1.png")
        self.p4 = os.path.join(d, "_f4.png")
        for p in (self.p1, self.p4):
            with open(p, "wb") as fh:
                fh.write(b"\x89PNG\r\n\x1a\n" + os.path.basename(p).encode() * 5)
        self.out = inject_html(DOC, {1: self.p1, 4: self.p4})

    def tearDown(self):
        for p in (self.p1, self.p4):
            if os.path.exists(p):
                os.remove(p)

    def test_placeholders_replaced(self):
        self.assertNotIn("figure-placeholder", self.out)
        self.assertEqual(self.out.count('<figure class="paper-figure"'), 2)

    def test_images_are_data_uris(self):
        self.assertEqual(self.out.count('src="data:image/png;base64,'), 2)

    def test_no_external_sources_remain(self):
        self.assertNotIn('src="http', self.out)
        self.assertNotIn("img-note", self.out)

    def test_alt_text_is_the_caption(self):
        self.assertIn('alt="Figure 1: Five functional properties."', self.out)

    def test_figcaption_present(self):
        self.assertIn("<figcaption>Figure 1: Five functional properties.</figcaption>", self.out)

    def test_css_and_lightbox_injected_once(self):
        self.assertEqual(self.out.count(".paper-figure {"), 1)
        self.assertEqual(self.out.count('id="figure-lightbox"'), 1)

    def test_unmapped_figure_keeps_its_placeholder(self):
        out = inject_html(DOC, {1: self.p1})
        self.assertIn("[Figure 4]", out)
        self.assertEqual(out.count('<figure class="paper-figure"'), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'inject_html'`

- [ ] **Step 3: Write the implementation**

Create `skills/paper-figures/scripts/inject_html.py`:

```python
#!/usr/bin/env python3
"""Inject harvested figures into a paper-gloss HTML file as base64 data URIs.

Replaces each `.figure-placeholder` div with a real <figure>, and adds the
supporting CSS plus a singleton lightbox. Everything stays inline so the file
remains self-contained and publishable as an Artifact.
"""
import base64
import html as htmllib
import os
import re

PLACEHOLDER = re.compile(
    r'<div class="figure-placeholder">(?P<body>.*?)</div>', re.S
)
LEAD_IN = re.compile(r"^\s*\[Figure\s+(?P<num>\d+)\]\s*(?:—|--|-)\s*")
IMG_NOTE = re.compile(r'<span class="img-note">.*?</span>', re.S)
TAG = re.compile(r"<[^>]+>")

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}

CSS = """
    .paper-figure {
      margin: 2rem auto;
      padding: 0;
      text-align: center;
    }
    .paper-figure img {
      max-width: 100%;
      height: auto;
      border: 1px solid var(--figure-border, rgba(128,128,128,0.3));
      border-radius: 6px;
      background: var(--figure-bg, transparent);
      cursor: zoom-in;
    }
    .paper-figure figcaption {
      margin-top: 0.6rem;
      font-size: 0.88rem;
      line-height: 1.5;
      color: var(--muted, #666);
      text-align: left;
    }
    .figure-lightbox {
      position: fixed;
      inset: 0;
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--lightbox-bg, rgba(0,0,0,0.85));
      cursor: zoom-out;
    }
    .figure-lightbox[hidden] { display: none; }
    .figure-lightbox img {
      max-width: 95vw;
      max-height: 95vh;
      object-fit: contain;
    }
    .figure-lightbox-close {
      position: absolute;
      top: 1rem;
      right: 1rem;
      font-size: 1.6rem;
      line-height: 1;
      background: none;
      border: none;
      color: #fff;
      cursor: pointer;
    }
"""

LIGHTBOX_HTML = """
<div id="figure-lightbox" class="figure-lightbox" role="dialog" aria-modal="true" aria-label="Enlarged figure" hidden>
  <button class="figure-lightbox-close" aria-label="Close">&times;</button>
  <img alt="">
</div>
"""

LIGHTBOX_JS = """
<script>
(function () {
  var box = document.getElementById('figure-lightbox');
  if (!box) return;
  var img = box.querySelector('img');

  function close() {
    box.hidden = true;
    img.removeAttribute('src');
  }

  function open(source) {
    // Only one interactive surface at a time: close the gloss popover and panel.
    if (typeof window.closeGlossPopover === 'function') window.closeGlossPopover();
    if (typeof window.closeGlossPanel === 'function') window.closeGlossPanel();
    img.src = source.src;
    img.alt = source.alt || '';
    box.hidden = false;
  }

  document.addEventListener('click', function (e) {
    var figImg = e.target.closest('.paper-figure img');
    if (figImg) { open(figImg); return; }
    if (!box.hidden && (e.target === box || e.target.closest('.figure-lightbox-close'))) close();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !box.hidden) close();
  });

  window.closeFigureLightbox = close;
})();
</script>
"""


def caption_of(body):
    """Strip the '[Figure N] — ' lead-in and any img-note span."""
    text = IMG_NOTE.sub("", body)
    text = LEAD_IN.sub("", text)
    text = TAG.sub("", text)
    return htmllib.unescape(text).strip()


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = MIME.get(ext, "application/octet-stream")
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode("ascii")


def inject_html(doc, images):
    """Replace placeholder divs with real figures; add CSS and the lightbox."""
    images = {int(k): v for k, v in images.items()}
    injected = 0

    def repl(m):
        nonlocal injected
        body = m.group("body")
        num_m = LEAD_IN.match(body)
        if not num_m:
            return m.group(0)
        num = int(num_m.group("num"))
        path = images.get(num)
        if not path or not os.path.exists(path):
            return m.group(0)
        caption = caption_of(body)
        esc = htmllib.escape(caption, quote=True)
        injected += 1
        return (
            f'<figure class="paper-figure" id="figure-{num}">'
            f'<img src="{data_uri(path)}" alt="{esc}" loading="lazy">'
            f"<figcaption>{htmllib.escape(caption)}</figcaption>"
            f"</figure>"
        )

    out = PLACEHOLDER.sub(repl, doc)
    if injected == 0:
        return out

    if ".paper-figure {" not in out:
        out = out.replace("</style>", CSS + "\n</style>", 1)
    if 'id="figure-lightbox"' not in out:
        out = out.replace("</body>", LIGHTBOX_HTML + LIGHTBOX_JS + "\n</body>", 1)
    return out
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: `Ran 38 tests` … `OK`

- [ ] **Step 5: Confirm the real glossed file's placeholders actually match**

Run:
```bash
cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts
python3 -c "
import re, sys
sys.path.insert(0, '.')
from inject_html import PLACEHOLDER, LEAD_IN, caption_of
doc = open('/Users/kyledisch/Projects/jacobian-lens/verbalizable-representations-global-workspace-language-models-eli5-glossed.html', encoding='utf-8').read()
hits = list(PLACEHOLDER.finditer(doc))
print('placeholder divs found:', len(hits))
matched = [m for m in hits if LEAD_IN.match(m.group('body'))]
print('with parseable [Figure N] lead-in:', len(matched))
print('sample caption:', caption_of(matched[0].group('body'))[:90])
"
```
Expected: `placeholder divs found: 94`, `with parseable [Figure N] lead-in: 94`, and a sample caption starting `Figure 1: Five functional properties…`.

If the counts disagree, the regex is wrong for the real file — fix it before moving on. This check is why the task exists.

- [ ] **Step 6: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/scripts/inject_html.py skills/paper-figures/scripts/tests/test_inject_html.py
git commit -m "feat(paper-figures): inject base64 figures and lightbox into glossed HTML"
```

**Note for Stage 9:** `LIGHTBOX_JS` calls `window.closeGlossPopover()` and `window.closeGlossPanel()`. The paper-gloss skill must be amended to expose those two functions on `window`, or the coordination silently no-ops. That is a required part of Stage 9, not optional.

---

## Stage 7 — Contact sheet

### Task 7: Build the review contact sheet

**Files:**
- Create: `skills/paper-figures/scripts/contactsheet.py`
- Test: `skills/paper-figures/scripts/tests/test_contactsheet.py`

- [ ] **Step 1: Write the failing test**

Create `skills/paper-figures/scripts/tests/test_contactsheet.py`:

```python
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contactsheet import build_sheet  # noqa: E402


class TestContactSheet(unittest.TestCase):
    def setUp(self):
        d = os.path.dirname(__file__)
        self.p = os.path.join(d, "_cs.png")
        with open(self.p, "wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n" + b"data" * 10)
        self.entries = [
            {"num": 1, "path": self.p, "caption": "First figure.", "verdict": "pass"},
            {"num": 2, "path": self.p, "caption": "Second & <odd>.", "verdict": "fail",
             "reason": "blank or unrendered"},
            {"num": 3, "path": None, "caption": "Not captured.", "verdict": "missing",
             "reason": "no static asset and screenshot failed"},
        ]
        self.out = build_sheet(self.entries, "Test Paper")

    def tearDown(self):
        os.remove(self.p)

    def test_every_entry_appears(self):
        for n in (1, 2, 3):
            self.assertIn(f"Figure {n}", self.out)

    def test_captured_figures_are_inlined(self):
        self.assertEqual(self.out.count("data:image/png;base64,"), 2)

    def test_failures_are_visibly_marked(self):
        self.assertIn("blank or unrendered", self.out)
        self.assertIn('class="entry fail"', self.out)

    def test_missing_figure_has_no_img(self):
        self.assertIn('class="entry missing"', self.out)
        self.assertIn("no static asset and screenshot failed", self.out)

    def test_captions_are_escaped(self):
        self.assertIn("Second &amp; &lt;odd&gt;.", self.out)
        self.assertNotIn("<odd>", self.out)

    def test_summary_counts_are_present(self):
        self.assertIn("3 figures", self.out)
        self.assertIn("1 pass", self.out)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'contactsheet'`

- [ ] **Step 3: Write the implementation**

Create `skills/paper-figures/scripts/contactsheet.py`:

```python
#!/usr/bin/env python3
"""Build a throwaway contact sheet for reviewing captured figures.

Usage:
    python3 contactsheet.py <entries.json> <out.html> [--title "Paper title"]

Thumbnails are inlined so the sheet is one portable file. It is never
committed — it exists only for the approval gate.
"""
import argparse
import base64
import html as htmllib
import json
import os

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


def thumb_uri(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as fh:
        blob = base64.b64encode(fh.read()).decode("ascii")
    return f"data:{MIME.get(ext, 'image/png')};base64,{blob}"


def build_sheet(entries, title):
    blocks = []
    for e in entries:
        verdict = e.get("verdict", "pass")
        cap = htmllib.escape(e.get("caption", ""))
        if e.get("path") and os.path.exists(e["path"]):
            body = f'<img src="{thumb_uri(e["path"])}" alt="Figure {e["num"]}">'
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
    args = ap.parse_args(argv)
    with open(args.entries, encoding="utf-8") as fh:
        entries = json.load(fh)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(build_sheet(entries, args.title))
    print(f"wrote {args.out} ({os.path.getsize(args.out):,} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts && python3 -m unittest discover -s tests -v`
Expected: `Ran 44 tests` … `OK`

- [ ] **Step 5: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/scripts/contactsheet.py skills/paper-figures/scripts/tests/test_contactsheet.py
git commit -m "feat(paper-figures): build the review contact sheet"
```

---

## Stage 8 — Skill prose

### Task 8: Write `references/capture-recipes.md`

**Files:**
- Create: `skills/paper-figures/references/capture-recipes.md`

- [ ] **Step 1: Write the reference file**

It must contain, verbatim and already verified:

- **Fetch the page:** `curl -sL --max-time 60 "<url>" -o /tmp/paper-page.html`
- **Manifest:** `python3 webfigs.py /tmp/paper-page.html "<url>" -o /tmp/manifest.json`
- **Static download:** `curl -sL --max-time 60 "<img_url>" -o figures/<slug>/fig-NN.png`
- **Interactive capture (Playwright MCP):** navigate once to the source URL;
  for each interactive figure, `browser_evaluate` to
  `document.querySelector('figure[data-fignum="N"]').scrollIntoView({block:'center'})`,
  `browser_wait_for` a short settle, then `browser_take_screenshot` with the element
  ref for `figure[data-fignum="N"]`. **Reuse one browser session for all captures** —
  do not re-navigate per figure.
- **PDF (not implemented in this plan; documented for the follow-up):**
  `pdftotext -bbox-layout -f P -l P in.pdf -` gives `<page width="612.000000" height="792.000000">`
  and per-word `xMin/yMin/xMax/yMax` in points. Convert to pixels with `px = pt / 72 * dpi`,
  then crop: `pdftoppm -png -r 220 -f P -l P -x X -y Y -W W -H H in.pdf out`.
  Verified working on arXiv 1706.03762.

- [ ] **Step 2: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/references/capture-recipes.md
git commit -m "docs(paper-figures): add capture recipes reference"
```

### Task 9: Write `SKILL.md`

**Files:**
- Create: `skills/paper-figures/SKILL.md`

- [ ] **Step 1: Write the skill**

Frontmatter `name: paper-figures`; the description must trigger on `/paper-figures`,
"add figures to this paper", "get the figures into the eli5", and must disambiguate
from `paper-eli5` (does the rewrite) and `paper-gloss` (does the glossary).

Body mirrors the spec's phases, each phase calling the scripts built above:
Phase 0 resolve target + source (PDF sources: **report and stop — not yet supported**),
Phase 1 `ledger.py`, Phase 2 `webfigs.py` + capture, Phase 3 `normalize.py`,
Phase 4 `checks.py` + Tier 2 visual sample, Phase 5 `contactsheet.py` + **hard gate**,
Phase 6 `inject.py` / `inject_html.py`, Phase 7 verification, Phase 8 delivery.

State explicitly: the report must say how many figures were visually reviewed versus
programmatically checked only, and must never imply all were inspected.

- [ ] **Step 2: Verify the skill is discoverable**

Run: `ls -la ~/.claude/skills/paper-figures/SKILL.md`
Expected: resolves through the symlink into this repo.

- [ ] **Step 3: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/SKILL.md
git commit -m "feat(paper-figures): add the paper-figures skill"
```

---

## Stage 9 — Amendments to existing skills

### Task 10: Fix paper-gloss and paper-eli5

**Files:**
- Modify: `skills/paper-gloss/SKILL.md`
- Modify: `skills/paper-eli5/SKILL.md`
- Modify: `docs/command-skill-reference.md`

- [ ] **Step 1: Amend paper-gloss — self-containment rule**

In "Self-containment & theming" and the Phase 3 checklist, replace the rule that greps
for `http://` / `https://` with: **zero *external* `src=` / `href=` / `@import`;
`data:` URIs are explicitly permitted.** The old rule is what downgraded all 10 static
figures.

- [ ] **Step 2: Amend paper-gloss — stop discarding images**

In the construct-mapping table, change the `[Figure N]` row so a markdown image
(`![Figure N](url)`) is **downloaded and inlined as a base64 `<figure>`**, not converted
to a placeholder with an `img-note` span. Only a bare `[Figure N]` becomes a placeholder.

- [ ] **Step 3: Amend paper-gloss — expose the close functions**

Required by Stage 6's lightbox. The popover and panel close functions must be assigned
to `window.closeGlossPopover` and `window.closeGlossPanel` so the lightbox can enforce
"only one interactive surface open at a time". Add this to the popover and panel specs.

- [ ] **Step 4: Amend paper-gloss — add the figure spec**

Add `.paper-figure` / `<figcaption>` / lightbox to the construct-mapping table and the
interaction rules, matching Stage 6's markup exactly.

- [ ] **Step 5: Amend paper-eli5 — Phase 3 counting**

Change the figure check to count **figure slots (placeholder *or* image)**, since
`[Figure N]` becomes `![Figure N](…)` after a retrofit. Add a closing pointer that
`/paper-figures` is the follow-up step for figures.

- [ ] **Step 6: Update the reference doc**

Add a `paper-figures` row to the appropriate category table, one-line description:
what it does, not how.

- [ ] **Step 7: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-gloss/SKILL.md skills/paper-eli5/SKILL.md docs/command-skill-reference.md
git commit -m "fix(paper-gloss): permit data URIs and stop discarding markdown images"
```

---

## Stage 10 — Slice A: the 10 static figures

### Task 11: Prove the full pipeline without Playwright

- [ ] **Step 1: Build ledger and manifest**

```bash
cd /Users/kyledisch/Projects/claude-config/skills/paper-figures/scripts
P=/Users/kyledisch/Projects/jacobian-lens
M=$P/verbalizable-representations-global-workspace-language-models-eli5.md
python3 ledger.py "$M" -o /tmp/ledger.json
```
Expected: `94 figure slots`.

- [ ] **Step 2: Download the 10 static images**

Use the `existing_url` values already in the ledger (figures 4, 47, 52, 53, 54, 57, 58,
59, 60, 73) into `$P/figures/verbalizable-representations/fig-NN.png`.

- [ ] **Step 3: Run Tier 1 checks**

Run: `python3 checks.py $P/figures/verbalizable-representations -o /tmp/checks.json`
Expected: `10 checked: 10 pass, 0 review, 0 fail`. Any failure here means a bad download.

- [ ] **Step 4: Normalize and contact-sheet**

```bash
python3 normalize.py $P/figures/verbalizable-representations /tmp/inline --count 94
python3 contactsheet.py /tmp/entries.json /tmp/sheet.html --title "Verbalizable Representations"
```
Send `/tmp/sheet.html` and confirm the 10 render correctly.

- [ ] **Step 5: Inject into both files and verify**

Confirm: markdown still has 94 slots (10 now images); HTML has 10 `<figure class="paper-figure">`
and 84 remaining placeholders; zero external `src=`; the file opens in Playwright with
the 10 figures visibly rendered.

- [ ] **Step 6: Commit**

```bash
cd /Users/kyledisch/Projects/jacobian-lens
git add figures/ *.md *.html
git commit -m "feat: add the 10 static figures to the eli5 and glossed outputs"
```

---

## Stage 11 — Slice B: 10 interactive figures

### Task 12: Prove the Playwright path

- [ ] **Step 1: Capture figures 1, 2, 3, 5, 6, 7, 8 plus 20, 45, 90**

One browser session, scroll-into-view, settle, element screenshot per the recipes file.
The three later figures exist specifically to shake out scroll-triggered mounts far down
the page.

- [ ] **Step 2: Run Tier 1 checks**

Run: `python3 checks.py /tmp/sliceb -o /tmp/checks-b.json`
Expected: `10 checked: 10 pass`. A `fail` with `blank or unrendered` means the settle
time is too short — increase it and re-capture. A `byte-identical` failure means the
selector matched the wrong element.

- [ ] **Step 3: Visually review all 10**

At this slice size, review every one. Confirm no caption is duplicated inside the image
and nothing bled in from neighbouring content.

- [ ] **Step 4: Record the settle time that worked**

Write it into `references/capture-recipes.md` — Slice C depends on it.

- [ ] **Step 5: Commit**

```bash
cd /Users/kyledisch/Projects/claude-config
git add skills/paper-figures/references/capture-recipes.md
git commit -m "docs(paper-figures): record the verified browser settle time"
```

---

## Stage 12 — Slice C: the full 94 and delivery

### Task 13: Full run

- [ ] **Step 1: Capture all 84 interactive figures** in one browser session.

- [ ] **Step 2: Tier 1 on all 94.** Re-capture every `fail`; escalate every `review`.

- [ ] **Step 3: Tier 2 visual review** on a ~12-figure spread plus every flagged figure.

- [ ] **Step 4: Normalize at `--count 94`.** Confirm total inline bytes ≤ 6MB.

- [ ] **Step 5: Contact sheet → hard gate.** Send and wait for approval.

- [ ] **Step 6: Inject into both files.**

- [ ] **Step 7: Full verification per spec Phase 7:**

```bash
grep -c 'class="paper-figure"' <glossed.html>      # expect 94
grep -c 'figure-placeholder' <glossed.html>        # expect 0
grep -oE 'src="https?://' <glossed.html> | wc -l   # expect 0
ls -la <glossed.html>                              # expect under 10MB
```
Then open it in Playwright and screenshot to confirm figures actually render.

- [ ] **Step 8: Deliver.** Commit in the jacobian-lens repo, push, PR, merge, re-publish
the Artifact, SendUserFile the HTML, and report the per-figure table with the
visually-reviewed-vs-programmatically-checked split stated plainly.

---

## Follow-up (not this plan)

The PDF backend. The mechanics are already verified and recorded in
`references/capture-recipes.md`; it needs its own plan covering caption-anchored crop
inference, the vision-corrected crop loop, and validation against a real arXiv paper.
