---
name: paper-gloss
description: Post-process a paper-eli5 output into a self-contained, interactive HTML page where every occurrence of selected jargon terms is clickable — clicking reveals a plain-English expansion in a popup — plus a toggle-able glossary panel listing every approved term at once. AI proposes the candidate term list with expansions; you trim it; the skill hand-authors a themed, responsive HTML artifact mirroring the eli5 document 1:1. Equations and inline math are typeset as real notation (unicode + HTML, native MathML where 2D layout is needed) rather than shipped as raw LaTeX, gated by a residual-TeX check; each display equation's "named form" — the same equation with variables replaced by what they are, plus a `where:` legend — renders as a grouped block between the equation and its plain-words gloss. Delivers a `-glossed.html` file (via the repo's git workflow) and a published claude.ai Artifact link. Every page carries an annotation layer — select text to highlight it, attach notes, and export to Obsidian-ready Markdown or re-importable JSON (localStorage-persistent per browser; export is the durability guarantee). An `--annotate` mode injects the layer into an already-published page and redeploys it to the same Artifact URL. Run after /paper-eli5 when specific terms are still opaque after the first rewrite. A `--retrofit` mode typesets math in an already-published page and redeploys it to the same Artifact URL.
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
- **`--retrofit <glossed.html> [artifact-url]`** → skip Phases 1–2 and run
  RETROFIT mode (below): typeset math in an already-published page and redeploy
  it to the same Artifact URL.
- **`--annotate <glossed.html> [artifact-url]`** → skip Phases 1–2 and run
  ANNOTATE mode (below): inject the annotation layer into an already-published
  page and redeploy it to the same Artifact URL.
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

If the document contains any math — inline or display — **also load
`references/math-rendering.md`**. It holds the conversion ladder, the symbol
table, and the two rules where math collides with the escaping and term-wrapping
rules below. It is the single copy of that contract; `/paper-figures` cites the
same file rather than carrying its own.

### Document skeleton — construct-by-construct mapping

