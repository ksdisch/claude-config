# Spot-check dashboard: monitor scores instead of reading code

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob's human role after the gates run: "I will look at the crap scores and make sure that
they're low. And I will do spot checks on the code from time to time" — score
monitoring plus sampled reading, never full review.

## The bet

Once any metric gate exists, a `/health`-style command that prints the current scores
(worst functions, trend since last check) gives Kyle Bob's supervision posture for the
cost of a report formatter. Folds naturally into the CRAP gate if built.

## Decisions / open questions

- Standalone command vs. a report mode of [`crap-score-gate.md`](crap-score-gate.md) —
  almost certainly the latter; this stub exists so the *supervision posture* half of the
  idea isn't lost inside the gate's enforcement half.

## Credible first step

Ship `/crap-check` (the gate's report-only first step) — it *is* this dashboard v0.

## Dependencies

- Same tooling as the CRAP gate (coverage + complexity per repo) — external.

## Explicitly out of scope

- Trend storage/history before the point-in-time report proves useful.

## Source segment

> "I will look at the crap scores and make sure that they're low. And I will I will do
> spot checks on the code from time to time"

Context: "I'm going to work very hard to get it into a situation where I don't have to
look at the code at all… I'm going to deal with the stuff around that to make sure it's
all okay."
