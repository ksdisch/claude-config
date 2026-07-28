---
name: paper-eli5
description: Rewrite someone else's research paper into plain English — section by section, paragraph by paragraph, 1:1. Same headings, same paragraph order; nothing summarized, merged, dropped, or reordered; only the language changes (smart-newcomer register, jargon translated on first use). Accepts a local PDF/markdown/text path, an arXiv URL or bare ID, or any other web URL. Equations, tables, and inline math stay verbatim with an "in plain words" gloss, and every display equation also gets a "named form" — the same equation re-emitted with each variable replaced by what it actually is, plus a `where:` legend — with math normalized to canonical `$…$` / `$$…$$` so `/paper-gloss` can typeset it; figures become placeholders with rewritten captions; the references section passes through untouched. Output lands in the current repo at docs/papers/<slug>-eli5.md (papers/ if no docs/; beside the input outside a repo) and is sent to Kyle. Use whenever Kyle types /paper-eli5, or says "eli5 this paper", "simplify this paper", "plain-English this paper", "make this paper readable", "translate this paper for a layman" — even if he doesn't name the skill. NOT for writing up Kyle's own finished projects (research-paper) and NOT for choosing the next project (seed-hunt). Works interactively or unattended; after the input paper is known it runs end-to-end.
---

# Paper ELI5 — a plain-English rewrite that mirrors the paper 1:1

Take a research paper written for field experts and produce a full rewrite a smart
newcomer can read — same sections, same paragraphs, same order. This is a
translation, not a summary and not a review. The enemy is **summarization drift**:
long rewrites quietly start merging and dropping paragraphs. The skeleton ledger
below exists to make that impossible.

Lineage note: this is the read-someone-else's-paper aid. NOT `/research-paper`
(writes up Kyle's own finished projects) and NOT `/seed-hunt` (picks the next
project). The name `paper-companion` stays reserved for a possible future
interactive companion. After the input paper is known there are no stops; when
running unattended, the global unattended rules apply.

## Parse `$ARGUMENTS`

- **Local path** ending `.pdf` / `.md` / `.txt` → the paper. Read PDFs via the Read
  tool in ≤20-page chunks.
- **arXiv URL or bare ID** (e.g. `2402.01234`, an `arxiv.org/abs/…` link) →
  normalize to `arxiv.org/pdf/<id>`, download to `/tmp` (never commit a PDF into a
  repo), read as PDF.
- **Any other URL** → fetch clean markdown via the `obsidian:defuddle` skill;
  fall back to WebFetch.
- **Remaining words** are operator notes: register tweaks ("even simpler"), an
  output path override, emphasis. Notes never override the Hard constraints.
- **No argument** → ask which paper. Unattended with no or ambiguous input →
  report the ambiguity as the outcome; don't guess.

## Hard constraints (non-negotiable, in force through every phase)

1. **STRUCTURE IS SACRED.** Same heading hierarchy, headings verbatim (an opaque
   heading may get a short parenthetical gloss). One original paragraph → one
   rewritten paragraph, same order — never merged, split, dropped, or reordered.
   Abstract counts as a section; appendices are included. Lists stay lists,
   item-for-item; footnotes stay in place.
2. **TRANSLATE, DON'T EDIT.** No added opinions, commentary, fact-checking, or
   claims. Numbers, results, and claims are stated exactly as the paper states
   them; an analogy must never shift a claim's meaning or strength. Ambiguous
   passages get a conservative, close-to-literal rendering — never a guess dressed
   as a simplification.
3. **CARRY EVERYTHING.** All of a paragraph's information survives — simpler
   wording, not less content. Sentence count may change; paragraph count may not.