| eli5.md construct | HTML shape |
|---|---|
| Header block (title, authors, source, date, register note) | `<header class="doc-header">` at the top of `<body>`: `<h1>` for the title, a metadata block for authors/source/date, and a short note pointing at the Glossary panel — **not** a full term list (that's what the panel is for) |
| Section headings (any level) | Mapped 1:1 by depth to `<h1>`–`<h6>`, verbatim text, same order. **Excluded from term-wrapping.** |
| Paragraphs | One input paragraph → exactly one `<p>` — never merged or split |
| Lists | `<ul>`/`<ol>` + `<li>`, item-for-item |
| Inline math (`$…$` in a sentence) | Typeset per the ladder in `references/math-rendering.md` — Tier 1 unicode + `<i>`/`<sub>`/`<sup>` inside `<span class="math">`. **Never left as literal TeX**, which is what put `$n_{\text{vocab}}$` in front of a reader. **Excluded from term-wrapping.** |
| Display equations (`$$…$$`, or an equation line) | Same ladder: Tier 1 if the expression is linear, Tier 2 `<math display="block">` when it needs 2D layout (fractions, sums with limits, matrices), Tier 3 `<pre class="equation" data-math-verbatim="1">` verbatim only when faithful typesetting isn't possible — and then counted in the final report. Any tier stays inside `<div class="scroll-x">` (`overflow-x:auto`). **Excluded from term-wrapping.** |
| Tables | Real `<table><thead>…<tbody>` markup, one input row/column → one output row/column, values unaltered, wrapped in `<div class="scroll-x">` |
| Named-form block (`*Named form:*` + `$$…$$` + a `*where:*` list) | One `<div class="named-form">` holding all three parts — see "The named-form block" below. The equation typesets by the same ladder as any display equation; the legend becomes a `<dl>`. **Split bucket** for term-wrapping: the equation and the legend's symbols are math (never wrapped), the legend's descriptions are prose (**included**). |
| "In plain words: …" gloss lines | `<p class="plain-words"><em>In plain words:</em> …</p>`, distinct styling (italic + subtle left border/tint). **Included** in term-wrapping. |
| Bare `[Figure N]` placeholders | `<div class="figure-placeholder">[Figure N] — {rewritten caption}</div>`, dashed border / muted background so it visibly reads as a placeholder. Separator is a literal em dash. |
| Markdown figure images (`![Figure N](url)`) | **Download the asset and inline it as base64**, never downgrade it to a placeholder: `<figure class="paper-figure" id="figure-N"><img src="data:image/…;base64,…" alt="{caption}" loading="lazy"><figcaption>{caption}</figcaption></figure>`. **Excluded from term-wrapping** — captions are never glossed. |
| Inline citations (`[12]`, `(Smith et al., 2023)`) | Plain inline text, unchanged. **Never wrapped**, even if a term-like substring appears inside. |
| References section | Carried verbatim as extracted. **Excluded from term-wrapping** — same bucket as equations/tables/citations. |

### The named-form block

`/paper-eli5` emits every display equation as three parts — the equation, a
**named form** (the same equation with each variable replaced by what it is, plus
a `where:` legend), then the plain-words line. The named form's job is to let a
reader who can't remember what *d*<sub>k</sub> stands for read the meaning
straight off the notation, so it must sit visually *between* the equation and the
prose, grouped with the equation rather than floating as loose paragraphs:

```html
<div class="named-form">
  <div class="named-form-label">Named form</div>
  <div class="scroll-x">
    <math display="block"> … </math>
  </div>
  <dl class="named-form-legend">
    <dt><span class="math"><i>Q</i></span></dt>
    <dd>the queries: what each token is looking for</dd>
    <dt><span class="math"><i>d</i><sub>k</sub></span></dt>
    <dd>the size of each key vector</dd>
  </dl>
</div>
```

- **The named-form equation typesets by the normal ladder** in
  `references/math-rendering.md` — Tier 1 if linear, Tier 2 MathML when it needs
  2-D layout, Tier 3 only as an honest fallback. It is ordinary `$$…$$` in the
  markdown, so no new math machinery exists for it and `check_math.py` guards it
  automatically. Words inside `\text{…}` are **upright** (`<mtext>` in MathML, no
  `<i>` in Tier 1) — that upright/italic contrast is what tells a reader at a
  glance which line is symbols and which is names.
- **It always keeps its own `.scroll-x` wrapper.** A named form is wider than the
  equation it mirrors — words are longer than letters — so it is the single most
  likely element on the page to overflow. Without the wrapper it is what makes
  the body scroll sideways.
- **Styling** groups the three parts as one unit: a shared subtle background or
  left border spanning the equation and the named form, a small uppercase
  `.named-form-label`, and a `<dl>` laid out with `<dt>` and `<dd>` on one line
  each (grid or `float`-free flex; never rely on default `<dd>` indentation
  alone). Every value through an existing CSS variable, like everything else.
- **Term-wrapping is split across this block**, and the split is not cosmetic:
  - The named-form **equation** is math — `.math` spans and `<math>` elements are
    in the never-wrap bucket, and that applies here in full. Its words live
    inside `<mtext>`/upright spans; injecting a `<button class="gloss-term">`
    there breaks the notation and inflates the term's occurrence tally exactly
    the way wrapping `<sub>model</sub>` does. It is tempting to make an exception
    *because* this line is made of words — don't; the words are notation here.
  - Legend `<dt>` contents are math too, and are never wrapped.
  - Legend `<dd>` descriptions are ordinary prose and **are** wrapped, on the
    same footing as a plain-words line. This is where a reader gets the clickable
    expansion, and it is the reason the split is worth the complexity.

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

Every occurrence of an approved term **inside paragraphs, list items,
plain-words lines, and named-form legend descriptions (`<dd>`)** (never
headings, equations, `.math` spans, `<math>` elements, named-form equations or
their legend `<dt>` symbols, tables, figure placeholders, figure captions,
citations, or references) is wrapped as:

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
  brackets) so the output stays well-formed. This is a rule about **prose
  text**: math spans are authored markup, so `<span class="math">`, `<i>`,
  `<sub>`, `<sup>`, `<math>` and its children are emitted as live tags, while
  any `<`/`>`/`&` *inside* math content is escaped.
