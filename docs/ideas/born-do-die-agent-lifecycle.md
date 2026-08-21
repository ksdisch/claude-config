# Born-do-die agent lifecycle: fresh context per task

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob's agents "are born, do the task, and die so that the next one comes in with a clean
context" — narrow focus keeps lost-in-the-middle at bay, at the cost of 10–15s startup
and re-orientation per agent.

## The bet

**Already covered** — the planner/builder protocol mandates builder sessions start fresh
from the plan file, and subagent dispatch is the standing in-session form. Captured per
Kyle's capture-all instruction; the residual is only Bob's *cost caveat*: startup time
means don't decompose below the task size that repays a fresh context.

## Decisions / open questions

- Is the decomposition-floor caveat worth one sentence in the planner/builder protocol
  ("split only when the stage outlives its startup cost")? That's the entire open
  question; otherwise close as confirmed-covered.

## Credible first step

Either add the one sentence, or close this stub as covered.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20**.

## Explicitly out of scope

- Any new lifecycle machinery — the protocol and Agent tool already are it.

## Source segment

> "the agents um are born, do the task, and die so that the next one comes in with a
> clean context"

Context: "the startup times are high, right? So an agent takes, you know, 10 15 seconds
to even start up… and then it's got to figure out its whole context all over again."
