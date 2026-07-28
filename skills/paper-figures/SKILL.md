---
name: paper-figures
description: Retrofit real figure images into an already-generated paper-eli5 output. Point it at a `-eli5.md` or `-eli5-glossed.html` and it re-finds the original source from the header block, harvests the actual figures (direct download for static assets, browser screenshots for JS-rendered graphics), and replaces the `[Figure N]` placeholders in place — images in the markdown, base64 data URIs plus a click-to-zoom lightbox in the HTML. One approval gate on a contact sheet, never one per figure. Never re-runs the rewrite, never touches caption wording, never re-opens the glossary. Use for "add the figures to this paper", "get the real figures into the eli5", "the figures are missing from the glossed page", or `/paper-figures`. Distinct from `/paper-eli5` (does the rewrite) and `/paper-gloss` (does the glossary).
---

# Paper Figures — harvest the real figures into an existing eli5

`/paper-eli5` and `/paper-gloss` reproduce a paper's prose faithfully but drop
its figures, leaving `[Figure N]` placeholders holding the spot with a rewritten
caption. On a figure-heavy paper that is a large fraction of the actual content.

This skill is a **retrofit pass**. It re-finds the original source, harvests the
real images, and fills the placeholders. It does not re-run the rewrite.

**Scope:** web sources only. PDF sources are **not yet supported** — report and
stop. The mechanics are documented in `references/capture-recipes.md` for the
follow-up that implements them.

Deterministic work lives in stdlib-only Python under `scripts/`; this file is
the orchestration and the judgement calls. Load
`references/capture-recipes.md` when you reach Phase 2 — it holds the exact
invocations.

---

## Input (`$ARGUMENTS`)

| Argument | Meaning |
|---|---|
| path to a `-eli5.md` | The target. If a sibling `-eli5-glossed.html` exists, offer to update both. |
| path to a `-eli5-glossed.html` | The target. If a sibling `-eli5.md` exists, offer to update both. |
| `--source <path\|url>` | Override the source resolved from the header block. |
| `--from-folder <dir>` | Manual mode: map `fig-01.png`, `fig-02.png`, … by number; skip automated capture. |
| none | Scan the current directory, `docs/papers/`, and `papers/` for `*-eli5.md` / `*-eli5-glossed.html` and show the list. |

**Unattended with no or ambiguous argument:** report the ambiguity as the
outcome. Do not guess which paper was meant.

---

## Phase 0 — Resolve target and source

Both output formats carry a header block with a `**Source:**` line. Read it to
re-find the original — this is why no PDF needs to have been retained, and why
the skill works on papers generated before it existed.

Classify the source:

- **web** — any non-PDF URL. Supported.
- **pdf** — a local `.pdf`, an arXiv URL, or a bare arXiv ID. **Report and stop**
  with the reason; the PDF backend is not implemented.
- **folder** — `--from-folder`. Supported, manual.

If the `Source:` line is missing or unreachable and no `--source` was given,
stop and report. Do not guess a source.

## Phase 1 — Build the figure ledger

```bash
python3 scripts/ledger.py <paper>-eli5.md -o /tmp/ledger.json
```

One entry per figure slot: number, line index, caption as it currently reads, and
an `existing_url` when the placeholder is already a markdown image. Both
placeholder forms are recognized:

```markdown
[Figure 1]
![Figure 4](https://…/img_1b62b10ab235e6e7.png)
```

For an HTML-only target, parse the `.figure-placeholder` divs instead.

**The ledger is the contract: every entry must end either resolved with a real
image or explicitly flagged with a stated reason. Silent drops are a defect.**

## Phase 2 — Capture

Load `references/capture-recipes.md` now.

Fetch the page, then `scripts/webfigs.py` to enumerate `<figure data-fignum="N">`
elements and classify each. Figures are addressed by the `data-fignum`
attribute, never by caption-text matching.

- **Static** (contains an `<img>`) → download the asset directly. Highest
  fidelity, near-free. The ledger's `existing_url` usually already has these.
- **Interactive** (a JS mount div) → drive Playwright: navigate **once**, then
  per figure scroll it into view, wait to settle, and element-screenshot the
  figure container at device scale factor 2. Reuse one browser session for all
  captures. Flag these in the report as *static snapshots of interactive
  graphics*.

