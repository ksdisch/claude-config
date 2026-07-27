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

## Decisions taken (approved 2026-07-27)

| Decision | Choice | Rationale |
|---|---|---|
| Where the logic lives | New standalone `/paper-figures` skill, callable by the others later | Keeps failure-prone extraction in one place with its own verification loop; retrofits already-generated papers; doesn't destabilize two working skills |
| HTML embedding | Base64 `data:` URIs + click-to-zoom lightbox | Preserves the single-file guarantee and the published Artifact link |
| Human gating | One approval gate on a contact sheet | Mirrors paper-gloss's existing term-list gate; one stop, not N |
| Capture strategy | Cheap deterministic path first, vision/browser fallback | Pure heuristics are brittle on multi-column PDFs; pure vision costs an image read per figure |

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

1. **Static asset first.** Fetch the page HTML, locate the `<figure>`/`<img>` whose
   caption matches "Figure N", and download the asset directly. Highest fidelity and
   near-free. This path alone resolves the Figure 4 case above.
2. **Browser screenshot fallback.** For figures with no static asset (interactive JS
   graphics), drive Playwright: navigate to the source URL, wait for network idle,
   locate the element containing the caption, and element-screenshot its figure
   container at device scale factor 2. Capture the graphic's default state, and flag
   it in the final report as a *static snapshot of an interactive graphic*.

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

## Phase 3 — Normalize

- `sips` caps width at 1400px and strips the colour profile.
- Encode as PNG for line art and plots, JPEG q80 for photographic or dense raster
  content — whichever is smaller for that image.
- Target ≤250KB per figure; if still over after resizing, step width and quality down.
- Write full-resolution originals to `<paper-dir>/figures/<slug>/fig-NN.png`. These are
  committed, are what the markdown references, and are reused by any later re-run.

## Phase 4 — Self-verify each capture (before the gate)

For each captured image, view it and confirm:

- the figure is **complete** — no clipped axis labels, no cut-off panel, no missing legend;
- **nothing bled in** — no body text, no adjacent figure, no page furniture;
- it **matches its caption** — if the caption describes three panels, three panels are visible.

Failures are re-cropped or flagged. They are never shipped to the gate as if correct.

## Phase 5 — Contact sheet gate (HARD STOP)

Build a throwaway `figures-contact-sheet.html` — inlined thumbnails, numbered, with each
caption underneath — and send it via SendUserFile. Then stop and ask:

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
- **Size:** report the total HTML file size; warn above ~8MB as an artifact-publishing
  risk.

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
`jacobian-lens/verbalizable-representations-…-eli5.md` and its glossed HTML, producing
real figures verified by a Playwright screenshot of the rendered output; the reference
doc row is added; the branch is committed, pushed, and merged via PR.
