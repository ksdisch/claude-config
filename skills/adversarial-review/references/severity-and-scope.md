# Severity grades and the escape hatch

Orchestrator-side calibration: how findings gate the merge, and which diffs may skip the loop. (What the reviewer *hunts for* lives in the reviewer's own brief — `agents/adversarial-reviewer.md` in the claude-config checkout, installed at `~/.claude/agents/` — so the brief stays self-contained for the fallback launch path. Consistent in spirit with `bug-hunt`'s severity reference, but this file is the authority for merge-gate decisions.)

## The three grades

| Grade | Meaning | Merge gate |
|---|---|---|
| **critical** | Data loss, security exposure, crash or wrong results on a realistic path. | Blocks. Fixed-and-verified, or waived by Kyle by name — no other exit. |
| **should-fix** | A real defect or contract violation a user or maintainer will plausibly hit; bounded blast radius. | Blocks until fixed or Kyle-waived. |
| **nice-to-have** | Valid but unimportant: style, naming, micro-perf, a latent edge with no live path. | Never blocks. Never auto-fixed. Listed as follow-ups in the PR comment. |

**Anti-inflation.** Grade blast radius, not confidence — a finding you're unsure of gets its uncertainty stated in the claim, not a lower grade. Reviewers always come back with *something*; the nice-to-have grade exists precisely so real-but-unimportant findings have somewhere honest to go. A calibrated-low list beats an alarmist one — inflated grades train the author to dispute everything and the judge to discount the reviewer.

## Scope calibration — SKIP / SINGLE ROUND / FULL LOOP (propose-first, updated 2026-08-22)

The loop no longer auto-runs; the session recommends a scope and Kyle decides interactively (unattended, the session decides and records why in the merge brief). This section calibrates the *recommendation* — Kyle's call can override any of it.

**SKIP-worthy** — a diff whose changes are all:

- docs-only **and non-behavioral** (README, code comments, prose no agent executes), or
- pure formatting with no semantic change, or
- config-typo scale (fixing a label, a string, a version bump with no code path implications).

**Lean FULL LOOP** if the diff touches: dependencies or lockfiles, CI/workflow files, auth or permissions, data handling (schemas, migrations, serialization), install-class scripts (anything that runs on someone's machine at setup), or **behavioral/agent-instruction files** — any `CLAUDE.md`, `skills/**`, `agents/**`, `commands/**`, hooks, or `settings*.json`: prose by file type, executable by effect. Ordinary executable code with decent test coverage often earns **SINGLE ROUND** (one reviewer dispatch, self-verified fixes — defined in SKILL.md Phase 0).

**Unattended floor:** behavioral/agent-instruction diffs never get SKIP when Kyle isn't around to veto — at least SINGLE ROUND.

A skip, however arrived at, must be **stated in the merge brief** ("skipped adversarial review: docs-only, Kyle's call" / "…session's call, unattended") — never silent. When in doubt about trivial vs. not, it isn't trivial.
