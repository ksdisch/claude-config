# Trajectory management: clear the context to clear the trajectory

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Matt Pocock's framing, endorsed by Bob: a session has a *trajectory* — early steering
decisions echo through everything that follows ("if you get it to test the UI once, it
will test the UI every time"), and "the only way to clear the trajectory is to clear the
context window." Bob's coffee-and-soap-opera story is the same point: contamination is
permanent within a context.

## The bet

**Already covered** — the planner/builder protocol's fresh-session rule and the
never-switch-models-mid-session rule both exist because of exactly this. Captured per
Kyle's capture-all instruction; the residual: trajectory contamination as a *handoff
trigger* (party-line's `auto-handoff` fires on run-config notes, completion shapes, and
context fullness — not on topic drift/contamination).

## Decisions / open questions

- Is drift-detection a worthwhile fourth trigger for `auto-handoff` (Project: party-line),
  or too fuzzy to mechanize? That's the only open delta.

## Credible first step

If pursued: a party-line exploration stub describing what a detectable "trajectory
contamination" signal would even be. Otherwise close as covered.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20**.

## Explicitly out of scope

- Global machinery; anything before the signal question is answered.

## Source segment

> "the only way to clear the trajectory is to clear the context window"

Context: Bob's parallel — a passerby's soap-opera chatter enters the coffee conversation's
context and "from that point on all the coffee references have to do with the soap
opera… As long as you can keep the direction of the model unconfused… it's not going to
have these crazy hallucinations."