- **Never wrap a term inside math.** `$d_{\text{model}}$` typesets to
  `<sub>model</sub>`; if "model" is an approved term, a naive wrapper puts a
  `<button>` inside a subscript — breaking the notation and inflating that
  term's occurrence tally past its prose count.

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
<div id="gloss-backdrop" class="gloss-backdrop" hidden></div>
<aside id="gloss-panel" class="gloss-panel" hidden>
  <button class="gloss-panel-close" aria-label="Close">×</button>
  <h2>Glossary</h2>
  <table>
    <thead><tr><th>Term</th><th>Plain-English expansion</th></tr></thead>
    <tbody id="gloss-panel-rows"></tbody>
  </table>
</aside>
```

The backdrop **must carry `id="gloss-backdrop"`** (and the matching class). It is
part of the page's public markup contract, not an internal detail: `/paper-figures`
hides it by id when it opens a figure lightbox on a page that predates the
`window.close*` exports below. An unnamed backdrop leaves a full-screen fixed
overlay stranded over the artifact with its close button already hidden.

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

Math costs nothing here: Tier 1 is plain `<i>`/`<sub>`/`<sup>` and Tier 2 MathML
is native to the browser, so neither needs a script, a webfont, or a `data:`
URI, and both inherit `currentColor` and theme for free. Add the small
`.math` / `sub` / `sup` / `math` rules from `references/math-rendering.md` to the
same inline `<style>` — the `line-height: 0` on `sub`/`sup` is load-bearing, or
every paragraph containing a subscript develops uneven leading.

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

---

## Phase 3 — Verify

- **Occurrence coverage:** for each approved term, the count of exact-string
  occurrences in the source prose (paragraphs, list items, plain-words lines,
  named-form legend descriptions — excluding
  equations/tables/figure-placeholders/citations/references **and any
  `$…$` math span, which typesets to `.math`/`<math>` and is never wrapped**)
  equals the count of `.gloss-term` buttons with that `data-term-id` in the
  output.
- **No bare occurrences:** scan the output's text nodes for each approved term's
  exact string outside a `.gloss-term` wrapper — any hit must be fixed, **except
  inside a `.math` span or a `<math>` element, where a bare occurrence is the
  required outcome**: `$d_{\text{model}}$` puts the literal text `model` in a
  `<sub>`, and wrapping it is what the never-wrap rule forbids. Exclude those
  subtrees before scanning; do not "fix" them.
- **No overlap/nesting:** confirm longest-match precedence was applied; zero
  overlapping or nested `.gloss-term` spans.
- **Dictionary symmetry:** every `data-term-id` in the body resolves to a
  `GLOSS_TERMS` key, and every dictionary entry is used at least once in the
  body **and** appears as a row in the glossary panel.
- **Structure fidelity:** per-section `<p>` count == input paragraph count
  **minus the input paragraphs that map to something other than a `<p>`** — the
  `*Named form:*` and `*where:*` marker lines (two per named form) and bare
  `[Figure N]` placeholders. Counting them makes a paper with N display
  equations miss by 2N, every time. **Subtract on the input side; there is no
  sum over output elements that works.** `*Named form:*` becomes the
  `.named-form-label` and `[Figure N]` becomes a `.figure-placeholder`, but
  `*where:*` leaves **no** output element at all — the `<dl>` renders the
  legend's markdown *list items*, not the marker line — so any additive
  restatement silently under-counts by one per named form, which is the same
  false failure this exclusion exists to prevent. Heading text and order
  identical to the input.
- **Non-prose passthrough:** equations, `.math` spans, `<math>` elements,
  named-form equations and their legend `<dt>` symbols, tables, figure
  placeholders, figure captions, citations, and the references section contain
  zero `class="gloss-term"` occurrences, even where term text coincidentally
  appears inside. The named-form equation is the new trap here: it reads as
  words, so a wrapper that decides by appearance rather than by container will
  wrap it.
- **Named forms carried 1:1:** the count of `.named-form` blocks equals the
  count of `*Named form:*` markers in the input markdown, each sits between its
  equation and that equation's plain-words line, and each `<dl>` has one `<dd>`
  per `<dt>` matching its `*where:*` list item-for-item. A named form that lost
  its legend, or a legend row that lost its symbol, fails here.
- **Math rendered:** `python3 scripts/check_math.py <file.html>` exits clean.
  Every hit it prints is TeX a reader would have seen. A `<pre class="equation">`
  with no `data-math-verbatim="1"` is an equation nobody triaged, and the gate
  fails on it deliberately — mark it Tier 3 or typeset it, but don't leave it
  undecided.
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
- **Annotation layer present and idempotent:**
  `python3 scripts/inject_annotations.py --check <file.html>` exits clean, and
  a second injector run leaves the file byte-identical (`md5` before == after).
- **Annotation layer is inert to every check above:** block-marker stamping
  and the two sentinel blocks add zero `<p>` elements, zero `.gloss-term`
  buttons, and no external loads — if any earlier bullet moved after
  injection, the injector touched something it must not.

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
  - `capabilities: {downloads: true}` — the annotation layer's export buttons
    call `window.claude.downloads.save()`; without the declaration they fall
    back to copy-to-clipboard even on claude.ai.
  - **Every run publishes a brand-new artifact** — a new paper each time, never
    a redeploy of a previous run's URL. The exceptions are RETROFIT and ANNOTATE
    modes below, both of which exist precisely to update a page in place.
- **Send the file** to Kyle via SendUserFile.
- **Final report:** output path; PR link + merge confirmation; Artifact URL;
  number of approved terms + per-term occurrence tally; **math counts — spans
  typeset at Tier 1, blocks at Tier 2, and every Tier 3 verbatim fallback named
  with the reason it couldn't be typeset**; named-form block count and how it
  reconciles against the input's display equations; any flags (bare occurrences fixed,
  overlap conflicts resolved via longest-match, garbled or ambiguous regions);
  confirmation Phase 3 passed clean.

---

## RETROFIT mode — repair math in an already-published page

For a glossed page that shipped before this contract existed, or one whose math
was left at Tier 3 and can now be typeset. It does **not** re-read the source
paper, re-propose terms, or re-run Phase 1 — it edits math and nothing else.

**Trigger:** `--retrofit <glossed.html> [artifact-url]`, or Kyle asking to fix
the math in an existing paper page.

1. **Enumerate, and capture the baseline before touching anything.**
   `python3 scripts/check_math.py <file.html> -o /tmp/math.json`.
   Read **both** counters in the payload: `found` is untypeset TeX, and
   `verbatim_blocks` is deliberate Tier 3. The gate blanks every
   `data-math-verbatim="1"` region before scanning, so a page whose math is
   entirely correct Tier 3 reports `found: 0` — the hit list alone cannot see
   the second population this mode exists for. Stop only when **both** are
   zero; that is the one case where there is nothing to do.

   Whenever `verbatim_blocks > 0`, re-examine every marked block against the
   ladder and promote the ones Tier 1 or Tier 2 can now express faithfully,
   leaving the rest marked and reported. This is **independent of the hit
   count** — a mixed page has both populations, and gating the promotion on
   `found: 0` would silently skip the Tier 3 half.

   Then, still before the first edit, record three numbers. Step 3 compares
   against them, and once step 2 has rewritten the file they are gone:
   - the count of `<p>` elements;
   - the `.gloss-term` tally **per `data-term-id`**, not just the total;
   - the `.gloss-term` buttons that sit inside a `$…$` run or an existing
     `.math` / `<math>` element, also per `data-term-id`. On a pre-contract
     page this is usually zero or one, but it is the number that makes a
     legitimate drop in step 3 distinguishable from damage.
2. **Convert.** Run the mechanical pass first, then hand-author what it
   refuses:

   ```bash
   python3 scripts/convert_math.py <file.html>            # dry run: see the worklist
   python3 scripts/convert_math.py <file.html> --apply
   ```

   It reports **three** outcomes, and only the first two are symmetric:

   - **converted** — unambiguous Tier 1, done for you;
   - **refused** — your hand-authoring worklist. The tool exits non-zero while
     any remain, so a partial pass cannot be mistaken for a finished one. Work
     it by the ladder: Tier 1 for anything linear, Tier 2 native MathML inside
     the existing `<div class="scroll-x">` for genuine 2-D layout, Tier 3 only
     where faithful typesetting is impossible.

     **One sub-list is printed apart and the ladder does not apply to it
     unqualified: `ambiguous` bare amounts** like `$100$`. A tool cannot tell a
     price from a lone constant, so it refuses rather than guessing. If the
     span is notation, typeset it by the ladder as usual. If it is money,
     **escape both delimiters as `&#36;`** — the page still reads `$100$`, and
     that is what clears the entry. Typesetting a price by the ladder deletes
     both `$` and invents math; leaving it raw makes it recur on every run.
   - **skipped** — spans read as money rather than notation (`$5-$10`). These
     are *not* work, and are deliberately **not** in the exit code, because
     filing a price under "typeset this by the ladder" invites you to mangle
     it by hand. **Read the list anyway.** It is the one bucket with no
     downstream detector: `check_math.py` cannot see these either, so anything
     here that really is notation will never be mentioned by either tool
     again. It is short by design — if it is long, something is miscalibrated.

   Three things the converter deliberately leaves to the *refused* pile rather
   than deciding alone, because each changes the page in a way a tool should
   not choose: a span containing a `.gloss-term` button (removing that button
   is the accounted decrease in step 3), every `$$…$$` display block, and every
   bare amount, per the escape rule above.

   Replace **only** the math span itself and never the surrounding prose —
   same discipline as `paper-figures`' `inject.py`, which rewrites the
   placeholder line and leaves every other byte alone so the structural verify
   still holds afterwards.
