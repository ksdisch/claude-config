# CRAP-score gate: coverage × cyclomatic complexity as a deterministic quality loop

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob's core post-implementation move: run CRAP (per-function cyclomatic complexity ×
test coverage → one "crappiness" score) over everything the agent just wrote, and loop
the agent until scores are under threshold. Deterministic number, not steering prose.

## The bet

This config's hooks gate *git behavior*; nothing gates the *code*. A CRAP gate is the
hooks-over-prompts convention applied to code quality itself — it replaces "write clean
code" (an instruction that decays into the middle of the context) with a pass/fail.

## Decisions / open questions

- **Enforcement point — amended by verification:** PostToolUse **cannot block or force
  re-action** (feedback-only), so the loop must anchor on the **Stop hook** (exit 2
  forces continuation with a reason) or run as an in-skill loop / `/crap-check` command
  the Stop evaluator invokes. Design around Stop, not PostToolUse.
- Per-language scoring: coverage + complexity tools differ per stack (radon/coverage.py,
  eslint-complexity/istanbul, etc.); a small wrapper script per repo, or one polyglot
  prober?
- Thresholds are per-audience — see
  [`agent-tuned-thresholds.md`](agent-tuned-thresholds.md) (Bob: 4 for humans, 6–8 for
  agents).
- Global hook vs. per-repo opt-in? A global Stop-gate that fires on repos without the
  tooling would thrash; per-repo opt-in via a config file is safer.

## Credible first step

A standalone `/crap-check` command (report-only, ranked worst functions) on one repo with
coverage already wired. Promote to a Stop-hook loop only after the score proves stable
and non-noisy.

## Dependencies

- Stop hook can block and force continuation — **verified 2026-08-20** against
  code.claude.com/docs/en/hooks.md.
- PostToolUse **cannot** gate — **verified same source**; design must not depend on it.
- Coverage + complexity tooling — external, per target repo.

## Explicitly out of scope

- Mutation testing (the hardener's job); enforcing on repos without coverage
  infrastructure.

## Source segment

> "why don't you run crap over everything you've just done and it would run crap and
> then it would it would clean up the code"

Context: CRAP's 2000s origin — "you would run… test coverage over your code and you'd
also measure the cyclatic complexity of every function and you would mix those two in a
complicated formula and out would come a score" — impractical then, cheap now.
