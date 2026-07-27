---
name: paper-gloss
description: Post-process a paper-eli5 output into a self-contained, interactive HTML page where every occurrence of selected jargon terms is clickable — clicking reveals a plain-English expansion in a popup — plus a toggle-able glossary panel listing every approved term at once. AI proposes the candidate term list with expansions; you trim it; the skill hand-authors a themed, responsive HTML artifact mirroring the eli5 document 1:1. Delivers a `-glossed.html` file (via the repo's git workflow) and a published claude.ai Artifact link. Run after /paper-eli5 when specific terms are still opaque after the first rewrite.
---

# Paper Gloss — click-to-reveal jargon glosses

A companion to `/paper-eli5`. Takes a finished eli5 output and produces a second
pass where every approved technical term becomes **clickable at each occurrence**
— tapping it pops up a plain-English expansion, then dismisses. The original
prose is never rewritten or interrupted; the paper reads exactly as it did, with
jargon quietly wired up for lookup instead of permanently annotated inline.

Example: "The model is trained using **backpropagation**" — the term
`backpropagation` gets a dotted underline. Clicking it opens a small popup: *"a
step where errors are traced backward through each layer to adjust the model's
internal dials."* Clicking again, clicking elsewhere, or `Escape` closes it. The
same expansion also appears as a row in the Glossary panel (📖, fixed top-right)
so every expansion is still visible at a glance without touching the running text.

Because this is genuinely interactive, the deliverable is a self-contained HTML
page, not Markdown — delivered both as a file in the repo and as a published
claude.ai Artifact.

---

## Parse `$ARGUMENTS`

- **Local path** to a `-eli5.md` file → the target document.
- **No argument** → ask which file. Scan the current directory / `docs/papers/` for
  `*-eli5.md` files and show the list.
- **Unattended with no argument** → report the ambiguity; don't guess.

---

## Phase 1 — Propose term list (STOP here for approval)

Read the entire eli5 file. Identify every term that is still likely to be opaque
to a smart newcomer: field-specific vocabulary, acronyms, multi-word technical
phrases, named methods/architectures, statistical concepts. Do **not** include
ordinary English words or very common terms (e.g., "model", "data", "method"
used in plain senses).

For each candidate term, produce one plain-English expansion. Unlike the old
inline-parenthetical version, the expansion is read **out of context** — in a
popup or a glossary row, not stitched into the sentence that contains the term.
Expansions must:
- Read as a **standalone mini-definition** — understandable with zero surrounding
  sentence, e.g. "A method that nudges the model's settings using the error
  signal from a small random sample of training examples each step." (Not a
  clause built to slot in after the term grammatically — there's no sentence to
  slot into anymore.)
- Be concise (1 clause to 2 sentences) and capture the term's meaning accurately,
  not approximately.

Present the list as a numbered table:

```
| # | Term (as it appears) | Proposed plain-English expansion |
|---|----------------------|----------------------------------|
| 1 | stochastic gradient descent | A method that nudges the model's settings using the error signal from a small random sample of training examples each step. |
| 2 | …                    | …                                |
```

Then **STOP and ask Kyle**:

> "Here are the terms I found. Reply with the numbers you want to keep (e.g.
> '1, 3, 5'), or 'all' to keep the whole list, or 'none' to cancel. You can
> also correct any expansion by writing '4: [your preferred wording]'."

Do not proceed to Phase 2 until you have Kyle's response. This is a hard gate.
The approved list becomes the literal content of the `GLOSS_TERMS` dictionary in
Phase 2 — whatever Kyle approves/edits here flows through unchanged.

---

## Phase 2 — Generation pass (build the HTML)

There is no markdown-to-HTML library or template in this skill — hand-author the
HTML directly, section by section, the same way you'd hand-author prose. Before
writing any markup, **load the `artifact-design` skill** and follow its general
conventions for anything not spelled out below (this spec covers paper-gloss's
specific content; artifact-design covers general artifact hygiene).

### Document skeleton — construct-by-construct mapping