3. **Re-verify.** Run the Phase 3 bullets that are defined against the output
   alone: *No bare occurrences* (the approved term list is the page's own
   embedded `GLOSS_TERMS`), *No overlap/nesting*, *Dictionary symmetry*,
   *Non-prose passthrough*, *Math rendered*, *Well-formedness*,
   *Self-containment*, *Theming completeness*, *Artifact prerequisites*, and
   the lightbox half of *Figures*. *Theming completeness* earns its place here:
   injecting the math CSS is the retrofit's own edit, so this run is the one
   most likely to reference a variable defined in `:root` but missing from the
   dark block or a `data-theme` override.

   The input-comparative bullets are **out of scope and must not be claimed** —
   *Occurrence coverage*, *Structure fidelity*, and the "every markdown image in
   the input" half of *Figures* all compare against an `-eli5.md` that a
   retrofit never loads. Say so in the report rather than reporting a full
   Phase 3 pass.

   In their place, check step 1's baseline. These are the retrofit's substitute
   for structure fidelity and occurrence coverage: a conversion that moves them
   has touched prose it had no business touching — the failure mode is a term
   swallowed into a subscript, which reads as a clean run because the page
   still parses.

   - **`<p>` elements: exactly unchanged.** No math conversion adds or removes
     a paragraph.
   - **`.gloss-term` tally, compared per `data-term-id`: may only *decrease*,
     and only for the terms you deliberately freed.** Compare term by term —
     an aggregate total hides the case that matters, where one term wrongly
     loses an occurrence while another wrongly gains one and the sum still
     balances. It cannot be pinned equal either, because a pre-contract page
     was built when *No bare occurrences* had no math carve-out, so the wrapper
     was **required** to wrap terms it found inside `$…$`. Those buttons are
     the `<button>`-inside-`<sub>` artifact this contract exists to kill, and
     *Non-prose passthrough* requires removing them.

     The legitimate drop for a term is the number of its buttons **you removed
     while hand-authoring a span in step 2** — a number you know exactly,
     because the converter refuses those spans rather than touching them.
     Cross-check it against step 1's third count, and expect a difference only
     where a math region was left unconverted (its button survives, correctly).
     Any other movement — an increase, a decrease on a term you did not touch,
     or a drop larger than what you removed — is the real defect signal.
   - **A term that loses *every* occurrence keeps its glossary row.** If all of
     a term's occurrences sat inside math, freeing them takes its body count to
     zero, and *Dictionary symmetry*'s "used at least once in the body" half
     does **not** apply to it in a retrofit — re-wrapping is forbidden by the
     never-wrap rule and deleting the `GLOSS_TERMS` entry is prose surgery this
     mode forbids. Leave the row, and name the term in the step 6 report so the
     now-unreachable entry is a stated outcome rather than a silent one.
