# paper-figures — design spec

**Date:** 2026-07-27
**Status:** approved design, pre-implementation
**Deliverables:**
- one new skill at `skills/paper-figures/SKILL.md` + `skills/paper-figures/references/capture-recipes.md`
  (auto-invocable as `/paper-figures` via the `~/.claude/skills` symlink)
- amendments to `skills/paper-gloss/SKILL.md` (self-containment rule, image handling, figure/lightbox spec)
- a one-line amendment to `skills/paper-eli5/SKILL.md` (Phase 3 counting) plus a follow-up pointer
- a new row in `docs/command-skill-reference.md`

No command wrapper is needed: `paper-eli5` and `paper-gloss` have none either — the
skill name is directly invocable.

## Purpose

`/paper-eli5` and `/paper-gloss` reproduce a paper's prose faithfully but drop its
figures, leaving `[Figure N]` placeholders holding the spot with a rewritten caption.
For figure-heavy papers this removes a large fraction of the actual content.

`/paper-figures` is a **retrofit pass**: point it at an existing `-eli5.md` (and/or
its sibling `-eli5-glossed.html`), it re-finds the original source, harvests the real
figure images, and replaces the placeholders in place. It never re-runs the rewrite.

## Motivating findings (from the audit that produced this spec)

1. **Two source classes need two capture backends.** A PDF stores figures as regions
   of a rendered page; a web paper stores them as `<img>` assets *or* as interactive
   JS graphics that exist only once rendered in a browser.
2. **paper-gloss currently destroys an image it already has.** In
   `jacobian-lens/…-eli5.md`, Figure 4 is a real markdown image
   (`![Figure 4](https://transformer-circuits.pub/…/img_1b62b10ab235e6e7.png)`), and
   the glossed HTML downgraded it to a placeholder annotated
   `(image available at <url>)`. Cause: paper-gloss's self-containment rule forbids
   external `src=`. The fix is an embedding-policy change, not extraction.
3. **No manual screenshotting is required.** Verified present on this machine:
   `pdfimages`, `pdftoppm`, `pdftocairo`, `pdftotext` (poppler, `/opt/homebrew/bin`),
   `sips` (macOS built-in, supports `--resampleWidth`), and Playwright MCP browser
   tools. Absent: PyMuPDF, Pillow, ImageMagick, `mutool`, `qpdf` — the design must
   not depend on them.
4. **Figure counts can be very large, and the first draft of this spec underestimated
   them by an order of magnitude.** The jacobian-lens paper has **94 figures**, not the
   8 an initial truncated grep suggested. Of those, **10 are static `<img>`** (figures
   4, 47, 52–54, 57–60, 73) and **84 are JS-rendered** into empty mount divs
   (`<div class='intro-functional'></div>`). The eli5 output is faithful — it carries
   all 94 slots. Any design that costs O(1) human or model attention *per figure* fails
   at this scale.
5. **The web DOM is machine-addressable.** Figures are marked up as
   `<figure data-fignum="N" id="…"><…mount or img…><figcaption><span class="fig-num">Figure N: </span>…</figcaption></figure>`.
   The `data-fignum` attribute makes figure↔caption association an exact selector
   lookup, not fragile caption-text matching.

### Verified mechanisms

Both risky capture primitives were tested against real inputs before this spec was
finalized:

- `pdftoppm -png -r 150 -f 3 -l 3 -x 0 -y 0 -W 600 -H 500 attn.pdf croptest` on
  arXiv 1706.03762 produced `croptest-03.png`. Crop offsets are **pixels at the chosen
  render resolution**, so the conversion from PDF points is `px = pt / 72 * dpi`.
- `pdftotext -bbox-layout` emits `<page width="612.000000" height="792.000000">` and
  per-word `xMin/yMin/xMax/yMax` in points, giving the caption anchor needed to derive
  that crop box.

## Decisions taken (approved 2026-07-27)

| Decision | Choice | Rationale |
|---|---|---|
| Where the logic lives | New standalone `/paper-figures` skill, callable by the others later | Keeps failure-prone extraction in one place with its own verification loop; retrofits already-generated papers; doesn't destabilize two working skills |
| HTML embedding | Base64 `data:` URIs + click-to-zoom lightbox | Preserves the single-file guarantee and the published Artifact link |
| Human gating | One approval gate on a contact sheet | Mirrors paper-gloss's existing term-list gate; one stop, not N |
| Capture strategy | Cheap deterministic path first, vision/browser fallback | Pure heuristics are brittle on multi-column PDFs; pure vision costs an image read per figure |
| Size budget | Adaptive: fixed total, divided by figure count | One rule scales from an 8-figure paper to a 94-figure one without special-casing |
| Verification at scale | Programmatic check on all, visual review on a sample + all flagged | Visual review of 94 captures is unaffordable; the real failure mode (blank/unrendered viz) is programmatically detectable |