| eli5.md construct | HTML shape |
|---|---|
| Header block (title, authors, source, date, register note) | `<header class="doc-header">` at the top of `<body>`: `<h1>` for the title, a metadata block for authors/source/date, and a short note pointing at the Glossary panel — **not** a full term list (that's what the panel is for) |
| Section headings (any level) | Mapped 1:1 by depth to `<h1>`–`<h6>`, verbatim text, same order. **Excluded from term-wrapping.** |
| Paragraphs | One input paragraph → exactly one `<p>` — never merged or split |
| Lists | `<ul>`/`<ol>` + `<li>`, item-for-item |
| Equations | `<pre class="equation">` verbatim, inside `<div class="scroll-x">` (`overflow-x:auto`) — never re-typeset as math |
| Tables | Real `<table><thead>…<tbody>` markup, one input row/column → one output row/column, values unaltered, wrapped in `<div class="scroll-x">` |
| "In plain words: …" gloss lines | `<p class="plain-words"><em>In plain words:</em> …</p>`, distinct styling (italic + subtle left border/tint). **Included** in term-wrapping. |
| Bare `[Figure N]` placeholders | `<div class="figure-placeholder">[Figure N] — {rewritten caption}</div>`, dashed border / muted background so it visibly reads as a placeholder. Separator is a literal em dash. |
| Markdown figure images (`![Figure N](url)`) | **Download the asset and inline it as base64**, never downgrade it to a placeholder: `<figure class="paper-figure" id="figure-N"><img src="data:image/…;base64,…" alt="{caption}" loading="lazy"><figcaption>{caption}</figcaption></figure>`. **Excluded from term-wrapping** — captions are never glossed. |
| Inline citations (`[12]`, `(Smith et al., 2023)`) | Plain inline text, unchanged. **Never wrapped**, even if a term-like substring appears inside. |
| References section | Carried verbatim as extracted. **Excluded from term-wrapping** — same bucket as equations/tables/citations. |

### Term-wrapping mechanism

Give each approved term a stable kebab-case slug id (dedupe collisions with
`-2`, `-3`…). Embed one dictionary, once, in a `<script>` block:

```html
<script>
  const GLOSS_TERMS = {
    "stochastic-gradient-descent": {
      term: "stochastic gradient descent",
      expansion: "A method that nudges the model's settings using the error signal from a small random sample of training examples each step."
    }
    // one entry per approved term — single source of truth for both tooltips and the panel
  };
</script>
```

Every occurrence of an approved term **inside paragraphs, list items, and
plain-words lines** (never headings, equations, tables, figure placeholders,
figure captions, citations, or references) is wrapped as:

```html
<button type="button" class="gloss-term" data-term-id="stochastic-gradient-descent">stochastic gradient descent</button>
```

Use `<button>`, not `<span>` + `onclick` — it's keyboard-focusable for free.
Reset it in CSS to read inline (`display:inline; background:none; border:none;
padding:0; margin:0; font:inherit; color:inherit; cursor:pointer;`) so it never
breaks the paragraph's text flow.

**Hard constraints:**
- **Every occurrence** gets wrapped — not just the first per section or first in
  the document.
- **Longest-match-first, no overlap.** If one approved term is a substring of
  another (e.g. "gradient descent" inside "stochastic gradient descent"), match
  the longest one at each text position. Wrapped spans must never overlap or
  nest — HTML tags can't validly overlap.
- **No other edits.** The surrounding prose is never rewritten — only wrapped.
  This is strictly lower-risk than the old parenthetical version, which had to
  adjust wording so the inserted parenthetical read naturally; here nothing
  about the sentence changes, so that risk doesn't exist.
- **Escape literal `<`, `>`, `&`** in source prose as HTML entities before
  wrapping (papers can contain things like "a < b" or generic-type angle
  brackets) so the output stays well-formed.

### Visual cue

Terms get a dotted underline (`border-bottom: 1px dotted var(--gloss-underline)`)
plus a subtle color tint distinct from body text, with a light background
highlight on `:hover`/`:focus-visible`. This is a static always-visible cue, not
a hover-reveal — clicking/tapping is the only way to open the expansion.

### Popover

One singleton element in the DOM, not one per occurrence:

```html
<div id="gloss-popover" class="gloss-popover" role="tooltip" hidden>
  <button class="gloss-popover-close" aria-label="Close">×</button>
  <div class="gloss-popover-term"></div>
  <div class="gloss-popover-expansion"></div>
</div>
```

Wire it up with **one delegated listener** on `document` (`click`, checking
`event.target.closest('.gloss-term')`) — not a per-occurrence `onclick`, since a
paper can have hundreds of occurrences. On click:
1. Look up `data-term-id` in `GLOSS_TERMS`; fill in the popover's term + expansion.
2. Position via `getBoundingClientRect()` of the clicked button, clamped to the
   viewport width (never widen the page) with a flip-above rule near the bottom.
3. Only one popover open at a time — opening a new term repositions/repopulates
   the same singleton rather than spawning another.
4. Mark the active button (`aria-expanded="true"`, `.gloss-term--active`).
5. Dismiss via: the close button, clicking the same term again (toggle-close),
   clicking anywhere outside the popover and outside any `.gloss-term`, or
   `Escape`. All paths converge on one close function that also clears the
   active-button state.

### Full-glossary panel

A fixed toggle button, e.g.:

```html
<button id="gloss-panel-toggle" aria-expanded="false" aria-controls="gloss-panel">📖 Glossary (N)</button>
```

positioned `fixed; top/right` so it stays reachable while scrolling (N = approved
term count). Opens a slide-in drawer:

```html
<aside id="gloss-panel" class="gloss-panel" hidden>
  <button class="gloss-panel-close" aria-label="Close">×</button>
  <h2>Glossary</h2>
  <table>
    <thead><tr><th>Term</th><th>Plain-English expansion</th></tr></thead>
    <tbody id="gloss-panel-rows"></tbody>
  </table>
</aside>
```

Render the rows from the **same `GLOSS_TERMS` object** at load time (loop over
it) — never hand-duplicate the text — so the panel and the tooltips can't drift
out of sync. `width: min(420px, 90vw)`, full height, own `overflow-y:auto` (term
counts can run into the dozens). Backdrop overlay behind the drawer; the
backdrop, the close button, and `Escape` all close it. Opening the panel closes
any open term popover, and vice versa — only one interactive surface is ever
open at a time.

**Expose both close functions on `window`.** Assign the popover's and the
panel's close functions to `window.closeGlossPopover` and
`window.closeGlossPanel`. `/paper-figures` injects a figure lightbox into this
same page and calls them to enforce the one-surface-at-a-time rule; without the
assignments that coordination silently no-ops and a figure can open on top of a
live popover.

### Figures and the lightbox

Figures inlined from markdown images (the `.paper-figure` row above) are
click-to-zoom. Add one **singleton** `#figure-lightbox` overlay that reuses the
figure's existing data URI — never a second copy of the bytes — wired with a
single delegated listener, consistent with `.gloss-term`. It obeys the same
one-surface rule: opening it closes the popover and the panel; close button,
click-outside, and `Escape` all converge on one close function. Style
`.paper-figure`, its `<figcaption>`, and the overlay through the existing CSS
variables — no hardcoded colours, so both theme override layers keep working.

When `/paper-figures` runs as a retrofit it injects this markup, CSS, and
lightbox itself; a fresh `/paper-gloss` run that inlines a markdown image
produces the same shapes directly.

### Self-containment & theming

Everything — CSS and JS — inline in one `<style>` and one or two `<script>`
blocks in the single HTML file. No `<link>` to fonts/CDNs, no **external**
`src=`, no `@import`. **`data:` URIs are explicitly permitted** — that is how
figures are embedded while keeping the file self-contained; a blanket ban on
`https://` is what previously downgraded real figures to placeholders. Theme via
CSS variables in `:root` (light defaults), overridden in
`@media (prefers-color-scheme: dark)`, overridden again (must win) by
`:root[data-theme="dark"]` / `:root[data-theme="light"]`. Every color/spacing
value goes through a variable — never a hardcoded color — so both override
layers apply uniformly. Relative units throughout, a centered readable max-width
column (~760–880px); equations and tables are the only elements allowed to
scroll horizontally, in their own `.scroll-x` containers — the page itself must
never scroll sideways.

---

## Phase 3 — Verify

- **Occurrence coverage:** for each approved term, the count of exact-string
  occurrences in the source prose (paragraphs, list items, plain-words lines —
  excluding equations/tables/figure-placeholders/citations/references) equals
  the count of `.gloss-term` buttons with that `data-term-id` in the output.
- **No bare occurrences:** scan the output's text nodes for each approved term's
  exact string outside a `.gloss-term` wrapper — any hit must be fixed.
- **No overlap/nesting:** confirm longest-match precedence was applied; zero
  overlapping or nested `.gloss-term` spans.
- **Dictionary symmetry:** every `data-term-id` in the body resolves to a
  `GLOSS_TERMS` key, and every dictionary entry is used at least once in the
  body **and** appears as a row in the glossary panel.
- **Structure fidelity:** per-section `<p>` count == input paragraph count;
  heading text and order identical to the input.
- **Non-prose passthrough:** equations, tables, figure placeholders, figure
  captions, citations, and the references section contain zero
  `class="gloss-term"` occurrences, even where term text coincidentally appears
  inside.
- **Figures:** every markdown image in the input is present as
  `<figure class="paper-figure">` with a `data:` URI and a non-empty `alt` —
  zero downgraded to placeholders. If a lightbox is present, there is exactly
  one, and `window.closeGlossPopover` / `window.closeGlossPanel` are both
  assigned.
- **Well-formedness:** every tag closes; `<`/`>`/`&` in source prose are
  entity-escaped; exactly one `<html>`/`<head>`/`<body>`/`<title>`; doctype
  present.
- **Self-containment:** zero external *resource loads* —
  `grep -oE 'src="https?://' file`, `grep -oE '<link[^>]+href="https?://' file`,
  `grep -c '@import' file`, and `grep -oE 'url\(\s*["'"'"']?https?://' file` must
  all be zero. `data:` URIs are permitted and expected wherever figures are
  inlined. **Prose `<a href="https://…">` hyperlinks are permitted** — a link the
  reader clicks is not a resource the page fetches. Do **not** grep for a bare
  `https://`, and do **not** grep `href=` undifferentiated: captions, the source
  line, and reference entries legitimately contain URLs as text; the blanket
  `https://` rule is what caused real figures to be discarded, and an
  undifferentiated `href=` rule fails every paper that links to anything.
- **Theming completeness:** every variable referenced is defined in `:root`,
  the dark-media-query block, and both `data-theme` override blocks.
- **Artifact prerequisites:** non-empty `<title>` present.

Fix any discrepancy and re-verify before claiming done.

---

## Phase 4 — Deliver

- **Output path:** same directory as the input file, `<slug>-eli5-glossed.html`
  (same directory-resolution logic as before, new extension).
- Re-confirm the `artifact-design` skill was loaded before finalizing.
- **Git (when in a repo):** normal global workflow — feature branch, commit,
  push, PR, merge autonomously, brief Kyle — unless the project CLAUDE.md
  tightens it. Outside a repo: just write the file.
- **Publish via the `Artifact` tool:**
  - `title`: the paper's title, matching the HTML `<title>` tag.
  - `favicon`: one or two emoji — default to "📖" unless the paper's subject
    suggests a better fit.
  - `description`: 1–2 sentences, e.g. "Plain-English rewrite of {title} with N
    clickable glossary terms and a full glossary panel."
  - `file_path`: the finished HTML.
  - **Every run publishes a brand-new artifact** — a new paper each time, never
    a redeploy of a previous run's URL.
- **Send the file** to Kyle via SendUserFile.
- **Final report:** output path; PR link + merge confirmation; Artifact URL;
  number of approved terms + per-term occurrence tally; any flags (bare
  occurrences fixed, overlap conflicts resolved via longest-match, garbled or
  ambiguous regions); confirmation Phase 3 passed clean.

---

## Definition of done

The glossed HTML file exists at its output path with the header block, working
click-to-reveal tooltips on every occurrence of every approved term, and a
working full-glossary panel; Phase 3 passed clean (no bare or overlapping
terms, structure matches input, self-contained, themed for light and dark); the
git branch was committed, pushed, and merged via PR; the Artifact was published;
the file was sent via SendUserFile; the final report lists path, PR link,
Artifact URL, per-term tallies, and every flag.
