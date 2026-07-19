# paper-eli5 — design spec

**Date:** 2026-07-19
**Status:** approved design, pre-implementation
**Deliverable:** one new skill at `skills/paper-eli5/SKILL.md` (auto-invocable as `/paper-eli5` via the `~/.claude/skills` symlink). No other files change.

## Purpose

Given someone else's research paper, produce a plain-English rewrite of the whole
paper that mirrors the original's structure exactly — section by section, paragraph
by paragraph. Nothing is reformatted, reordered, summarized, or dropped; the only
change is that the language becomes readable by a smart newcomer instead of a field
expert.

Lineage fit: this is the read-someone-else's-paper aid that `research-paper`'s
description points at ("NOT for reading someone else's paper"). The name
`paper-companion` stays reserved for a possible future interactive companion
(Q&A, quizzing); `paper-eli5` is deliberately a one-shot translator.

## Triggering

Frontmatter description triggers on: `/paper-eli5`, "eli5 this paper", "simplify
this paper", "plain-English this paper", "make this paper readable", "translate
this paper for a layman". Disambiguation in the description: NOT for writing up
Kyle's own projects (`research-paper`) and NOT for choosing the next project
(`seed-hunt`). Works interactively or unattended; after the input paper is known
there are no stops.

## Input (`$ARGUMENTS`)

- **Local path** ending `.pdf` / `.md` / `.txt` → read directly. PDFs are read via
  the Read tool in ≤20-page chunks.
- **arXiv URL or bare ID** (e.g. `2402.01234`, `arxiv.org/abs/…`) → normalize to
  the PDF URL (`arxiv.org/pdf/<id>`), download to `/tmp` (never committed into a
  repo), then read as PDF.
- **Any other URL** → fetch as clean markdown via the `obsidian:defuddle` skill,
  falling back to WebFetch.
- **Remaining words** in the argument are operator notes: they may tune register
  ("even simpler"), override the output path, or add emphasis. Notes never override
  the Fidelity hard constraints.
- **No argument** → ask which paper. In an unattended run with no/ambiguous input,
  report the ambiguity as the outcome instead of guessing.

## Approach (decided)

Ledger-disciplined single session — two passes in the main session, no subagents.
Chosen over a straight one-shot rewrite (nothing would prevent summarization drift
on long papers) and over per-section subagent fan-out (costlier, and sections lose
whole-paper context). The ledger is the structural guard; the glossary is the
consistency guard.

## Pass 1 — Map (before writing a word)

Build two internal working artifacts (not shipped):

1. **Skeleton ledger** — every heading verbatim, in order (Abstract counts as a
   section; appendices included), and per section: paragraph count plus counts of
   equations, tables, and figures.
2. **Glossary** — every field-jargon term and acronym mapped to ONE chosen
   plain-English rendering, decided here and used consistently across all sections.

PDF text extraction often garbles paragraph boundaries (two-column layouts,
hyphenation). The map pass reconstructs true paragraph boundaries by judgment; the
ledger is built from that reconstruction, so the Verify phase checks output against
a self-consistent baseline. Unreadable/garbled regions are flagged in the final
report — content is never invented to fill them.

## Pass 2 — Rewrite contract

Proceed section by section in order, appending each finished section to the output
file and checking it off against the ledger.

- **Headings kept verbatim** (navigation anchors). An opaque heading may get a
  short parenthetical gloss appended.
- **1 original paragraph → 1 rewritten paragraph.** Same order. Never merged,
  split, dropped, or reordered. All of a paragraph's information is carried —
  simpler wording, not less content. Sentence count may change; paragraph count
  may not.
- **Lists and footnotes:** bulleted/numbered lists stay lists, item-for-item, each
  item's wording simplified; footnotes stay in place and are simplified like prose.
- **Register:** smart-newcomer plain English. First use of a term = plain phrase
  with the original term in parentheses (the reader still learns the field's
  vocabulary); subsequent uses follow the glossary. Analogies only where they
  genuinely help.
- **Equations and tables:** kept verbatim in place, each immediately followed by an
  italic *"In plain words: …"* line. Table values are never altered.
- **Figures:** images can't be carried from a PDF; a `[Figure N]` placeholder holds
  the spot and the caption is rewritten. (Markdown/HTML inputs that reference image
  URLs keep the reference.)
- **Citations:** inline markers (`[12]`, `(Smith et al., 2023)`) stay exactly where
  they are. The references section passes through verbatim as extracted — never
  rewritten, never pruned.

### Fidelity hard constraints (non-negotiable)

1. No added opinions, commentary, fact-checking, or editorializing — this is a
   translation, not a review.
2. Numbers, results, and claims stated exactly as the paper states them; an analogy
   must never shift a claim's meaning or strength.
3. Ambiguous passages get a conservative, close-to-literal translation — never a
   guess dressed as a simplification.
4. Nothing summarized, nothing skipped, nothing added. Structure is sacred.

## Verify (mechanical, before claiming done)

- Output headings == ledger headings, same order.
- Per-section paragraph counts == ledger counts.
- Per-section equation / table / figure-placeholder counts == ledger counts.
- References section present and verbatim.

Any mismatch → fix and re-verify. This is the guard against silent summarization.

## Output & delivery

- **Path:** `docs/papers/<slug>-eli5.md` in the current repo; no `docs/` → use
  `papers/` at repo root; not a git repo → next to the input file (URL input
  outside a repo → cwd). Operator notes may override.
- **Slug:** kebab-case from the paper title, articles dropped, ~6 words max
  (fallback: arXiv ID).
- **Header block** at the top of the output: paper title, authors, source
  (link/path), generation date, and a one-line note that this is a plain-English
  rewrite mirroring the original structure 1:1 with equations/tables verbatim.
- **Git:** normal global workflow — feature branch, commit, push, PR, merge
  autonomously, brief Kyle — unless the host project's CLAUDE.md tightens it.
  (No review-only-PR override here: this is a reading aid, not a record of truth.)
- **SendUserFile** the finished rewrite.
- **Final report:** output path, PR link (if repo), per-section paragraph tallies
  from Verify, and every flagged spot (garbled regions, figures replaced by
  placeholders).

## Out of scope (YAGNI)

No TL;DR or summary section, no Q&A/quizzing (future `paper-companion` territory),
no audio, no shipped glossary section, no re-deriving or reformatting of math, no
figure regeneration. It rewrites language; everything else passes through.

## Definition of done (for the skill itself)

`skills/paper-eli5/SKILL.md` exists with house-style frontmatter (name + rich
trigger description) and a body encoding: input parsing, the two-pass
ledger/glossary approach, the rewrite contract, the fidelity hard constraints, the
mechanical verify, and output/delivery rules — all consistent with this spec.