4. **Republish in place:** `Artifact(url=<existing-url>, file_path=…)` with the
   same title and favicon. This is the stated carve-out from "every run
   publishes a brand-new artifact" — the whole point is that Kyle's existing
   link keeps working. Without a URL, ask for it rather than minting a new one
   and orphaning the old.
5. **Git:** normal workflow — branch, commit, push, PR, merge, brief Kyle.
6. **Report:** hits found; spans typeset per tier, split into what the
   converter did mechanically and what you hand-authored; remaining Tier 3
   fallbacks; the unchanged `<p>` count; the per-term tally with every drop
   named — which `data-term-id`s lost occurrences, how many, and any term now
   at zero body occurrences but still in the glossary; and the Artifact URL you
   redeployed to.

The eli5 markdown is **not** rewritten by a retrofit. Its `$…$` is already the
canonical form and is correct where it lives.

**A retrofit never generates named forms.** It works on published HTML without
the source paper, so it has no way to learn what a symbol stands for; producing
one would be inventing meanings, which `paper-eli5` constraint 5 forbids and
which no downstream check could catch — a plausible wrong definition reads
exactly like a right one. A page that predates this construct stays without it;
say so in the report. Named forms already on the page are typeset like any other
math, and for step 3's *Non-prose passthrough* the never-wrap containers are the
named-form **equation and its legend `<dt>` symbols** — not `.named-form` as a
whole. A page built under this contract legitimately carries `.gloss-term`
buttons inside `.named-form > dl > dd`; treating the block as one never-wrap
container either false-fails the check or strips real buttons, and stripping
them then trips the per-`data-term-id` tally rule, which permits a decrease only
for terms deliberately freed while hand-authoring a math span. Adding named
forms to an existing page means re-running
`/paper-eli5` against the paper, not retrofitting.

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

---

## Definition of done

The glossed HTML file exists at its output path with the header block, working
click-to-reveal tooltips on every occurrence of every approved term, and a
working full-glossary panel; Phase 3 passed clean (no bare or overlapping
terms, structure matches input, self-contained, themed for light and dark,
named forms carried 1:1 with their legends intact,
`check_math.py` clean with every Tier 3 fallback named in the report); the
git branch was committed, pushed, and merged via PR; the Artifact was published;
the file was sent via SendUserFile; the final report lists path, PR link,
Artifact URL, per-term tallies, and every flag.

For a **RETROFIT** run, substitute its own step 3: the output-only Phase 3
bullets passed, the input-comparative ones were declared out of scope rather
than claimed, the `<p>` count came back unchanged, and the per-term tally either
held or fell by exactly the reported count of buttons freed from math. Everything
else on this list still holds, and the Artifact was redeployed to the existing
URL rather than published fresh.
