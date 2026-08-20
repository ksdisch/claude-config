# Agent gauntlet pipeline: specifier → coder → cleaner → hardener → QA

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Uncle Bob's working pipeline relays every story through five narrow-context agents —
specifier (human doc → Gherkin + QA procedure), coder (unit tests + implementation),
cleaner (CRAP analysis + general review), hardener (mutation testing, merciless), QA
(executable script from the QA doc) — with each stage ending in a deterministic check
rather than a judgment call, and a fresh context per stage. He reports ~4–5× human
productivity at higher-than-human quality: a 5-minute single-agent task takes the
gauntlet an hour, versus half a day for a person.

## The bet

Quality comes from deterministic loops between focused agents, not from steering one
long-context agent. The existing `adversarial-review` loop already proves the review
stage of this relay works; the bet is that extending the relay in both directions
(spec before, harden/QA after) buys the same reliability for the whole build, not just
the merge gate.

## Decisions / open questions

- Orchestration surface: Workflow tool script vs. a skill that chains `Agent` dispatches
  vs. `/autonomous-milestone` integration. The Workflow tool's pipeline() is the natural
  fit; decide whether the gauntlet is its own skill or a mode of autonomous-milestone.
- Which stages are agents vs. plain tools: the cleaner overlaps `code-simplifier` and the
  QA stage overlaps `/smoke-test` — reuse or purpose-build?
- Per-language deterministic tooling (complexity, coverage, mutation) must exist for the
  target repo; the gauntlet needs a capability probe stage or a per-repo config.
- Where the human sits: Bob reviews scores and spot-checks, never the code. Does the
  adversarial-review gate still run at merge, or does the gauntlet subsume it? (One gate
  per merge is the standing rule.)

## Credible first step

A three-stage skeleton on one real repo: specifier → coder → hardener, with the Stop-hook
or in-loop check "tests green + mutation survivors = 0" as the only gates. Measure
wall-clock and quality against a plain single-session build of the same story.

## Dependencies

- Workflow tool availability — **verified 2026-08-20** (present and documented in-session).
- Agent-file `model:`/`effort:` frontmatter keys — **verified** (recorded as consumed
  fields in CLAUDE.md's planner/builder protocol; note the misspelled-`effort:` silent
  fallback caveat).
- Per-language mutation/complexity tools (Stryker, mutmut, etc.) — external to Claude
  Code; must be checked per target repo.

## Explicitly out of scope

- Building any of the five stage agents to production quality before the skeleton proves
  the relay pays (the hardener and specifier have their own idea docs:
  [`mutation-testing-hardener.md`](mutation-testing-hardener.md),
  [`specifier-subagent.md`](specifier-subagent.md)).
- Replacing `adversarial-review` — that decision is gated inside this doc, not assumed.

## Source segment

> "one guy does one thing and the next one reviews it and the next one tests it and the
> next one hardens it and so on"

Context: Bob describes the full relay — "I will run a specifier… those feed into a coder…
that gets fed into a cleaner… then I have it go from there to a hardener… then it goes
into a QA agent" — and the economics: "it'll take about an hour… a person would take
about a half a day."
