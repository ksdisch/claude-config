# paper-math — design spec

**Date:** 2026-07-28
**Status:** approved design, implemented in the same PR
**Deliverables:**
- one new reference at `skills/paper-gloss/references/math-rendering.md` (the contract)
- one new gate at `skills/paper-gloss/scripts/check_math.py` + `scripts/tests/test_check_math.py`
- amendments to `skills/paper-eli5/SKILL.md` (constraint 4, Phase 1 ledger, Phase 3, description)
- amendments to `skills/paper-gloss/SKILL.md` (construct table, term-wrapping, escaping,
  theming, Phase 3, Phase 4 report, RETROFIT mode, description)
- a one-block amendment to `skills/paper-figures/SKILL.md` (Phase 7 verify)
- updated rows in `docs/command-skill-reference.md`; the math clause of the
  `paper-eli5` design spec marked superseded

No new skill and no command wrapper. RETROFIT lives inside `/paper-gloss` because it
edits a page `/paper-gloss` authored, needs no source fetch, and downloads nothing —
a fourth family member would duplicate the whole delivery apparatus to carry one pass.

## Purpose

The pipeline shipped raw LaTeX to readers. In the published rewrite of Anthropic's
global-workspace paper, §2.3 reads:

> there are `$n_{\text{vocab}}$` vectors … and `$n_{\text{vocab}} > d_{\text{model}}$`

where the source renders *n*<sub>vocab</sub> and *d*<sub>model</sub> as typeset
notation. Six expressions in that one section alone.

## Motivating findings

1. **It is a gap, not a bug.** `paper-gloss`'s construct-mapping table had rows for
   headings, paragraphs, lists, equations, tables, plain-words lines, figures,
   citations, and references — and **no row for inline math**. Inline math fell
   through to "Paragraphs → one `<p>`, verbatim", which is exactly what happened.
2. **Display math was a deliberate decision, now reversed.** The old equations row
   said `<pre class="equation">` "never re-typeset as math", backed by an explicit
   YAGNI in the `paper-eli5` design spec: "no re-deriving or reformatting of math."
   Reformatting is now in scope; re-deriving still isn't.
3. **Nothing could catch it.** Neither skill's verify phase looked for residual TeX,
   so the defect was invisible to every gate the family already runs.
4. **Self-containment forbids the usual answer.** No CDN, no external `src=`, no
   `@import` rules out loading KaTeX or MathJax the ordinary way. It does not rule
   out rendering math — only rendering it with someone else's JavaScript.

## Approach — a three-tier ladder

Rejected: **inlined self-hosted KaTeX** (~600–800KB of JS, CSS, and base64 woff2 per
page against a 6MB budget already shared with figures, plus a third-party blob and a
font-URL rewrite step in a prose-only repo) and **screenshotting equations** off the
source like figures (perfect fidelity, but images don't respect the artifact's dark
theme, don't reflow, aren't selectable, and only work for web sources).

Chosen: markup the browser already knows.

| Tier | Form | When |
|---|---|---|
| 1 | unicode + `<i>`/`<sub>`/`<sup>` in `<span class="math">` | all inline math, and any linear display equation |
| 2 | native `<math display="block">` MathML | fractions, sums/integrals with limits, matrices, roots |
| 3 | `<pre class="equation" data-math-verbatim="1">` verbatim, named in the report | faithful typesetting isn't possible |

Both rendering tiers cost zero bytes of asset, need no script or webfont, and inherit
`currentColor` — so they theme for free in light and dark. Tier 3 is constraint 5
("NEVER INVENT") applied to math: a reader can still read TeX, but cannot detect a
subscript that moved.

## The contract, and why it is one file

Math gets the same **producer/consumer markup contract** figures already have
(`[Figure N]` → `ledger.py` → `inject.py`): `/paper-eli5` normalizes every expression
to canonical `$…$` / `$$…$$` in the markdown — where TeX is *correct*, since GitHub
renders it — `/paper-gloss` typesets it, `/paper-figures` must not regress it, and
counts reconcile at every hop.

The contract lives in exactly one file, cited by both consumers. The self-containment
grep suite is already copy-pasted verbatim between `paper-gloss/SKILL.md` and
`paper-figures/SKILL.md`; a second instance of that mistake was not worth making.

### Two collisions the contract has to resolve

- **Escaping.** `paper-gloss` requires literal `<`, `>`, `&` in source prose to be
  entity-escaped. Math spans are authored markup — their tags are emitted live, while
  `<`/`>`/`&` *inside* math content is escaped.
- **Term-wrapping.** `$d_{\text{model}}$` typesets to `<sub>model</sub>`. If "model"
  is an approved gloss term, a naive wrapper puts a `<button>` inside a subscript,
  breaking the notation and inflating that term's tally past its prose count. `.math`
  and `<math>` join the never-wrap bucket.

## The gate

`check_math.py` blanks non-prose regions with equal-length whitespace (so line numbers
stay true), strips tags, then runs overlapping detectors and merges their spans — one
missed variable reports as one hit, not as the four regexes it tripped.

Two calibration decisions, both taken from how the bug shipped:

- **A bare `$` is never a hit.** Papers say "$5M in compute". An inline pair is only
  credited when no whitespace sits just inside either delimiter, which is what rejects
  "we spent $5M and $8M". A gate that cries wolf gets ignored, and an ignored gate is
  how this reached a reader.
- **A `<pre class="equation">` without `data-math-verbatim="1"` IS scanned.** The
  attribute marks a deliberate, reported Tier 3 fallback; its absence marks an
  equation nobody triaged. Exempting every `<pre>` would have let the exact construct
  the gate exists for pass silently.

The reported count is `len(hits)` — never a figure declared upfront. `inject.py:60`
already prints a manifest count instead of what it did (`BACKLOG.md:15`), and that
habit was not worth inheriting.

## RETROFIT mode

`/paper-gloss --retrofit <glossed.html> [artifact-url]`. Enumerate with the gate,
convert only the math spans, re-verify, then republish with `Artifact(url=…)` to the
**same URL** — the stated carve-out from "every run publishes a brand-new artifact",
which otherwise orphans the link Kyle already has.

The re-verify additionally pins two counts as unchanged: `<p>` elements and the
per-`data-term-id` `.gloss-term` tally. A math conversion that moves either has
touched prose it had no business touching — and the failure mode there is a term
swallowed into a subscript, which reads as a clean run because the page still parses.

The eli5 markdown is not rewritten by a retrofit; its `$…$` is already correct.

## Out of scope (YAGNI)

No LaTeX→HTML converter library or vendored engine — the ladder is authored by hand,
the same way the rest of the page is. No math in the `paper-eli5` markdown beyond
delimiter normalization. No PDF-source equation capture. `check_math.py` is HTML-only:
in markdown, TeX is the correct form, so scanning it there would flag every span.

## Definition of done

The contract file, the gate, and its tests exist; all three SKILL.md files carry their
amendments; `check_math.py` exits clean on a page rendered per the ladder and non-zero
on the §2.3 text that motivated this; both test suites pass; the reference index and
the superseded YAGNI clause are updated in the same commit.
