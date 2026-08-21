# Module dependency-rules checker: a spec file the agents cannot violate

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob declares which modules may depend on which in "a nice tight little specification
file that the agents cannot violate," with a checker at the end of the run; violations
force the agent to invert a dependency, insert an interface, or split a module.

## The bet

Architecture is the one thing agents reliably erode and no test catches. A dependency
spec is the cheapest deterministic encoding of "strategic" design — the exact layer Bob
says agents can't do themselves. Today this repo's architecture governance is entirely
prose an agent can soften.

## Decisions / open questions

- **Enforcement point — amended by verification:** PostToolUse is feedback-only, so
  enforcement lands on the **Stop hook** (blocking, verified), a pre-push hook alongside
  `check-doc-sync.py`, or CI. Pre-push mirrors the existing house pattern and can't
  thrash mid-turn; Stop catches it earliest. Possibly both.
- Checker: dependency-cruiser (JS/TS) vs. a small per-repo script reading a house
  `deps.yml`. A house format keeps it polyglot; dependency-cruiser is free where it fits.
- Global pattern, per-repo instantiation — which project pilots it? (Constellation or
  DogHood have the clearest layer rules.)

## Credible first step

Write `deps.yml` + a ~50-line checker for one repo, run it by hand over the current tree,
and see whether it finds real violations before wiring any hook.

## Dependencies

- Stop hook blocking — **verified 2026-08-20** (code.claude.com/docs/en/hooks.md);
  PostToolUse cannot gate (same source).
- Dependency-graph tooling — external, per language.

## Explicitly out of scope

- Auto-fixing violations (the agent in the loop does that); visualizing the graph
  (that's [`architecture-viewer.md`](architecture-viewer.md)).

## Source segment

> "That goes into a nice tight little specification file that the agents cannot violate"

Context: "I can define which module should depend on which, which one should not depend
on which, how the dependency should flow… there's another little checker that runs at
the end and if they violate it, they've got to fix it somehow. Usually by inverting a
dependency or inserting an interface or splitting a module in half."
