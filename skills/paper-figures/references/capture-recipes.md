# Capture recipes

Exact invocations for each backend. `SKILL.md` states the strategy; this file
states the commands. Load it on demand, not up front.

All script paths below are relative to `skills/paper-figures/scripts/`.

---

## Web sources

### 1. Fetch the page

```bash
curl -sL --max-time 60 "<url>" -o /tmp/paper-page.html
```

If the fetch fails or returns a login/paywall shell, stop and report — do not
fall back to guessing figure URLs.

### 2. Build the manifest

```bash
python3 webfigs.py /tmp/paper-page.html "<url>" -o /tmp/manifest.json
```

Prints `N figures: S static, I interactive` to stderr. Figures are addressed by
the `data-fignum` attribute, never by matching caption text.

Cross-check the manifest against the ledger from `ledger.py`. They should agree
on the figure numbers; a disagreement means either the page changed since the
eli5 was generated or one of the parsers is wrong. Resolve it before capturing.

### 3. Static figures — direct download

Highest fidelity and near-free. Use the `img_url` from the manifest, or the
`existing_url` already carried in the ledger (paper-eli5 preserves markdown
image URLs, so the static set usually needs no page fetch at all).

```bash
mkdir -p "<paper-dir>/figures/<slug>"
curl -sL --max-time 60 -w '%{http_code}\n' "<img_url>" \
  -o "<paper-dir>/figures/<slug>/fig-NN.png"
```

Confirm every download returned `200` before moving on. Zero-byte or HTML-body
responses will fail the Tier 1 checks, but catching them here is cheaper.

### 4. Interactive figures — Playwright MCP

These are JS visualizations mounted into an empty div; they exist only once
rendered in a browser.

**Reuse one browser session for every capture — do not re-navigate per figure.**
Navigation is the expensive part, and re-navigating 84 times is what turns a
long run into a failed one.

Per figure:

1. Scroll it into view — mounts are often scroll-triggered:
   ```js
   document.querySelector('figure[data-fignum="N"]').scrollIntoView({block: 'center'})
   ```
   via `browser_evaluate`.
2. Wait for the settle time (see below) with `browser_wait_for`.
3. `browser_take_screenshot` with the element ref for `figure[data-fignum="N"]`,
   at device scale factor 2.

Exclude the `<figcaption>` from the screenshot region where the DOM allows it —
the caption is re-rendered as real text by the injection step, so capturing it
duplicates it.

Flag every figure captured this way in the final report as a **static snapshot
of an interactive graphic**.

**Settle time:** not yet measured against a real run. Slice B of the
implementation plan exists to determine it; record the value that worked here
before attempting a full-paper run. Start at ~500ms and increase if Tier 1
reports `blank or unrendered`.

### 5. Tier 1 checks

```bash
python3 checks.py "<paper-dir>/figures/<slug>" -o /tmp/checks.json
```

Prints `N checked: P pass, R review, F fail`, exits non-zero if anything failed.

- `blank or unrendered` → the settle time is too short. Increase it and
  re-capture that figure.
- `byte-identical to another capture` → the selector matched the wrong element.
- `degenerate dimensions` / `implausible aspect ratio` → the mount collapsed
  before rendering.

### 6. Normalize

```bash
python3 normalize.py "<paper-dir>/figures/<slug>" /tmp/inline --count <total-figures>
```

Pass `--count` as the **full** figure count, not the size of the slice being
processed, or a slice will be normalized against a budget it doesn't have.

Requires macOS `sips`. Originals are never modified — this writes budget-fitting
copies for base64 inlining.

### 7. Contact sheet

```bash
python3 contactsheet.py /tmp/entries.json /tmp/sheet.html --title "<paper title>"
```

`entries.json` is a JSON array of
`{"num": N, "path": "...", "caption": "...", "verdict": "pass|review|fail|missing", "reason": "..."}`.
Send the result with SendUserFile and stop for approval.

### 8. Inject

```bash
python3 inject.py md   in.md   out.md   images-md.json     # paths relative to the .md
python3 inject.py html in.html out.html images-html.json   # real paths on disk
```

The two images maps differ: markdown references figures by **relative path**,
HTML inlines the **file contents** as base64, so its map must point at paths
this process can actually open.

Both injectors are idempotent — re-running on an already-injected file will not
duplicate the CSS or the lightbox.

---

## PDF sources

**Not implemented.** The skill reports and stops on a PDF source. The mechanics
below were verified while writing the spec and carry over unchanged to the
follow-up plan that will implement this backend.

Caption anchor and page geometry:

```bash
pdftotext -bbox-layout -f P -l P in.pdf -
```

Emits `<page width="612.000000" height="792.000000">` and per-word
`xMin/yMin/xMax/yMax` in **points**.

Convert points to pixels at the chosen render resolution:

```
px = pt / 72 * dpi
```

Render a page for visual crop confirmation at ~110 DPI, then take the final crop
at ~220 DPI using poppler's native cropping — no ImageMagick dependency:

```bash
pdftoppm -png -r 220 -f P -l P -x X -y Y -W W -H H in.pdf out
```

Verified working on arXiv 1706.03762: `pdftoppm -png -r 150 -f 3 -l 3 -x 0 -y 0
-W 600 -H 500 attn.pdf croptest` produced `croptest-03.png`.

---

## Tool availability

Verified present on the target machine: `pdfimages`, `pdftoppm`, `pdftocairo`,
`pdftotext` (poppler), `sips` (macOS built-in), Playwright MCP browser tools.

**Absent — do not depend on them:** PyMuPDF, Pillow, ImageMagick, `mutool`,
`qpdf`.

`sips` is macOS-only. On a non-macOS host, `normalize.py` cannot run; the rest of
the pipeline (ledger, manifest, checks, injection, contact sheet) is stdlib-only
Python and runs anywhere. Report the limitation rather than silently skipping
normalization — inlining un-normalized figures is how the HTML blows past its
size budget.
