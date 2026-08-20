# Concentrate steering density in narrow-scope subagents

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

When an agent's task is narrow, its context stays small and rules keep their salience:
"you can pile a few more, not a lot more, but a few more rules up at the top and they'll
tend to follow them better." Matt's version: the reviewer can absorb far more steering
than the implementer because its task is less open-ended.

## The bet

Steering budget should be allocated *inversely to task breadth*: keep broad sessions
lean, and put the dense rulebooks in narrow single-purpose agents. This is implicit in
the existing agent files (`adversarial-reviewer`, `silent-failure-hunter` carry rich
charters) but stated nowhere — so nothing stops the next skill from doing the opposite.

## Decisions / open questions

- Where it lives: an agent-authoring note in CONVENTIONS.md (if that idea ships) vs. a
  line in CLAUDE.md. Pairs with [`minimal-initial-prompt.md`](minimal-initial-prompt.md)
  — same salience budget, two directions.

## Credible first step

One paragraph wherever agent-authoring guidance ends up living; cite the two existing
agents as the worked examples.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20** (pure convention).

## Explicitly out of scope

- Rewriting existing agents (they already comply).

## Source segment

> "you can pile a few more, not a lot more, but a few more rules up at the top and
> they'll tend to follow them better"

Context: "when you focus the agents down to a single task, you're keeping the context
window under control. The lost in the middle problem becomes much less of a problem."