Exclude the `<figcaption>` from the screenshot region where the DOM allows it —
injection re-renders the caption as real text, so capturing it duplicates it.

Anything the automated paths fail on falls back to `--from-folder`.

## Phase 3 — Normalize

```bash
python3 scripts/normalize.py <figures-dir> /tmp/inline --count <total-figures>
```

Full-resolution originals are written to
`<paper-dir>/figures/<slug>/fig-NN.png`. They are committed, are what the
**markdown** references, and are never downscaled. The budget applies only to
the copies inlined into the HTML:

```
per_figure = min(250_000, 6MB / figure_count)
```

94 figures → ~64KB each; 8 figures → the full 250KB cap. Pass `--count` as the
**total** figure count even when normalizing a slice.

Say plainly in the report that on a figure-dense paper the lightbox zoom is
limited by the inlined resolution, and that the full-resolution copies live in
`figures/`.

`normalize.py` needs macOS `sips`. On another host, report that rather than
inlining un-normalized figures.

## Phase 4 — Self-verify

Two tiers, because visual review does not scale to 94 figures.

**Tier 1 — programmatic, on every figure.**

```bash
python3 scripts/checks.py <figures-dir> -o /tmp/checks.json
```

Catches the dominant failure mode — a JS visualization that never rendered —
plus degenerate dimensions and byte-identical captures (a sign the selector
matched the wrong element). Re-capture with a longer settle before escalating.

**Tier 2 — visual, on a sample.** View roughly 12 figures spread across the
document, **plus every figure Tier 1 flagged**. For each confirm: it is
*complete* (no clipped axis labels, no cut-off panel, no missing legend);
*nothing bled in* (no body text, no adjacent figure, no page furniture); and it
*matches its caption* (a caption describing three panels shows three panels).

## Phase 5 — Contact sheet gate (HARD STOP)

Build the sheet's input with `entries.py` — **never hand-assemble it.** It joins
the three sources the sheet needs (captions from the ledger, paths from the
figures directory, verdicts from Tier 1) and emits **one entry per ledger slot**,
so a figure that was never captured appears as `missing` instead of silently
vanishing from the review. A hand-built list is assembled from the files that
exist, which is exactly how the Phase 1 ledger-closure contract gets broken.

```bash
python3 scripts/entries.py /tmp/ledger.json <figures-dir> \
        --checks /tmp/checks.json -o /tmp/entries.json
python3 scripts/contactsheet.py /tmp/entries.json /tmp/sheet.html --title "<paper>"
```

To retain a slot deliberately without an image, add a `skip_reason` to that
figure in the ledger JSON before running `entries.py`; it is carried onto the
sheet as the stated reason. That is the only sanctioned way to close a slot
without a capture.

Thumbnails inlined, numbered, captions underneath, Tier 1 failures visibly
marked. Not committed. Send it with SendUserFile, then stop and ask:

> "Here are the N figures I captured. Reply 'all good', or list what to fix
> (e.g. '3 bad crop, 5 drop')."

**Do not proceed without a response.** Rejected figures are re-captured with a
different backend or a corrected crop and re-presented; a figure rejected twice
falls back to manual mode or stays a placeholder with a stated reason.

**Unattended runs** cannot stop for a gate: proceed on Phase 4 alone and state
prominently in the report that the gate was skipped and the figures are
unreviewed.

## Phase 6 — Inject

```bash
python3 scripts/inject.py md   in.md   out.md   images-md.json
python3 scripts/inject.py html in.html out.html images-html.json
```

The two maps differ — markdown references figures by **relative path**, HTML
inlines the **file contents**, so its map must point at openable paths.

Markdown: only the placeholder line changes; the caption line, the prose, and the
total line count are untouched.

```markdown
![Figure 1](figures/verbalizable-representations/fig-01.png)

Figure 1: Five functional properties of a global workspace…
```

HTML: each `.figure-placeholder` div becomes a real `<figure class="paper-figure">`
with a base64 `data:` URI, a non-empty `alt`, and a `<figcaption>`; the supporting
CSS and a **singleton** lightbox are added once. The lightbox reuses the same
inlined bytes, is wired with one delegated listener, and obeys paper-gloss's
one-interactive-surface-at-a-time rule — opening it closes the gloss popover and
panel via `window.closeGlossPopover` / `window.closeGlossPanel`. Close button,
click-outside, and `Escape` all converge on one close function.

