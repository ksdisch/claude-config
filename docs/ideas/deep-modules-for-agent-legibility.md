# Prefer deep modules (small interface, deep implementation) for agent legibility

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Ousterhout's deep-modules idea gets a new justification in the agent era: models "can
read the interface without having to understand the implementation" — a narrow interface
over a deep implementation lets an agent work against a module without loading its guts
into context. Bob: "anything you can do that helps the structure of the code will help
the models understand that code."

## The bet

Deep-modules-as-context-economy is worth one stated CLAUDE.md rule, so code review and
new-module scaffolds prefer narrow interfaces deliberately rather than by taste. Bob's
caveat rides along: interface-only reading "is both a danger and an advantage — as long
as the code is consistent, you're okay."

## Decisions / open questions

- Global CLAUDE.md rule vs. an `adversarial-review` lens ("is this module shallow?") —
  the review-lens form is enforceable, the rule form is cheap. Could be both.

## Credible first step

One sentence in the global CLAUDE.md code-conventions territory; optionally one line in
the adversarial-reviewer charter's checklist.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20**.

## Explicitly out of scope

- Refactoring existing modules to comply; any metric for "depth" (that way lies a gate
  nobody asked for).

## Source segment

> "deep modules which have a small interface and then a deep um lots of hidden
> information inside them … they can read the interface without having to understand
> the implementation"

Context: Matt raises Ousterhout's deep-modules concept; Bob: "absolutely… they pay
attention to the structure. It can allow them to not read the code beneath them, which
is both a danger and and an advantage."
