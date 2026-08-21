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

**The steps are ordered, and the order is load-bearing** — each one acts on state the one before
it established.

1. **Clean tree.** The target repo's working tree must be clean before anything else. Dirty →
   name what is uncommitted and **stop**. Every later stage commits whatever it finds dirty and
   attributes it to an agent, so pre-existing work would be swept into a `stage-N:` commit
   unreviewed, on a branch headed for `adversarial-review`. This is the one check BRANCH-PINNED
   deliberately does *not* make later, so it has to be made here.
2. **Baseline suite green.** Run the repo's test command on the pre-branch state. Red baseline →
   name the failing tests and **stop**. The gauntlet builds on green; it does not rescue red repos,
   because a red baseline makes every downstream gate meaningless.
3. **Create the story branch** `feat/gauntlet-<slug>` in the target repo. Everything after this
   point writes to it, including the mutation runner install — which is why it comes before step 5
   and not after.
4. **Coverage mechanism present.** Node ≥ 22 has it built in (`--experimental-test-coverage`
   with `--test-coverage-lines=N`; a threshold miss is a nonzero exit, which is what makes it
   usable as a pure exit-code check). Python: `pytest-cov`. Record the baseline coverage number
   in the run log — coverage is **measured, not gated**. Absent → record it as a named degradation
   and **continue**: the scorecard's coverage line becomes "no mechanism available" rather than a
   number. Coverage gates nothing, so its absence never stops the run.
5. **Mutation runner reachable.** Stryker for JS/TS, mutmut for Python. Absent → install it as a
   dev dependency, which lands on the story branch created in step 3 and is therefore visible,
   committed, and revertable. Not installable → the hardener stage cannot gate: name the missing
   tool and stop (unattended), or ask Kyle whether to run two-stage with G3 recorded as unavailable
   (attended). **Never silently skip a stage.**
6. **Open the run log.** Create `~/.claude/gauntlet/<repo-name>/<date>-<slug>/` — outside the repo,
   mirroring the review-mailbox pattern, so the relay's bookkeeping never lands in the story's diff.
   Record the start timestamp, the language, the test/coverage/mutation commands, and every probe
   result above.

No per-repo config file yet. Commands are resolved per run from the repo itself; a `.gauntlet.json`
earns its keep once a second repo runs this.

## Stage 1 — Specify

Dispatch `specifier` with `STORY`, `REPO_PATH`, and the two output paths: `OUT_FEATURE`
(`docs/specs/<slug>.feature`) and `OUT_QA` (`docs/specs/<slug>-qa.md`). It reads the story and
enough of the repo to ground it, then writes both files.

**Gate G1 (structural).** Both files exist, and the `.feature` file contains at least one
`Scenario` with at least one each of `Given`, `When`, and `Then`. Then commit them, and **record
that commit's sha in the run log** — G2 measures against it.

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
2. The diff **from the Stage 1 commit to HEAD** touches at least one test file. Implementation
   without tests fails the gate even when the suite is green — a suite that never exercised the new
   code passing is not evidence.

Two things about condition 2 that the gate is worthless without:

- **The range is stage-2's work only, not the branch diff.** Stage 1 already committed
  `docs/specs/<slug>.feature` and `docs/specs/<slug>-qa.md` into the branch diff. Measured against
  merge-base, the specifier's own output would satisfy a test-file check and the gate would pass on
  a lap that wrote pure implementation — the exact case it exists to catch.
- **"Test file" means a file the suite executes**, resolved from the repo's own layout: for Node,
  `*.test.*` / `*.spec.*` or anything under `test/` or `tests/`; for Python, `test_*.py` /
  `*_test.py` or anything under `tests/`. Never a `.feature` or a QA procedure — those are
  specifications, and `docs/` is excluded outright. If the repo's convention doesn't match either
  list, take the predicate from what its existing test command actually collects, and record the
  predicate you used in the run log.

Failure → redispatch the coder with the gate's *actual output* appended (the failing test names
and messages, or the fact that no test file was touched). Not a summary of it: the raw output is
the thing that makes the next lap land.

**Invariant CODER-CAP: 3 laps.** A lap is one dispatch plus one gate run. Cap hit → stop. The
scorecard records the failure and every lap's gate output; the branch is left as-is for Kyle. A
fourth lap is never taken, and the cap is never raised mid-run.

## Stage 3 — Harden