Figure captions stay **excluded from gloss-term wrapping**.

Both injectors are idempotent; re-running will not duplicate CSS or the lightbox.

## Phase 7 — Verify injection

- **Ledger closure:** every entry resolved with an image, or a placeholder
  retained with a stated reason. No silent drops.
- **Markdown:** `![Figure N](…)` count == ledger count; every referenced path
  exists on disk; the diff touches only placeholder lines.
- **HTML:** `<figure class="paper-figure">` count == ledger count; every
  `<img src>` is a `data:` URI; every `<img>` has a non-empty `alt`.
- **Self-containment:** zero external *resource loads* — no external `src=`, no
  `<link … href=…>`, no `@import`, no CSS `url(http…)`:

  ```bash
  grep -oE 'src="https?://' f | wc -l          # expect 0
  grep -oE '<link[^>]+href="https?://' f | wc -l  # expect 0
  grep -c '@import' f                           # expect 0
  grep -oE 'url\(\s*["'"'"']?https?://' f | wc -l # expect 0
  ```

  `data:` URIs are permitted. **Prose `<a href="https://…">` hyperlinks are also
  permitted** — a link the reader can click is not a resource the page fetches,
  and papers legitimately link to repos, demos, and sources. Do not grep for a
  bare `https://`, and do not grep `href=` undifferentiated: the first rule is
  what downgraded real figures to placeholders, and the second fails every paper
  that cites a URL.
- **No collateral damage:** re-run paper-gloss's Phase 3 checks that injection
  could disturb — per-section `<p>` counts, heading text and order, gloss-term
  coverage, dictionary symmetry.
- **Math still rendered:** `python3 ../paper-gloss/scripts/check_math.py f` exits
  clean. `inject_html.py` only swaps `.figure-placeholder` divs and appends at
  the `</style>` / `</body>` seams, so it has no path to math — but this pass
  re-publishes the page, and a re-publish that ships unrendered TeX is a defect
  no matter which stage introduced it. On an older page predating the math
  contract the check will fail honestly; hand it to `/paper-gloss --retrofit`
  rather than suppressing it. The contract itself lives in
  `../paper-gloss/references/math-rendering.md` — one copy, cited, never forked.
- **End-to-end proof:** open the finished HTML in Playwright and screenshot it.
  Confirm the figures actually *render* — not merely that the tags are present —
  and that clicking one opens the lightbox with no console errors.
- **Size:** report total HTML size. If it exceeds 10MB, re-run normalization at a
  smaller per-figure share rather than shipping a file that may fail to publish.

Fix any discrepancy and re-verify before claiming done.

## Phase 8 — Deliver

- **Git:** feature branch **in the paper's own repo**, commit the images and the
  updated files, push, PR, merge autonomously, brief Kyle — unless that project's
  CLAUDE.md tightens it. Outside a repo: just write the files.
- **Re-publish the Artifact** if the glossed HTML changed. A figure retrofit
  publishes a **brand-new artifact**, not a redeploy — that remains this skill's
  rule. Do not read it as a claim that redeploying is impossible: `paper-gloss`'s
  RETROFIT mode deliberately republishes in place with `Artifact(url=…)`, the one
  named carve-out, because repairing math on a page Kyle already shared must not
  orphan his link. Whether a figure retrofit should take the same carve-out is an
  open question, not settled here — if Kyle gives you the existing URL, use it.
- **SendUserFile** the updated HTML.
- **Final report:** a per-figure table — number, capture method
  (direct-download / browser-shot / manual), final dimensions, file size — plus
  every flag: interactive-graphic snapshots, unresolved placeholders and why,
  crops corrected after self-verify, total HTML size, new Artifact URL, PR link.

**State the review split plainly: how many figures were visually reviewed versus
programmatically checked only. Never imply all of them were inspected.**

---

## Scope boundary

Does **not** re-run the rewrite, does **not** touch caption wording, does **not**
re-open the glossary term list. It only fills figure slots.

## Definition of done

Every ledger entry carries a real image or a stated reason; Tier 1 passes on all
captures; the contact-sheet gate was answered (or its absence reported); both
files are injected and verified; the finished HTML renders its figures under a
Playwright screenshot and is under 10MB; the report states the
visually-reviewed-versus-programmatically-checked split.
