# Cleaner agent as an automatic between-tasks stage

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob's cleaner stage runs CRAP analysis plus general review after every implementation
pass — "clean up whatever mess the implementer made, because the implementer will have
made a horrible mess by that point." The mess isn't an accident to catch occasionally;
it's an expected byproduct to clean on schedule.

## The bet

The capability exists (`code-simplifier` agent, `/simplify` skill) but only on demand.
The delta is *placement*: cleaning as a standing stage between tasks rather than a thing
Kyle remembers to invoke. Un-cleaned mess compounds — Bob's December observation was
agents slowing down and breaking one thing while fixing another as mess accumulated.

## Decisions / open questions

- Trigger: gauntlet stage (if the pipeline ships) vs. a habit rule ("run /simplify before
  every PR") vs. wired into `ship-and-route`'s land flow. The ship-and-route wiring is
  the cheapest real placement.
- Guard: the cleaner must not fight `adversarial-review` — cleanup lands before review,
  never after a CLEAR verdict.

## Credible first step

One line in `ship-and-route`'s pre-review flow offering a `/simplify` pass on the diff,
trialed for a few merges to see if it catches real mess or just churns style.

## Dependencies

- `code-simplifier` plugin enabled — **verified 2026-08-20** (settings.json
  `enabledPlugins`); `/simplify` skill present — **verified** (session skill roster).

## Explicitly out of scope

- Building a new cleaner agent (reuse the plugin's); auto-cleaning without a diff review
  gate downstream.

## Source segment

> "the cleaner's job is to run crap analysis and just general code review. clean it
> clean up whatever mess the implement made"

Context: "…because the implement will have made a horrible mess by that point."
