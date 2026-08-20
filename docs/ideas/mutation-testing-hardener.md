# Mutation-testing "hardener" subagent

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Mutation testing — flip operators across the code, expect the suite to fail per mutant,
kill every survivor — was always the strongest test-quality signal and always impractical
for humans (Bob: an overnight run in 2000). Agents don't care how boring the work is; his
"hardener" runs it mercilessly as a standing pipeline stage.

## The bet

Nothing in this config measures test-suite *strength* — `bug-hunt` finds defects,
`adversarial-review` judges diffs, `silent-failure-hunter` finds swallowed errors, but
nothing tests the tests. A hardener agent closes that class. Coverage isn't it.

## Decisions / open questions

- Read-then-fix (plugs survivors with tests itself) vs. read-only auditor that reports
  survivors, `silent-failure-hunter`-style? The existing auditor shape is the proven
  template; fixing is more valuable but needs the tests-unmodified rules thought through.
- Per-language runners: Stryker (JS/TS), mutmut (Python) — probe-and-report when absent,
  never silently skip.
- Scope: whole repo vs. diff-scoped (diff-scoped keeps runtime sane and matches the
  gauntlet stage).

## Credible first step

An `agents/mutation-hardener.md` modeled on `silent-failure-hunter.md` (read-only,
graded findings), dispatched by hand over one repo with Stryker installed. Promote to
fix-mode only after the report format proves useful.

## Dependencies

- Agent-file `model:`/`effort:` frontmatter — **verified 2026-08-20** (consumed fields per
  CLAUDE.md planner/builder protocol).
- Mutation runners (Stryker, mutmut) — external to Claude Code, must exist per target repo;
  **not version-sensitive to Claude Code itself**.

## Explicitly out of scope

- Wiring it as an automatic gate (that's the gauntlet's call:
  [`agent-gauntlet-pipeline.md`](agent-gauntlet-pipeline.md)); CI integration.

## Source segment

> "The hardener is the guy who runs the mutation testing and he's absolutely merciless"

Context: "it's going to mutate it and it's going to have 100% coverage and every equal
sign and every less…" — and the history: in 2000 the same run "was impractical. I could
not put that as part of a normal build scenario."
