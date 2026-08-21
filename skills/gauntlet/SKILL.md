---
name: gauntlet
description: Relay one story through a three-stage agent pipeline — specifier → coder → mutation-hardener — where every stage ends in a deterministic gate the orchestrating session runs itself, and the run ends in a scorecard rather than a merge. Use when Kyle types /gauntlet or says "run the gauntlet", "relay this story", "run this story through the pipeline", or asks to build a backlog item through the staged relay instead of a single session. Takes a target repo path plus a story (inline text or a backlog-item pointer). NOT for pre-merge review of a finished branch (adversarial-review owns that gate, and the gauntlet's branch still goes through it), not for proactive defect hunts with no story in play (bug-hunt), not for picking what to build next (backlog-hygiene).
---

# Gauntlet

**You are the orchestrator.** Three agents do the work; you run every gate. The relay's whole
value is that a stage advances on a command's exit code, not on an agent's account of itself —
so the gates live here, in Bash, in this session, and nowhere else.

| Stage | Agent | Gate you run |
|---|---|---|
| 1 Specify | `specifier` (opus/high) | **G1** — spec files exist and are shaped like Gherkin |
| 2 Code | `gauntlet-coder` (opus/high) | **G2** — suite exit 0 **and** the diff touches a test file |
| 3 Harden | `mutation-hardener` (sonnet/high, `HARDEN` mode) | **G3** — mutation survivors = 0 **and** suite still green |

The run produces a branch and a scorecard. It does **not** merge. Merging is the normal git
workflow plus `adversarial-review`, outside this skill — one gate per merge, and the gauntlet's
stages never substitute for it.

## Cross-cutting invariants

These hold at every stage. A stage that cannot satisfy one stops the run; it never proceeds
degraded and quiet.

- **GATES-ARE-LOCAL** — every gate is a command *you* run and read the exit code of. An agent's
  claim that its tests pass is input to your next dispatch, never a substitute for running them.
  If you did not run it this lap, it did not pass.
- **LOUD-DEGRADATION** — a missing tool, a skipped check, or a hit cap is named in the scorecard
  by name and reason. Never absorb a degradation to keep the relay moving.
- **STAGE-COMMITS** — each stage's work is committed by you, with a stage-tagged message
  (`stage-1: …`, `stage-2 lap 2: …`), *before* its gate runs. Agents leave the tree dirty and
  report; commit authorship stays in one place so every lap is reproducible and diffable.
- **BRANCH-PINNED** — before and after every dispatch, assert you are still on the story branch.
  Stage agents edit files, so a clean-tree check proves nothing here; the branch name is the
  thing to assert. A stray checkout ends the run.

## Stage 0 — Probe

Run before any dispatch. Its job is to find out whether this repo can be gated at all.

1. **Baseline suite green.** Run the repo's test command. Red baseline → name the failing tests
   and **stop**. The gauntlet builds on green; it does not rescue red repos, because a red
   baseline makes every downstream gate meaningless.
2. **Coverage mechanism present.** Node ≥ 22 has it built in (`--experimental-test-coverage`
   with `--test-coverage-lines=N`; a threshold miss is a nonzero exit, which is what makes it
   usable as a pure exit-code check). Python: `pytest-cov`. Record the baseline coverage number
   in the run log — coverage is **measured, not gated**.
3. **Mutation runner reachable.** Stryker for JS/TS, mutmut for Python. Absent → install it as a
   dev dependency **on the story branch**, so the change is visible, committed, and revertable.
   Not installable → the hardener stage cannot gate: name the missing tool and stop (unattended),
   or ask Kyle whether to run two-stage with G3 recorded as unavailable (attended). **Never
   silently skip a stage.**
4. **Set up the run.** Create the story branch `feat/gauntlet-<slug>` in the target repo and the
   run-log directory `~/.claude/gauntlet/<repo-name>/<date>-<slug>/` — outside the repo, mirroring
   the review-mailbox pattern, so the relay's bookkeeping never lands in the story's diff. Record
   the start timestamp, the language, the test/coverage/mutation commands, and the probe results.

No per-repo config file yet. Commands are resolved per run from the repo itself; a `.gauntlet.json`
earns its keep once a second repo runs this.

## Stage 1 — Specify

Dispatch `specifier` with `STORY`, `REPO_PATH`, and the two output paths: `OUT_FEATURE`
(`docs/specs/<slug>.feature`) and `OUT_QA` (`docs/specs/<slug>-qa.md`). It reads the story and
enough of the repo to ground it, then writes both files.

**Gate G1 (structural).** Both files exist, and the `.feature` file contains at least one
`Scenario` with at least one each of `Given`, `When`, and `Then`. Then commit them.

G1 is deliberately honest about its reach: it checks spec *presence and shape*, not spec
*quality*. Nothing mechanical can tell a sharp scenario from a vague one. Spec quality is judged
downstream — by whether the coder's tests, written from this Gherkin, satisfy Kyle at the
scorecard. Do not dress G1 up as more than it is when you report it.

Failure → redispatch the specifier once with the specific structural defect named. Still failing
→ stop; a specifier that cannot produce a scenario is a signal about the story, not a lap to burn.

## Stage 2 — Code

Dispatch `gauntlet-coder` with `STORY`, `FEATURE_PATH`, `REPO_PATH`, and a pointer to the repo's
conventions (its `CLAUDE.md`). It writes unit tests and implementation, runs the suite as it
works, and leaves the tree dirty. You commit.

**Gate G2.** Two conditions, both yours to check:

1. The full suite exits 0.
2. The branch diff versus merge-base touches **at least one test file**. Implementation without
   tests fails the gate even when the suite is green — a suite that never exercised the new code
   passing is not evidence.

Failure → redispatch the coder with the gate's *actual output* appended (the failing test names
and messages, or the fact that no test file was touched). Not a summary of it: the raw output is
the thing that makes the next lap land.