**Scope the run on the command line, never in a tracked config file.** The scope is the source
files the story branch touched (diff versus merge-base, excluding test files); whole-repo mutation
is unaffordable and mostly irrelevant to this story. Pass it per run — Stryker takes `--mutate`,
mutmut takes paths. A `stryker.conf.json` carrying a three-file `mutate` list would be stage-3 work
under STAGE-COMMITS, would ride the branch through the merge, and would leave the target repo with
a mutation setup whose near-empty runs look like passes forever after. That is the silent
degradation this skill exists to refuse, arriving by the back door. If some repo genuinely cannot
be scoped without a config file, write it outside the repo and point the tool at it; if even that
is impossible, treat the tracked config as a degradation, name it in the scorecard, and revert it
before the branch leaves the run.

**Run the mutation tool first, then dispatch.** Before the first hardener dispatch, run it
yourself over the scope. Two things fall out of this and neither is optional:

- **Zero survivors here ends Stage 3 immediately** — gate passed, no dispatch spent, and the
  scorecard says so. A well-hardened change is a common outcome, not a suspicious one.
- **The hardener is never dispatched without `SURVIVORS`.** Its `HARDEN` mode is written entirely
  against a list; dispatched blind it has nothing to work from and the lap is a no-op, which turns
  the 2-lap budget into 1.

Dispatch `mutation-hardener` in `HARDEN` mode with `REPO_PATH`, `SCOPE`, and `SURVIVORS` (file,
line, mutator, what it changed). It adds or strengthens tests; it may not edit implementation files.

**Gate G3.** You re-run the mutation tool yourself and read the survivor count out of its JSON
report. The gate passes when the suite is still green **and** every remaining survivor is one you
have explicitly accepted (below) — in the ordinary case, when there are none left at all. An agent
reporting "all mutants killed" is not the gate.

**Accepted survivors — the named exit, not a silent one.** Some mutants cannot be killed by any
honest test: an *equivalent* mutant (semantically identical to the original), or one killable only
by changing implementation. The hardener reports these rather than working around them, and it is
right to. Without an exit for them G3 would be unsatisfiable in a case Stage 3 itself guarantees
will occur, and a fully-hardened change would burn both laps and record a false failure. So:
accepting one is an **explicit, recorded act** — you name the mutant, the reason it cannot be
killed, and your assessment of the hardener's claim, in the scorecard, under LOUD-DEGRADATION. An
accepted survivor never silently disappears into a zero, and it never re-laps.

An implementation-only survivor is a **finding about the implementation** — dead code, an
unreachable branch, a defensive check nothing can trigger. Carry it into the scorecard as a finding
for Kyle, not as a gate failure.

Any other failure → redispatch with the surviving mutants listed.

**Invariant HARDENER-CAP: 2 laps.** Cap hit → stop and report the standing survivors by name in
the scorecard.

## Stage 4 — Scorecard

Write `scorecard.md` into the run-log directory:

- Per-stage wall-clock, and the run total.
- Laps per gate, with each lap's gate outcome and the reason it failed.
- Dispatch count.
- Final line coverage against the Stage 0 baseline — **measured, not gated**; say so where you
  report it. No mechanism available → say that, rather than omitting the line.
- Mutants generated / killed / survived. Every **accepted survivor** by name, with the reason it
  cannot be killed and your assessment of that reason; every survivor still standing at the cap,
  likewise.
- Any **implementation findings** the hardener raised — mutants that point at dead code or an
  unreachable branch rather than a test gap.
- Files touched, and the diff size.
- Every degradation, cap, and missing tool, by name (LOUD-DEGRADATION).

Then present it to Kyle. Gloss every identifier on first mention — a survivor called `M14` or a
gate called `G2` means nothing on its own — and give him the absolute path to the run-log
directory plus a copy-pasteable `code <path>` line for the full scorecard.

Kyle's seat is at the scorecard: he reads it and spot-checks. The relay never requires him to
read code mid-run, and never asks him to adjudicate a gate — gates are exit codes, not opinions.

## Autonomy boundary

- ✅ **Without asking:** the probe, creating the story branch and run log, installing the mutation
  runner as a dev dependency **onto the already-created story branch**, all dispatches, all gate
  runs, all stage commits, accepting a survivor on the recorded terms above, writing and presenting
  the scorecard.
- ⛔ **Never without Kyle:** raising a cap, running two-stage when the mutation runner is missing
  (unattended: stop instead), proceeding past a dirty tree in the target repo, merging the story
  branch, or reporting a gate as passed on an agent's word.
- ⛔ **Never:** merging from this skill at all. The branch leaves here unmerged, and goes through
  the repo's normal git workflow including `adversarial-review`.
