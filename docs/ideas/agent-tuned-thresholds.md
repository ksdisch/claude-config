# Agent-tuned thresholds: widen human lint limits for agents

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob keeps CRAP scores below 4 for humans but sets 6 for agents and is considering 8:
agents have a huge, perfectly accurate short-term memory, so complexity limits calibrated
to human working memory over-constrain them for no quality gain.

## The bet

Every numeric gate this config builds (complexity, function size, file size) should
carry per-audience thresholds — and copying human style guides into agent gates is a
category error worth writing down once, where every future gate can cite it.

## Decisions / open questions

- Where the rule lives: a paragraph in CLAUDE.md vs. a threshold registry file each gate
  reads. Registry only earns its keep once ≥2 gates exist.
- Bob's caveat applies: "you can't trust any debate you have with an agent" about what
  its own threshold should be — thresholds get set by observed failure, not by asking
  the model.

## Credible first step

One CLAUDE.md sentence stating the principle, added in the same PR as the first numeric
gate that ships (likely [`crap-score-gate.md`](crap-score-gate.md)).

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20** (pure convention).

## Explicitly out of scope

- Picking actual numbers before a gate exists to attach them to.

## Source segment

> "for a human I would keep crap numbers below four, right? But for the agents I've set
> this at six and I'm thinking and maybe I'll push it to eight"

Context: "the agents can deal with different levels of complexity than humans. They have
a much better short-term memory… and a perfectly accurate short-term memory."