## Input (`$ARGUMENTS`)

- **Path to a `-eli5.md`** → the target. If a sibling `-eli5-glossed.html` exists,
  offer to update both.
- **Path to a `-eli5-glossed.html`** → the target. If a sibling `-eli5.md` exists,
  offer to update both.
- **`--source <path|url>`** → override the source resolved from the header block.
- **`--from-folder <dir>`** → manual mode; skip automated capture entirely.
- **No argument** → scan the current directory, `docs/papers/`, and `papers/` for
  `*-eli5.md` / `*-eli5-glossed.html` and show the list.
- **Unattended with no or ambiguous argument** → report the ambiguity as the outcome;
  don't guess.

## Phase 0 — Resolve target and source

Both output formats carry a header block with a `**Source:**` line (a URL or a local
path). Read it to re-find the original — this is why no PDF needs to be retained, and
why the skill works on papers generated before it existed.

Classify the source as **pdf** (local `.pdf`, arXiv URL, or bare arXiv ID → normalize
to `arxiv.org/pdf/<id>`, download to `/tmp`, never commit), **web** (any other URL), or
**folder** (`--from-folder`). If the `Source:` line is missing or unreachable and no
`--source` was given, stop and report — do not guess a source.

## Phase 1 — Build the figure ledger

Scan the target markdown (or, for HTML-only targets, the `.figure-placeholder` divs)
and record one entry per figure:

- figure number `N`
- the placeholder's exact location
- the caption text as it currently reads (already rewritten by paper-eli5)
- an existing image URL, if the placeholder is already a markdown image

Two placeholder forms exist in the wild and both must be recognized:

```markdown
[Figure 1]

Figure 1: caption text…
```
```markdown
![Figure 4](https://…/img_1b62b10ab235e6e7.png)

Figure 4: caption text…
```

The ledger is the contract: **every entry must end either resolved with a real image
or explicitly flagged with a stated reason.** Silent drops are a defect.

## Phase 2 — Capture

The exact shell invocations, flags, and coordinate conversions for each backend live in
`skills/paper-figures/references/capture-recipes.md`, loaded on demand — SKILL.md states
the strategy, the reference file states the commands.

### Web sources

Figures are addressed by the `data-fignum` attribute, never by caption-text matching.
Enumerate `<figure data-fignum="N">` elements once, then classify each:

1. **Static asset (contains `<img>`).** Resolve the `src` against the page URL and
   download the asset directly. Highest fidelity and near-free. 10 of jacobian-lens's
   94 figures take this path, including the Figure 4 case above.
2. **Interactive (no `<img>` — a JS mount div).** Drive Playwright: navigate once,
   scroll the target `figure[data-fignum="N"]` into view (mounts may be
   scroll-triggered), wait for it to settle, and element-screenshot that figure
   container at device scale factor 2. Reuse **one** browser session for all captures —
   do not re-navigate per figure. Capture the graphic's default state, and flag it in
   the final report as a *static snapshot of an interactive graphic*.

Exclude the `<figcaption>` from the screenshot region where the DOM allows it — the
caption is re-rendered as real text by the injection step, so capturing it would
duplicate it.

### PDF sources

1. `pdftotext -bbox-layout` → word-level bounding boxes and page dimensions. Find the
   "Figure N" / "Fig. N" caption line, its bbox, and its page.
2. Propose a crop box for the region adjacent to the caption — above it for figures,
   below it for tables — bounded by whitespace gaps and column-aware via text-gap
   analysis, extended to the enclosing column or the full text width as appropriate.
3. Render that page at ~110 DPI, **view the rendered page**, and confirm or correct
   the proposed box in page-fraction coordinates.
4. Final crop at ~220 DPI via poppler's native cropping:
   `pdftoppm -png -r 220 -f <page> -l <page> -x <X> -y <Y> -W <W> -H <H>`.
   No ImageMagick dependency.

### Manual fallback

`--from-folder <dir>` maps files named `fig-01.png`, `fig-02.png`, … to ledger entries
by number. Also used per-figure for anything the automated paths fail on, or that the
Phase 5 gate rejects twice.

## Phase 3 — Normalize (adaptive budget)

