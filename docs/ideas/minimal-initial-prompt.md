# Minimal initial prompt: trim always-loaded instructions to the salience budget

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Because of lost-in-the-middle, "the key with agents is to trim that initial prompt down
to its absolute minimum so that you can get as much of it as possible into its priority."
Long always-loaded instruction files don't fail loudly — their middle just stops
existing.

## The bet

The global CLAUDE.md is long (git workflow, ID-gloss rule, planner/builder protocol,
reference-doc maintenance, wiki rules), and this claim says its effective content is
smaller than its actual content. `/trim-context` already hunts bloat *by size*; the
missing criterion is *positional salience and mechanizability* — which rules must be in
the head/tail, and which can convert to hooks and leave the prompt entirely.

## Decisions / open questions

- Build as an improvement to `/trim-context` (a salience pass alongside the size pass),
  not a rival command.
- Ordering: hoisting must-holds to top/bottom of CLAUDE.md is a cheap reorder; converting
  rules to hooks is a per-rule project — the audit should output a ranked conversion
  list, not do the conversions.

## Credible first step

Run the audit once by hand on the global CLAUDE.md: classify each rule must-hold vs
guidance, list hook-convertible ones, and see if the resulting reorder is worth a PR.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20** (analysis + doc edits).

## Explicitly out of scope

- Actually converting rules to hooks (each conversion is its own change with its own
  review); touching project CLAUDE.md files before the global one proves the method.

## Source segment

> "trim that initial prompt down to its absolute minimum so that you can get as much of
> it as possible into its priority"

Context: "maybe the first three sentences you put at the beginning will remain as
priority, but the 50th and the 80th sentence in there, they're gone."
