# Tests as agent documentation: keep tests readable as the behavioral spec

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

"They read tests to understand what the system does" — agents use the test suite as
system documentation, which promotes test readability from a human nicety to a
functional interface for every future agent session in the repo.

## The bet

One stated convention — test names are behavior statements, test bodies are worked
examples — pays compounding rent in every agent session that reads the suite to orient.
Pairs naturally with [`ephemeral-specs.md`](ephemeral-specs.md): if prose specs are
scratch, readable tests are what's left as the durable spec.

## Decisions / open questions

- Where: global CLAUDE.md vs. per-project conventions. Global states the principle;
  projects with test suites get the specifics.

## Credible first step

One paragraph in the global CLAUDE.md; apply opportunistically in review rather than
retrofitting suites.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20**.

## Explicitly out of scope

- Renaming existing tests wholesale; any lint enforcement.

## Source segment

> "They read tests to understand what the system does"

Context: "the models pay attention to interface names… they also pay attention to the
tests."
