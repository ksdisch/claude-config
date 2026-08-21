# Specifier subagent: human doc → Gherkin + QA procedure

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

The first stage of Bob's gauntlet: an agent that takes a rough human-written feature
description and emits two artifacts — a Gherkin acceptance test (given/when/then) and a
written QA procedure phrased from a human-at-the-UI point of view ("You are a human. You
are operating this system at the UI. You must prove that the system works").

## The bet

Converting vague intent into deterministic acceptance criteria *before any code exists*
is the cheapest point to catch building-the-wrong-thing — and standalone, it's a sharper
`Acceptance:` generator for backlog stubs than prose.

## Decisions / open questions

- Standalone agent (`agents/specifier.md`) vs. gauntlet-only stage — standalone first;
  the gauntlet consumes it later.
- Where outputs land: Gherkin next to tests, QA procedure in `docs/`? Both are inputs to
  later stages (coder gets the Gherkin, QA agent gets the procedure).
- Relation to DogHood's `/new-scope` (scope briefs): same instinct, project-specific
  template — the specifier is the global, test-shaped version.

## Credible first step

Draft `agents/specifier.md` and run it on one real backlog stub; compare its Acceptance
output against the hand-written one already there.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20** (plain agent dispatch).

## Explicitly out of scope

- Executing the QA procedure (see [`qa-doc-to-executable-script.md`](qa-doc-to-executable-script.md));
  Gherkin runner tooling.

## Source segment

> "The job of the specifier is to take a a human written document and turn it into a uh
> a girkin and a QA a QA uh procedure"

Context: "Girkin is you know given when then stuff. It's a high level acceptance test.
And a QA procedure is essentially a system test… I have them write it from a human's
point of view."