Full-resolution originals are always written to `<paper-dir>/figures/<slug>/fig-NN.png`.
These are committed, are what the **markdown** references, and are reused by any later
re-run. They are never downscaled — the budget applies only to the copies inlined into
the HTML.

The inline budget is computed, not fixed:

```
TOTAL_IMAGE_BUDGET = 6 MB          # pre-base64; ~8MB once encoded
per_figure = TOTAL_IMAGE_BUDGET / figure_count
```

- 94 figures → ~64KB each (≈900px wide, JPEG q70)
- 8 figures → ~250KB+ each at near-full quality (cap width at 1400px regardless)

`sips` does the resampling (`--resampleWidth`) and strips the colour profile. Encode as
PNG for flat-colour line art and JPEG for photographic or dense raster content —
whichever is smaller for that image. If a figure still exceeds its share after resizing,
step width and quality down until it fits, and record the final dimensions in the report.

Consequence to state plainly in the report: on a 94-figure paper the lightbox zoom is
limited by the inlined resolution. The full-resolution copy lives in `figures/` for
anyone who needs it.

## Phase 4 — Self-verify (before the gate)

Two tiers, because visual review does not scale to 94 figures.

### Tier 1 — programmatic, on every figure

The dominant failure mode is a JS visualization that never rendered, which produces a
blank or near-uniform image. That is cheaply detectable:

- **Not blank / not near-uniform.** Sample the decoded pixels; reject if the image is a
  single flat colour or has near-zero variance.
- **Plausible dimensions** — not 0-width, not a 1×1 tracking pixel, not absurdly tall
  and thin (a sign the mount collapsed before rendering).
- **Non-trivial encoded size** relative to its dimensions.
- **Distinctness** — two different figure numbers producing byte-identical images means
  the selector matched the wrong element.

Any figure failing Tier 1 is re-captured (longer settle, re-scroll) before escalating.

### Tier 2 — visual, on a sample

View a sample of roughly 12 figures spread across the document, **plus every figure
Tier 1 flagged**. For each, confirm:

- the figure is **complete** — no clipped axis labels, no cut-off panel, no missing legend;
- **nothing bled in** — no body text, no adjacent figure, no page furniture;
- it **matches its caption** — if the caption describes three panels, three panels are visible.

Figures that fail are re-captured or flagged. The report must state plainly how many
figures were visually reviewed versus programmatically checked only — never imply all 94
were inspected.

## Phase 5 — Contact sheet gate (HARD STOP)

Build a throwaway `figures-contact-sheet.html` — inlined thumbnails (capped at ~320px
wide so the sheet itself stays small even at 94 figures), numbered, with each caption
underneath, and Tier-1 failures visually marked. It is not committed. Send it via
SendUserFile, then stop and ask:

> "Here are the N figures I captured. Reply 'all good', or list what to fix
> (e.g. '3 bad crop, 5 drop')."

Do not proceed to Phase 6 without a response. Rejected figures are re-captured (a
different backend, or a corrected crop box) and re-presented; a figure rejected twice
falls back to manual mode or stays a placeholder with a stated reason.

**Unattended runs** cannot stop for a gate. In that case, proceed on the strength of the
Phase 4 self-verification alone, and state prominently in the final report that the
contact-sheet gate was skipped and the figures are unreviewed.

## Phase 6 — Inject

### Into `-eli5.md`

Replace only the placeholder line. The caption line is **untouched**:

```markdown
![Figure 1](figures/verbalizable-representations/fig-01.png)

Figure 1: Five functional properties of a global workspace…
```

### Into `-eli5-glossed.html`

Replace the `.figure-placeholder` div with:

```html
<figure class="paper-figure">
  <img src="data:image/png;base64,…" alt="{caption}" loading="lazy">
  <figcaption>{caption}</figcaption>
</figure>
```

Add `.paper-figure` styling (centred, `max-width:100%`, rounded border, distinct
figcaption) using the existing CSS-variable theming — no hardcoded colours, so both
`prefers-color-scheme` and `data-theme` override layers keep working.

Add a **singleton lightbox**: clicking a figure opens it full-bleed in one shared
overlay element, reusing the same inlined data URI (no second copy of the bytes).
It obeys paper-gloss's existing "only one interactive surface open at a time" rule —
opening the lightbox closes any gloss popover and the glossary panel, and vice versa.
Dismiss via close button, click outside, or `Escape`, all converging on one close
function. Wire it with a single delegated listener, consistent with how `.gloss-term`
is already handled.

