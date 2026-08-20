# Ephemeral specs: the end result is the specification

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob doesn't persist specs: "the specifications are ephemeral, they go away… there is no
equivalent to source code." What persists is the *checks* — Gherkin acceptance tests, QA
scripts, dependency specs — and the code itself: "I look at the end result and say,
well, that is the specification." He calls the industry spec-driven-development wave
"probably not going to work; my experiments did not work particularly well."

## The bet

Prose specs written to drive a build are scratch; keeping them as durable artifacts
creates a second source of truth that drifts. If adopted, spec files become archaeology
snapshots, not living documents.

## Decisions / open questions

- **This idea Contradicts `spec-miner`**, whose premise is durable
  `openspec/specs/<capability>/spec.md` files as first-class artifacts. Resolve
  deliberately: are spec-miner's outputs living documents (then this idea is rejected,
  record why) or point-in-time mining aids (then say so in spec-miner's charter)? The
  capture forces the call, not the answer.
- Distinguish spec *prose* from spec *checks*: Bob keeps Gherkin and QA scripts. The
  config's analogue: vision docs and plan files are steering (ephemeral?), tests and
  hooks are the spec (durable). Where do wiki Decisions.md records fall? (Probably
  durable — they record *why*, which code can't.)

## Credible first step

A one-paragraph amendment to `spec-miner`'s charter declaring which of the two readings
its outputs get — no tooling change at all.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20** (pure convention decision).

## Explicitly out of scope

- Deleting existing openspec outputs; changing plan-file practice (that's
  [`anti-plan-maxing.md`](anti-plan-maxing.md)'s fight).

## Source segment

> "the specifications are ephemeral they go away" … "I look at the end result and say,
> well, that is the specification"

(Auto-caption renders "ephemeral" as "ephemeris.") Context: "There is no equivalent to
source code… there has to be a human thing that defines everything up front. Well —"
and his tools-as-spec move: point your agents at my tools and build your own.