4. **NON-PROSE PASSES THROUGH.** Equations and tables verbatim in place. A table
   is immediately followed by an italic *"In plain words: …"* line and its values
   are never altered; a **display** equation ships as the three-part block of
   Phase 2 — verbatim equation, then the named form and its legend, then the
   *"In plain words: …"* line. **Math is non-prose too — including inline math inside a
   sentence.** Every expression is normalized to one canonical grammar, `$…$`
   inline and `$$…$$` display, whatever the source used (`\(…\)`, `\[…\]`, a
   KaTeX annotation, a PDF's extracted glyphs). TeX is correct in this markdown —
   GitHub renders it, and it is the stable grammar `/paper-gloss` consumes to
   typeset the HTML, exactly as `[Figure N]` is the grammar `/paper-figures`
   consumes. A variable is never left as bare prose characters, and notation the
   source didn't have is never invented. Figure images can't be carried from a
   PDF: a `[Figure N]` placeholder holds the spot and the caption is rewritten
   (markdown/HTML inputs keep their image references). Inline citation markers
   (`[12]`, `(Smith et al., 2023)`) stay exactly where they are; the references
   section is carried verbatim as extracted — never rewritten, never pruned.
5. **NEVER INVENT.** Garbled or unreadable regions are flagged in the final
   report, not filled in.

## Phase 1 — Map (before writing a word)

Ingest the whole paper first. Build two internal working artifacts (never shipped):

1. **Skeleton ledger** — every heading verbatim, in order; per section: paragraph
   count plus counts of equations, tables, figures, and math spans (inline and
   display tallied separately — inline math is the one that silently evaporates,
   because unlike an equation it has no line of its own to go missing). These are
   counts of what the **source** contains; the rewrite also authors math of its
   own (Phase 2's named forms), which Phase 3 reconciles separately.
2. **Glossary** — every field-jargon term and acronym mapped to ONE chosen
   plain-English rendering, decided here and used consistently in every section.

PDF extraction garbles paragraph boundaries (two-column layouts, hyphenation).
Reconstruct true paragraph boundaries by judgment and build the ledger from that
reconstruction — Phase 3 verifies the output against this same baseline, so the
check stays self-consistent.

## Phase 2 — Rewrite (section by section, append as you go)

Work through sections in ledger order. Append each finished section to the output
file and check it off — the file is the accumulator; don't hold the whole rewrite
in memory.

- **Register:** smart-newcomer plain English. First use of a term = plain phrase
  with the original term in parentheses (the reader still learns the field's
  vocabulary); subsequent uses follow the glossary. Analogies only where they
  genuinely help — and never where they'd bend a claim (constraint 2).
- **Header block** first, at the top of the file: paper title, authors, source
  (link or path), generation date, and one line noting this is a plain-English
  rewrite mirroring the original structure 1:1, with equations and tables carried
  verbatim and each display equation followed by a named form and a plain-words
  gloss.

### Display equations — the three-part block

A display equation (`$$…$$` on its own line) ships as three parts, in this order,
with nothing between them:

1. **The equation, verbatim** — canonical `$$…$$`, per constraint 4.
2. **The named form** — the same equation re-emitted with every variable replaced
   by what it actually *is*, followed by a `where:` legend. This is the part a
   reader who can't hold "what was $d_k$ again?" in their head reads instead.
3. **The gloss** — the italic *"In plain words: …"* prose line.

The grammar is fixed, because it is the contract `/paper-gloss` consumes to
typeset the block — exactly as `$$…$$` is the grammar it consumes for math and
`[Figure N]` is the one `/paper-figures` consumes for figures:

```markdown
$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

*Named form:*

$$\text{attention output} = \text{softmax}\!\left(\frac{\text{queries} \times \text{keys}^\top}{\sqrt{\text{key dimension}}}\right) \times \text{values}$$

*where:*
- $Q$ — the queries: what each token is looking for
- $K$ — the keys: what each token offers
- $V$ — the values: what each token carries
- $d_k$ — the size of each key vector

*In plain words: each token scores how relevant every other token is to it, then
blends the others' values in proportion to those scores.*
```

Rules for the named form:

- **It is real TeX**, in the same canonical `$$…$$` grammar as the equation above
  it, with words wrapped in `\text{…}` so they typeset upright. A plain-text line
  would render as a visibly different species of object directly under the
  notation it mirrors, and would slip past the residual-TeX gate that guards
  everything else.
- **Structure is preserved; only symbols are replaced.** Operators, grouping,
  fractions, exponents, and sum limits stay as notation; a reader should be able
  to lay the two lines on top of each other and see them line up. Replacing `=`
  with "equals" or a fraction with the word "over" defeats the purpose.
- **Names come from the paper and from the Phase 1 glossary**, so a variable is
  named identically in every equation it appears in. Never coin a meaning the
  paper doesn't state.
- **A symbol the paper never defines stays a symbol** in both the named form and
  the legend, where its line reads `— not defined in the paper`, and it goes in
  the Phase 4 flag list. Constraint 5 governs: an undefined variable is a flag,
  never a guess.
- **The legend lists every symbol in the equation, in reading order, once each** —
  including symbols already defined by an earlier equation's legend. A reader
  lands mid-document; a back-reference is not a definition.
- **Skip the block when there is nothing to substitute** — an equation of pure
  numbers, or one whose every symbol is already a spelled-out word. A skip is
  recorded in a running exempt list, never taken silently; Phase 3 reconciles
  that list against the equation count.
- **When full substitution would be less readable than the equation**, substitute
  the outer structure only and let the legend carry the inner detail. A named
  form denser than the equation it explains has failed at its one job.
- **Inline math gets no named form.** The sentence around it already carries the
  meaning; expanding every `$…$` in place would double the length of every
  sentence that mentions a variable.

## Phase 3 — Verify (mechanical, before claiming done)

- Output headings == ledger headings, same order.
- Per-section paragraph counts == ledger counts.
- Per-section equation / table / **figure-slot** counts == ledger counts. A
  figure slot is a placeholder **or** an image — `[Figure N]` and
  `![Figure N](…)` both count, since `/paper-figures` rewrites the former into
  the latter and the totals must still reconcile after a retrofit.
- Named forms reconcile: per section, **named-form blocks + exempt-list entries
  == display-equation count**. Every display equation either carries a named form
  or is on the exempt list with a reason; neither an equation that quietly lost
  its named form nor a named form with no equation above it survives this check.
- Every named form is followed by a `*where:*` legend whose entries cover every
  symbol in its equation, and every `— not defined in the paper` entry appears in
  the Phase 4 flag list.
- Per-section inline-math and display-math counts, **after subtracting the math
  this rewrite authored**, == ledger counts: subtract one `$$…$$` per named form
  and one `$…$` per legend entry. The ledger counts what the source contained, so
  the authored math has to come off the top or the check reports a false mismatch
  on every equation — and every span, source or authored, uses the canonical
  `$…$` / `$$…$$` delimiters. A stray `\(…\)` that survives here becomes
  unrendered TeX on the published page.
- References section present, verbatim as extracted.

Any mismatch → fix and re-verify. Do not claim done until this passes clean.

## Phase 4 — Deliver

- **Path:** `docs/papers/<slug>-eli5.md` in the current repo (create the folder);
  no `docs/` → `papers/` at repo root; not a git repo → next to the input file
  (URL input outside a repo → cwd). Operator notes may override. Slug: kebab-case
  from the paper title, articles dropped, ~6 words max (fallback: arXiv ID).
- **Git (when in a repo):** the normal global workflow — feature branch, commit,
  push, PR, merge autonomously, brief Kyle — unless the host project's CLAUDE.md
  tightens it. Outside a repo: just write the file.
- **Send the file** to Kyle via SendUserFile.
- **Final report:** output path; PR link if any; per-section paragraph tallies
  from Phase 3; every flagged spot (garbled regions, figures replaced by
  placeholders, symbols the paper never defined, and every equation on the
  named-form exempt list with its reason).
- **Next step for figures:** if any `[Figure N]` placeholders remain, say so and
  point at **`/paper-figures`** — it re-finds the original source, harvests the
  real figure images, and fills the placeholders in place without re-running the
  rewrite.

## Definition of done

The rewrite exists at its output path with the header block; Phase 3 passed clean
(headings, per-section paragraph and non-prose counts, named-form reconciliation,
references intact); every display equation carries a named form or an exempt-list
entry; the register and first-use convention held throughout; the file was sent
via SendUserFile; the final report lists path, tallies, and every flag.