Figure captions remain **excluded from gloss-term wrapping**, exactly as the current
paper-gloss spec requires.

## Phase 7 — Verify injection

- **Ledger closure:** every entry resolved with an image, or a placeholder retained
  with a stated reason. No silent drops.
- **Markdown:** `![Figure N](…)` count == ledger count; every referenced path exists on
  disk; the diff touches only placeholder lines (caption and prose lines unchanged).
- **HTML:** `<figure class="paper-figure">` count == ledger count; every `<img src>` is a
  `data:` URI; every `<img>` has a non-empty `alt`.
- **Self-containment (revised check):** zero *external* `src=` / `href=` / `@import`;
  `data:` URIs are permitted. This replaces the old "grep for `https://` → zero hits"
  rule, which is what caused the Figure 4 regression.
- **No collateral damage:** re-run paper-gloss's Phase 3 checks that injection could
  disturb — per-section `<p>` counts, heading text and order, gloss-term coverage and
  dictionary symmetry.
- **End-to-end proof:** open the finished HTML in Playwright and screenshot it,
  confirming the figures actually render — not merely that the tags are present.
- **Size:** report the total HTML file size. The adaptive budget targets ~8MB encoded;
  if the finished file exceeds 10MB, re-run normalization at a smaller per-figure share
  rather than shipping a file that may fail to publish.

Fix any discrepancy and re-verify before claiming done.

## Phase 8 — Deliver

- **Git:** feature branch **in the paper's own repo**, commit the images and updated
  files, push, PR, merge autonomously, brief Kyle — unless that project's CLAUDE.md
  tightens it. Outside a repo: just write the files.
- **Re-publish the Artifact** if the glossed HTML changed. Per paper-gloss's existing
  rule this is a brand-new artifact, never a redeploy of a previous URL.
- **SendUserFile** the updated HTML.
- **Final report:** a per-figure table (number, capture method used —
  direct-download / browser-shot / pdf-crop / manual — final dimensions, file size),
  every flag (interactive-graphic snapshots, unresolved placeholders and why, crops
  corrected after self-verify), total HTML size, new Artifact URL, PR link.

## Amendments to existing skills

1. **`skills/paper-gloss/SKILL.md`**
   - Self-containment rule and Phase 3 check: forbid *external* `src=`/`href=`/`@import`;
     explicitly permit `data:` URIs.
   - Stop downgrading `![…](url)` markdown images to placeholders — download and inline
     them as base64 instead. (Fixes the Figure 4 regression on its own.)
   - Add the `.paper-figure` / `<figcaption>` / lightbox spec to the construct-mapping
     table and the interaction rules.
2. **`skills/paper-eli5/SKILL.md`**
   - Phase 3 verification counts "figure slots (placeholder **or** image)", since
     `[Figure N]` becomes `![Figure N](…)` after a retrofit.
   - Add a pointer to `/paper-figures` as the follow-up step.
3. **`docs/command-skill-reference.md`** — add the `paper-figures` row, in the same
   commit, per the global CLAUDE.md rule.

## Scope boundary

The skill does **not** re-run the rewrite, does **not** touch caption wording, and does
**not** re-open the glossary term list. It only fills figure slots.

Auto-invocation of `/paper-figures` from `/paper-eli5` is explicitly **out of scope for
this spec**. It happens only after the skill is proven standalone against the two
existing papers (`jacobian-lens`, `dim-stage`).

## Definition of done

`skills/paper-figures/SKILL.md` exists and is invocable as `/paper-figures`; the three
amendments above are made in the same branch; the skill has been run end-to-end against
`jacobian-lens/verbalizable-representations-…-eli5.md` and its glossed HTML, resolving
all **94** figure slots (10 by direct download, 84 by browser capture) with every slot
either carrying a real image or flagged with a stated reason; Tier-1 checks pass on all
94 and Tier-2 visual review passes on the sample; the finished HTML renders its figures
under a Playwright screenshot and is under 10MB; the reference doc row is added; the
branch is committed, pushed, and merged via PR.

## Staged rollout

The 84-figure browser-capture run is long and can be flaky, so implementation proves the
machinery on a slice before committing to the full run:

1. **Slice A — static path.** The 10 `<img>` figures end-to-end, including injection into
   both files. Proves ledger, normalize, inject, and verify without touching Playwright.
2. **Slice B — interactive path, 10 figures.** Figures 1, 2, 3, 5, 6, 7, 8 plus three
   later ones, to shake out scroll-triggered mounts and settle timing.
3. **Slice C — full 94.** Only after A and B are clean.
