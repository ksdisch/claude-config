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

Drive this through `browser_run_code_unsafe` in **one call that loops over every
figure**, not one MCP call per figure — 84 round-trips is its own failure mode.

#### Set up the context explicitly

`browser_take_screenshot`'s element mode cannot express a clip region, and
`page.setViewportSize()` **permanently drops `deviceScaleFactor` to 1** on that
page — captures silently halve in resolution. Make a fresh context instead:

```js
const ctx = await page.context().browser().newContext({
  viewport: { width: 1440, height: 2600 },   // tall enough to clip most figures in one shot
  deviceScaleFactor: 2,
});
const p = await ctx.newPage();
await p.goto(url, { waitUntil: 'load' });
await p.waitForTimeout(1500);
```

#### Hide page furniture first — it bleeds into element screenshots

An element screenshot captures whatever is painted over that region, including
`position: fixed` page chrome. On transformer-circuits.pub a floating
table-of-contents chip (`div.toc-float`, `z-index: 100000`) landed on top of
Figure 1 and replaced its first panel title. Neutralize every fixed/sticky node
that is **not inside a figure** (in-figure sticky elements, e.g. `td.layer-label`
row headers, are part of the graphic and must stay):

```js
await p.evaluate(() => {
  document.querySelectorAll('body *').forEach(el => {
    if (el.closest('figure[data-fignum]')) return;
    const cs = getComputedStyle(el);
    if ((cs.position === 'fixed' || cs.position === 'sticky') && el.offsetHeight > 0 && el.offsetWidth > 0)
      el.style.setProperty('display', 'none', 'important');
  });
});
```

#### Per figure: scroll, settle, clip

Screenshot a **computed clip region**, not the element box. The mount's border
box is not always the figure's painted extent — axis labels and legends can sit
tens of pixels outside it, and an element screenshot cuts them off.

Compute the union of the mount and its visible descendants, but **skip any
descendant inside a clipped or scrollable ancestor**. That subtree is bounded by
its own container, and chasing it captures content the reader cannot see:
naively, Figure 87 demanded a 21,949px-tall region and Figure 5 a 2,788px-wide
one — both scrollable panes. With the rule below they need 0px and 13px.

```js
const rect = await p.evaluate(({ n, CAP, PAD }) => {
  const fig = document.querySelector(`figure[data-fignum="${n}"]`);
  const mount = [...fig.children].find(c => c.tagName !== 'FIGCAPTION');
  fig.scrollIntoView({ block: 'center' });
  const mr = mount.getBoundingClientRect();
  let minX = mr.left, minY = mr.top, maxX = mr.right, maxY = mr.bottom;
  mount.querySelectorAll('*').forEach(d => {
    const cs = getComputedStyle(d);
    if (cs.visibility === 'hidden' || cs.display === 'none' || cs.opacity === '0') return;
    let a = d.parentElement, clipped = false;
    while (a && a !== mount) {
      const acs = getComputedStyle(a);
      if (acs.overflowX !== 'visible' || acs.overflowY !== 'visible') { clipped = true; break; }
      a = a.parentElement;
    }
    if (clipped) return;                      // scrollable pane — already bounded
    const r = d.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return;
    minX = Math.min(minX, r.left); minY = Math.min(minY, r.top);
    maxX = Math.max(maxX, r.right); maxY = Math.max(maxY, r.bottom);
  });
  const x  = mr.left   - Math.min(CAP, Math.max(0, mr.left - minX)) - PAD;
  const y  = mr.top    - Math.min(CAP, Math.max(0, mr.top  - minY)) - PAD;
  const x2 = mr.right  + Math.min(CAP, Math.max(0, maxX - mr.right)) + PAD;
  const y2 = mr.bottom + Math.min(CAP, Math.max(0, maxY - mr.bottom)) + PAD;
  return { x, y, w: x2 - x, h: y2 - y, vw: innerWidth, vh: innerHeight };
}, { n, CAP: 120, PAD: 4 });

await p.waitForTimeout(450);
const fits = rect.x >= 0 && rect.y >= 0 && rect.x + rect.w <= rect.vw && rect.y + rect.h <= rect.vh;
if (fits) await p.screenshot({ path: file, clip: { x: rect.x, y: rect.y, width: rect.w, height: rect.h } });
else      await p.locator(`figure[data-fignum="${n}"] > div`).screenshot({ path: file });
```

`clip` is **viewport-relative** when `fullPage` is false — passing document
coordinates fails with *"Clipped area is either empty or outside the resulting
image"*. Hence scroll first, then clip; and fall back to an element screenshot
for any region taller or wider than the viewport.

Selecting `figure[data-fignum="N"] > div` (the single non-figcaption child)
excludes the `<figcaption>` — injection re-renders the caption as real text, so
capturing it would duplicate it. On this paper every figure had exactly one
content child: 84 `div`, 10 `img`.

Flag every figure captured this way in the final report as a **static snapshot
of an interactive graphic**.

**Settle time — measured on jacobian-lens (2026-07-27, 84 interactive figures):**
these mounts are **not scroll-triggered**. Immediately after a cold
`waitUntil: 'load'`, every mount was already fully populated — `innerHTML`
length and box size were identical before and after `scrollIntoView`. Time from
scroll to a stable box was **≤ 60ms**.

Use **1500ms after load, then 450ms per figure**. That is generous for this page
and cost only ~40s across all 84. Do not assume it generalizes: re-measure with
the before/after `innerHTML`-length probe on a new paper, and increase it if
Tier 1 reports `blank or unrendered`.

Note that a page open for several minutes will report near-zero settle for every
figure regardless — measure only immediately after a fresh navigation.

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

Two steps — build the entries, then render the sheet. Do **not** hand-assemble
`entries.json`:

```bash
python3 entries.py /tmp/ledger.json "<paper-dir>/figures/<slug>" \
        --checks /tmp/checks.json -o /tmp/entries.json
python3 contactsheet.py /tmp/entries.json /tmp/sheet.html --title "<paper title>"
```

`entries.py` joins captions (ledger), paths (figures directory) and verdicts
(Tier 1) into the shape `contactsheet.py` consumes:
`{"num": N, "path": "...", "caption": "...", "verdict": "pass|review|fail|missing", "reason": "..."}`.

It iterates the **ledger**, not the directory, so every slot produces an entry
and an uncaptured figure shows up as `missing` rather than disappearing from the
review — the ledger-closure contract in `SKILL.md` depends on this. Assembling
the list from the captured files instead is how a dropped figure goes unnoticed.

To keep a slot deliberately empty, set `skip_reason` on that figure in the
ledger JSON before running `entries.py`; the sheet then shows the slot with your
stated reason. Nothing else writes that field.

`contactsheet.py` downscales to `--max-width` (default 320) before inlining.
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