**Invariant CODER-CAP: 3 laps.** A lap is one dispatch plus one gate run. Cap hit → stop. The
scorecard records the failure and every lap's gate output; the branch is left as-is for Kyle. A
fourth lap is never taken, and the cap is never raised mid-run.

## Stage 3 — Harden

First, scope the mutation run: take the source files the story branch touched (diff versus
merge-base, excluding test files) and write or update the mutation tool's config to mutate only
those. Whole-repo mutation is unaffordable and mostly irrelevant to this story.

Dispatch `mutation-hardener` in `HARDEN` mode with `REPO_PATH`, `SCOPE` (those files), and — on
re-laps — `SURVIVORS`, the surviving mutants from *your* run. It adds or strengthens tests; it may
not edit implementation files.

**Gate G3.** You run the mutation tool yourself and read the survivor count out of its JSON
report — survivors = 0 **and** the suite still green. An agent reporting "all mutants killed" is
not the gate.

Failure → redispatch with the surviving mutants listed (file, line, mutator, what it changed).

**Invariant HARDENER-CAP: 2 laps.** Cap hit → stop and report the standing survivors by name in
the scorecard.

A mutant that survives because only an implementation change could kill it is a **finding about
the implementation**, not a test gap. The hardener reports those rather than working around them;
carry them into the scorecard as findings, and do not let one keep the relay looping.

## Stage 4 — Scorecard

Write `scorecard.md` into the run-log directory:

- Per-stage wall-clock, and the run total.
- Laps per gate, with each lap's gate outcome and the reason it failed.
- Dispatch count.
- Final line coverage against the Stage 0 baseline — **measured, not gated**; say so where you
  report it.
- Mutants generated / killed / survived, and any standing survivors by name.
- Files touched, and the diff size.
- Every degradation, cap, and missing tool, by name (LOUD-DEGRADATION).

Then present it to Kyle. Gloss every identifier on first mention — a survivor called `M14` or a
gate called `G2` means nothing on its own — and give him the absolute path to the run-log
directory plus a copy-pasteable `code <path>` line for the full scorecard.

Kyle's seat is at the scorecard: he reads it and spot-checks. The relay never requires him to
read code mid-run, and never asks him to adjudicate a gate — gates are exit codes, not opinions.

## Autonomy boundary

- ✅ **Without asking:** the probe, creating the story branch and run log, installing the mutation
  runner as a dev dependency on the story branch, all dispatches, all gate runs, all stage commits,
  writing and presenting the scorecard.
- ⛔ **Never without Kyle:** raising a cap, running two-stage when the mutation runner is missing
  (unattended: stop instead), merging the story branch, or reporting a gate as passed on an
  agent's word.
- ⛔ **Never:** merging from this skill at all. The branch leaves here unmerged, and goes through
  the repo's normal git workflow including `adversarial-review`.
