# QA agent: written QA doc → executable UI script

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

The last stage of Bob's gauntlet: an agent takes the human-readable QA procedure (from
the specifier) and "turns it into an executable script that manipulates the system and
comes up with a deterministic result."

## The bet

`/smoke-test` currently ends at a checklist Kyle walks himself — precisely the human
slowness Bob designs out. The written procedure is already the input; the missing half
is compilation to a browser script. Constellation's `/verify-planet` proves the pattern
works in one project; this generalizes it.

## Decisions / open questions

- Build as a second stage of `/smoke-test` (checklist → script) rather than a new skill.
- Driver: Playwright MCP vs. claude-in-chrome — Playwright is the headless/CI-capable
  choice; claude-in-chrome sees the real logged-in browser. Probably Playwright for
  determinism, matching `/verify-planet`.
- Script persistence: one-shot verification vs. saved into the repo as a regression
  harness (saved is more valuable, needs a home + naming convention).

## Credible first step

Take one existing `/smoke-test` output checklist and have an agent compile it into a
Playwright script by hand-dispatch; run it; judge the pass/fail fidelity before touching
the skill.

## Dependencies

- Playwright MCP plugin enabled — **verified 2026-08-20** (settings.json
  `enabledPlugins`); whether MCP tools reach subagents in headless/cron runs remains the
  known caveat (interactively-authenticated servers may be absent there).

## Explicitly out of scope

- Full E2E test-suite generation; replacing project-native test harnesses.

## Source segment

> "the QA agent takes the the written QA document, turns it into an executable script
> that manipulates the system and comes up with a deterministic result"

Context: "if you can get through all of that, you've got a pretty pretty working
program."
