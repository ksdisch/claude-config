---
name: paper-eli5
description: Rewrite someone else's research paper into plain English — section by section, paragraph by paragraph, 1:1. Same headings, same paragraph order; nothing summarized, merged, dropped, or reordered; only the language changes (smart-newcomer register, jargon translated on first use). Accepts a local PDF/markdown/text path, an arXiv URL or bare ID, or any other web URL. Equations and tables stay verbatim with an "in plain words" gloss; figures become placeholders with rewritten captions; the references section passes through untouched. Output lands in the current repo at docs/papers/<slug>-eli5.md (papers/ if no docs/; beside the input outside a repo) and is sent to Kyle. Use whenever Kyle types /paper-eli5, or says "eli5 this paper", "simplify this paper", "plain-English this paper", "make this paper readable", "translate this paper for a layman" — even if he doesn't name the skill. NOT for writing up Kyle's own finished projects (research-paper) and NOT for choosing the next project (seed-hunt). Works interactively or unattended; after the input paper is known it runs end-to-end.
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
4. **NON-PROSE PASSES THROUGH.** Equations and tables verbatim in place, each
   immediately followed by an italic *"In plain words: …"* line; table values are
   never altered. Figure images can't be carried from a PDF: a `[Figure N]`
   placeholder holds the spot and the caption is rewritten (markdown/HTML inputs
   keep their image references). Inline citation markers (`[12]`, `(Smith et al.,
   2023)`) stay exactly where they are; the references section is carried verbatim
   as extracted — never rewritten, never pruned.
5. **NEVER INVENT.** Garbled or unreadable regions are flagged in the final
   report, not filled in.

## Phase 1 — Map (before writing a word)

Ingest the whole paper first. Build two internal working artifacts (never shipped):

1. **Skeleton ledger** — every heading verbatim, in order; per section: paragraph
   count plus counts of equations, tables, and figures.
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
  rewrite mirroring the original structure 1:1 with equations/tables verbatim.

## Phase 3 — Verify (mechanical, before claiming done)

- Output headings == ledger headings, same order.
- Per-section paragraph counts == ledger counts.
- Per-section equation / table / **figure-slot** counts == ledger counts. A
  figure slot is a placeholder **or** an image — `[Figure N]` and
  `![Figure N](…)` both count, since `/paper-figures` rewrites the former into
  the latter and the totals must still reconcile after a retrofit.
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
  placeholders).
- **Next step for figures:** if any `[Figure N]` placeholders remain, say so and
  point at **`/paper-figures`** — it re-finds the original source, harvests the
  real figure images, and fills the placeholders in place without re-running the
  rewrite.

## Definition of done

The rewrite exists at its output path with the header block; Phase 3 passed clean
(headings, per-section paragraph and non-prose counts, references intact); the
register and first-use convention held throughout; the file was sent via
SendUserFile; the final report lists path, tallies, and every flag.
