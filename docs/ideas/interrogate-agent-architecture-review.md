# Interrogate-the-agent architecture review

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Before redesigning, Bob interrogates the agents about the code they built: "What's the
structure here? How does this module interrelate with that module? What are the modules
after all?" — then "I would get scared to death because the answers were horribly
frightening," and only then designs the module structure and hands back an
implementation plan.

## The bet

A structured interrogation ritual after each meaningful build chunk catches
architectural drift while it's one story old. Overlaps `feature-dev:code-explorer`
(deep codebase analysis) and `/project-guide` (whole-project prose) — the delta is
cadence and framing: a short, repeatable Q&A about *what just changed structurally*,
not a full guide.

## Decisions / open questions

- Skill vs. habit: possibly just a named question set inside `ship-and-route` or `/wrap`
  rather than a new artifact. If the architecture viewer ships, the viewer likely
  subsumes this (look at the map instead of asking).

## Credible first step

Try it as a raw prompt after the next multi-file build: "explain the module structure
you just created and its dependencies; flag anything that would scare a maintainer."
Decide from the answer whether it earns a durable home.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20**.

## Explicitly out of scope

- The visual map ([`architecture-viewer.md`](architecture-viewer.md)); duplicating
  `feature-dev:code-explorer`.

## Source segment

> "I'd interrogate the agents. What's the structure here? How how does this module
> interrelate with that module?"

Context: "…and then I would get scared to death because the answers were horribly
frightening. And then I would design a module structure and I would tell the agent,
okay, here's how the modules should really be partitioned."
