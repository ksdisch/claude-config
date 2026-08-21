# Values, not disciplines: stop imposing human TDD ritual on agents

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob — the loudest TDD advocate alive — no longer imposes line-by-line red-green TDD on
agents: "even when I have told them to do test-driven development at high discipline,
they always fall back" to function-then-test. His distinction: *values* (everything
tested, complexity bounded, small interfaces) are legitimate to enforce on agents;
*disciplines* (the human ritual that produces those values, compensating for human
working memory) are not, because agents don't share the limitation.

## The bet

If he's right, the strict-TDD machinery in this config is fighting the model instead of
constraining the output — burning prompt budget on a rule that doesn't hold, where a
deterministic outcome gate (coverage + mutation) would enforce the value directly.

## Decisions / open questions

- **This idea Contradicts `/tdd` and `superpowers:test-driven-development`** (rigid,
  "follow exactly"). Adopting it means rewriting `/tdd` into a tests-as-spec outcome
  gate and recording a divergence from the superpowers skill; rejecting it should be a
  recorded decision too. The capture's job is to force this call, not pre-decide it.
- Does the failing-test-first *commit* discipline (tests committed before implementation,
  tests never modified) survive as a value even if line-by-line ping-pong dies? Probably
  yes — decide explicitly.

## Credible first step

One session: run the same small feature twice on a scratch repo — once under `/tdd` as
written, once under "outcome gate only" (coverage + tests-unmodified check) — and diff
quality, wall-clock, and how often the agent actually obeyed the ritual.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20** (pure convention decision).

## Explicitly out of scope

- Deleting `/tdd` before the experiment; weakening the tests-never-modified invariant.

## Source segment

> "it's probably a mistake to impose a human discipline on an agent. It is not a mistake
> to impose human values on the agent"

Context: he allows agents to "behave more like John Ousterhout would — write a function
and then write the test for that function," noting they revert to this even under
high-discipline instruction.
