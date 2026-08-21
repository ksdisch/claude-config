---
name: gauntlet
description: Relay one story through a three-stage agent pipeline — specifier → coder → mutation-hardener — where every stage ends in a gate the orchestrating session runs itself rather than takes on an agent's word, and the run ends in a scorecard rather than a merge. Use when Kyle types /gauntlet or says "run the gauntlet", "relay this story", "run this story through the pipeline", or asks to build a backlog item through the staged relay instead of a single session. Takes a target repo path plus a story (inline text or a backlog-item pointer). NOT for pre-merge review of a finished branch (adversarial-review owns that gate, and the gauntlet's branch still goes through it), not for proactive defect hunts with no story in play (bug-hunt), not for picking what to build next (backlog-hygiene).
---

# Gauntlet

**You are the orchestrator.** Three agents do the work; you run every gate. The relay's whole
value is that a stage advances on a command's exit code, not on an agent's account of itself —
so the gates live here, in Bash, in this session, and nowhere else.

| Stage | Agent | Gate you run |
|---|---|---|
| 1 Specify | `specifier` (opus/high) | **G1** — spec files exist and are shaped like Gherkin |
| 2 Code | `gauntlet-coder` (opus/high) | **G2** — suite exit 0 **and** the diff touches a test file |
| 3 Harden | `mutation-hardener` (sonnet/high, `HARDEN` mode) | **G3** — suite still green **and** no *unaccepted* mutation survivors **in the story's changed lines** (see Stage 3: `PASSED` vs `PASSED-WITH-ACCEPTED(n)`) |

The run produces a branch and a scorecard. It does **not** merge. Merging is the normal git
workflow plus `adversarial-review`, outside this skill — one gate per merge, and the gauntlet's
stages never substitute for it.

## Cross-cutting invariants

These hold at every stage. A stage that cannot satisfy one stops the run; it never proceeds
degraded and quiet.

- **GATES-ARE-LOCAL** — every gate is a command *you* run and read the exit code of. An agent's
  claim that its tests pass is input to your next dispatch, never a substitute for running them.
  If you did not run it this lap, it did not pass. **G3's accepted-survivor path is the one
  documented exception**, and it exists because a mutant no honest test can kill would otherwise
  make that gate unsatisfiable. It is fenced accordingly — see Stage 3 — and it reports under its
  own outcome name, so it can never be counted as a clean pass.
- **LOUD-DEGRADATION** — a missing tool, a skipped check, or a hit cap is named in the scorecard
  by name and reason. Never absorb a degradation to keep the relay moving.
- **STAGE-COMMITS** — each stage's work is committed by you, with a stage-tagged message
  (`stage-1: …`, `stage-2 lap 2: …`), *before* its gate runs. Agents leave the tree dirty and
  report; commit authorship stays in one place so every lap is reproducible and diffable.
  **Never commit while a dispatch is still outstanding. The dispatch returning is the completion
  signal, and it is the only one.** Read the report it returns — that is where the touched paths come
  from, and you need them below. What you must not do is go looking for a completion signal anywhere
  else while the call is in flight: **a tree that has stopped changing is not a finished agent.** An
  agent reading files, composing its report, or sitting between two edits leaves exactly the same
  still tree as one that is done. Committing on that heuristic captures half a lap, sends a partial
  diff into the gate, and makes the gate's result a statement about a state no agent ever produced.
  Separately, and for a different reason: **never open the dispatch's raw transcript file** — the
  returned report is the summary you need, while the transcript behind it is large enough to displace
  the run's own context, and it tells you nothing the report doesn't.
  **Stage paths by name — never `git add -A` or `git add .`.** The names are the ones the stage's
  dispatch specified plus the ones the agent reports touching; new files are staged the same way, since
  everything the relay produces is untracked at the moment you commit it. Naming paths, not
  restricting yourself to tracked ones, is what keeps the probe's permitted scratch files out of the
  story's diff.
- **BRANCH-PINNED** — before and after every dispatch, assert you are still on the story branch.
  Stage agents edit files, so a clean-tree check proves nothing here; the branch name is the
  thing to assert. A stray checkout ends the run.

## Stage 0 — Probe

Run before any dispatch. Its job is to find out whether this repo can be gated at all.

**Precondition — the three agents must resolve in *this* session.** Claude Code loads the agent
registry at session start, so `specifier`, `gauntlet-coder` and `mutation-hardener` are dispatchable
only if their files were on disk before this session began. A session that just wrote or merged them
gets `Agent type 'specifier' not found` at the first dispatch. Reading the roster comes before the
repo probe, because it is about the session rather than the repo and because failing it invalidates
every stage; the dispatch fallback below, if you need it, comes after step 1.

**The check is the session's own agent roster, and `agents/` on disk is not it.** That distinction
*is* the defect: the pilot's three files were on disk and merged to `main`, and all three dispatches
still failed. So a `ls`, a `grep`, or a glance at the checkout returns a pass in precisely the case
that fails, and it is the check you will reach for by reflex. Confirm instead that all three names
appear in the list of available agent types **this session** was given. If you cannot see that list,
or are unsure whether what you are reading is the live roster, settle it by dispatching. `Agent
type '<name>' not found` is the definitive answer, and three cheap dispatches are worth less than a
wasted run — but **two of the three types can write** (`gauntlet-coder` holds `Write` and `Edit`,
`specifier` holds `Write`), and their briefs tell them to produce files. So the probe task is
*"reply with the single word OK and change nothing"*, never a vague one-liner they can read as their
real job, and the probes run **after step 1's clean-tree check**, not before it. Re-assert a clean
tree once they return: a probe that dirtied the repo is a probe that just manufactured the exact
mis-attribution step 1 exists to prevent.

Any that do not resolve → **stop and tell Kyle to re-run from a fresh session.** Do not fall back to
`general-purpose` with the agent's brief pasted in: that fallback silently drops the two things the
agent files exist to guarantee —
`tools:` restrictions are not enforced (the specifier's deliberate lack of `Bash` is what backs its
promise never to claim a test passed, and under the fallback it is prose), and `effort:` cannot be
passed through the `Agent` tool at all, so the subagent inherits this session's. A relay run on that
fallback is not a run of this pipeline, and its scorecard cannot be used as evidence about it.

**The steps are ordered, and the order is load-bearing** — each one acts on state the one before
it established.

1. **Clean tree.** No **tracked** file in the target repo may be modified or staged. Any that are →
   name them and **stop**. A tracked file that is already modified is one an agent may also touch,
   and once it does you cannot tell the two edits apart: the pre-existing work goes into a
   `stage-N:` commit unreviewed, attributed to an agent, on a branch headed for
   `adversarial-review`. Starting clean is what makes every later "the agent changed this" claim
   true. This is the one check BRANCH-PINNED deliberately does *not* make later, so it has to be
   made here.
   **Untracked paths do not stop the run** — real repos carry scratch directories, and refusing to
   start on one would be its own failure. Name them in the run log and leave them alone. What makes
   that safe is the other half of the rule (STAGE-COMMITS): **every stage commit stages paths by
   name, never `-A`**. A scratch file nobody named cannot be swept into a stage commit — while the
   specifier's and coder's brand-new files, which are equally untracked, still get committed because
   they *are* named.
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
5. **Mutation runner can measure this repo.** Stryker for JS/TS, mutmut for Python. Absent →
   install it as a dev dependency, which lands on the story branch created in step 3. **Commit the
   install here, tagged `stage-0`**, rather than leaving it dirty: that is what makes it visible,
   committed, and revertable, and it is what keeps the manifest and lockfile out of Stage 1's
   `stage-1:` commit — where they would be attributed to the specifier, the exact mis-attribution
   step 1 stops the run to prevent. Not installable → the hardener stage cannot gate: name the
   missing tool and stop (unattended), or ask Kyle whether to run two-stage with G3 recorded as
   unavailable (attended). **Never silently skip a stage.**

   **Then prove it can measure, with a trial mutation — "the binary installed" is not a probe.**
   Scope a run to one small source file the existing suite already covers, cap it at a handful of
   mutants, and read the *per-mutant status* out of the JSON report. **The probe passes only when
   mutants die `Killed`.** A run where they die `Timeout` has measured nothing: a timeout kill is the
   clock expiring, not a test catching anything, and it produces a survivor count of zero that looks
   exactly like a well-hardened change. That is a false G3 pass, which is the one failure this whole
   skill is built to refuse.

   The failure mode to expect, because it is the common one: **Stryker's `command` test runner has
   no per-test granularity.** Against a `node --test` repo its dry run reports the entire suite as a
   single test (`Ran 1 tests in …`), after which every mutant re-runs the whole suite. Run several of
   those at once and the machine thrashes: every mutant dies on the clock rather than on an
   assertion. The dry-run line is the cheap early tell — read it before you spend a full run.

   **The resolution is one Stryker config written outside the repo** — the escape clause Stage 3
   grants — carrying the repo's full test command as `commandRunner.command`, **concurrency 1**, and
   a timeout above the suite's measured duration, passed with `--config-file`. The config is needed
   because `--commandRunner.command` is not a recognised flag; the command runner's command can only
   come from a config file. What makes the full suite affordable rather than ruinous is that nothing
   here runs many of them at once, and that Stage 3 mutates **line ranges** rather than whole files —
   see Stage 3. A config written *inside* the repo is the tracked-config degradation Stage 3 refuses:
   same file, wrong side of the boundary.

   Re-probe after configuring. Still dying by timeout rather than detection → **G3 cannot gate this
   repo**: treat it exactly as "not installable" above (stop, or ask Kyle), and record the timing
   evidence rather than a bare "probe failed". Record either way in the run log: the trial's
   killed/timeout split, and the absolute path of the out-of-repo config, since Stage 3 reuses it
   unchanged.
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
files the story branch touched — the diff versus merge-base, minus everything that is not source
the mutation tool can mutate. Concretely, subtract: test files (G2's predicate), everything under
`docs/`, and the dependency manifest and lockfile that Stage 0 step 5 committed. Those exclusions
are not redundant with each other — G2 rules in as many words that `.feature` and QA files are
specifications rather than test files, and a `package.json` is neither a test nor under `docs/` —
so each one names a real thing that otherwise reaches `--mutate`, where Stryker reports noise and
mutmut is likelier to error than to shrug. The general rule, if the branch touched something this
list doesn't name: **the scope is source files the tool can mutate**, and anything else comes out.
Whole-repo mutation is unaffordable and mostly irrelevant to this story. Pass it per run — Stryker
takes `--mutate`, mutmut takes paths. A `stryker.conf.json` carrying a three-file `mutate` list
would be stage-3 work under STAGE-COMMITS, would ride the branch through the merge, and would
leave the target repo with a mutation setup whose near-empty runs look like passes forever after.
That is the silent degradation this skill exists to refuse, arriving by the back door. If some
repo genuinely cannot be scoped without a config file, write it outside the repo and point the
tool at it; if even that is impossible, treat the tracked config as a degradation, name it in the
scorecard, and revert it before the branch leaves the run.

**Narrow at the tool, by line range — not in the report afterwards.** Stryker's `--mutate` takes a
mutation range, not just a path: `file:startLine[:startColumn]-endLine[:endColumn]`. That is the
whole fix for the pilot's load-bearing defect, and it is a command-line flag, so it needs no config
file. Derive the ranges once and keep them for the stage: `git diff -U0` against the merge-base,
restricted to the scope files, taking the **new-side** range from each hunk header. Pass one
`--mutate` entry per range. Nothing moves those ranges while Stage 3 runs — the hardener may not edit
implementation files, and test files are already out of the scope — so one derivation holds for every
lap.

Why it matters, in the pilot's own numbers: the story touched 104 lines of a ~500-line module.
Mutated by file that is **385 mutants and 39 survivors**, every one of the 39 in a function the story
never wrote. Mutated by range it is the mutants inside those 104 lines, and **0 survivors**. Read at
file level the orchestrator dispatches the hardener against a module's accumulated debt, burns both
HARDENER-CAP laps on it, and records a false G3 failure against a change that is in fact fully
hardened. Two units are in play and they must not blur: **`SCOPE` is a file list** — what the `SCOPE`
dispatch parameter carries — while **the gate's unit is a line range**.

A tool with no range support (mutmut) is the fallback path, not the main one: mutate the scope files
and intersect the report against the ranges yourself, keeping only mutants whose reported line falls
inside one. Record that you took the fallback. On that path alone, mutants outside the changed lines
exist; they are a finding about the repo's existing suite, recorded in the scorecard by count and
file, and **never put in the hardener's `SURVIVORS` list** — a lap spent on pre-existing debt is a
lap the story's own survivors don't get, and the hardener has only two. If they look worth acting
on, the instrument is a standalone `mutation-hardener` `AUDIT` dispatch, outside this run.

**One out-of-repo config, and it runs the whole test suite.** Narrowing at the tool is what makes
this affordable, and affordability is what lets the config be simple. Stage 0 established that
`commandRunner.command` can only come from a config file; Stage 3 uses that one config, unedited,
with the repo's **full test command**, **concurrency 1**, and a timeout above the suite's measured
duration. Record its absolute path in the run log.

The arithmetic is the argument. The pilot's disaster was 385 mutants each re-running a full suite,
four to eight at a time — the machine thrashed and every mutant died on the clock. Ranges cut the
mutant count to the tens, and party-line's suite is 7.5 seconds, so tens of mutants run sequentially
in minutes. Once the full suite is affordable there is **no narrowed test list, no second config, and
nothing to confirm**: the tests each mutant faces are simply all of them, which is both the strongest
set available and the only set G3 should be claiming anything about. Every mechanism this stage used
to need for picking, checking and re-checking a subset of tests is deleted rather than fixed, because
the question it answered no longer arises.

### Reading a mutation run

**This applies to every mutation run the stage makes, G3's re-run after each hardener lap included.**
That re-run is where it matters most: the hardener has just added tests, so the suite each mutant
re-executes is longer than the one the first run measured, and that is exactly when mutants start
dying on the clock instead of on an assertion. Three statuses, and conflating any two of them is how
a false pass gets recorded:

- **`Killed`** — a test caught the mutant. This is the only status that is evidence of anything good.
- **`Timeout`** — the instrument failed. The clock expired before any assertion ran, so it is
  **never a survivor and never a pass**. Raise the timeout, confirm concurrency is 1, re-run. If it
  persists, that is Stage 0's "G3 cannot gate this repo" exit arriving late — not a result.
- **`Survived` or `NoCoverage`** — a survivor, and both go to the hardener. Under the full suite
  `NoCoverage` means *no test in the repo executes that line*, which is the harshest finding this
  stage can produce, not a gap in the measurement. Discarding it would let wholly untested new code
  record a clean pass, and G2 does not stop that: it requires only that the diff touch a test file,
  never that the changed lines are covered.

A raw survivor count read straight off the tool's report, without the status split, is never the gate.

**Run the mutation tool first, then dispatch.** Before the first hardener dispatch, run it
yourself over the scope. Two things fall out of this and neither is optional:

- **Zero survivors here ends Stage 3 immediately** — gate passed, no dispatch spent, and the
  scorecard says so. A well-hardened change is a common outcome, not a suspicious one.
- **The hardener is never dispatched without `SURVIVORS`.** Its `HARDEN` mode is written entirely
  against a list; dispatched blind it has nothing to work from and the lap is a no-op, which turns
  the 2-lap budget into 1.

Dispatch `mutation-hardener` in `HARDEN` mode with `REPO_PATH`, `SCOPE`, and `SURVIVORS`. `SCOPE` is
the file list; `SURVIVORS` is **only the survivors inside the changed lines** (file, line, mutator,
what it changed), never every survivor those files produced. It adds or strengthens tests; it may not
edit implementation files.

**Gate G3.** You re-run the mutation tool yourself over the same ranges and read it under *Reading
a mutation run* above — the status split is the gate, not the tool's bare survivor number. That
matters most here: this run follows a hardener lap that lengthened the suite, which is when timeouts
are likeliest and when a zero looks most like success. An agent reporting "all mutants killed" is
not the gate. G3 has **two passing outcomes and they are never recorded as the same one**:

- **`G3: PASSED`** — suite green, changed-line survivor count zero. Fully deterministic.
- **`G3: PASSED-WITH-ACCEPTED(n)`** — suite green, and the only changed-line survivors left are `n`
  you have explicitly accepted. Record it in this form, with the count, everywhere the run is reported.

**Accepted survivors — the named exit, not a silent one.** Some mutants cannot be killed by any
honest test: an *equivalent* mutant (semantically identical to the original), or one killable only
by changing implementation. The hardener reports these rather than working around them, and it is
right to. Without an exit for them G3 would be unsatisfiable in a case Stage 3 itself guarantees
will occur, and a fully-hardened change would burn both laps and record a false failure.

**But be clear-eyed about what accepting one costs.** "This mutant is equivalent" is not an exit
code — it is your judgment about the hardener's claim, and it is the single place in this relay
where a gate turns on a judgment rather than a command's result. That is why it is fenced:

- Accepting is an **explicit, recorded act**. Name the mutant, the reason it cannot be killed, and
  your own assessment of the hardener's claim — not a restatement of it — in the scorecard, under
  LOUD-DEGRADATION.
- The outcome is `PASSED-WITH-ACCEPTED(n)`, never `PASSED`. A run that accepted four survivors and
  a run that killed everything must never produce the same line, least of all in a scorecard being
  used as evidence about the pipeline itself.
- An accepted survivor never silently disappears into a zero, and it never re-laps.

An implementation-only survivor is a **finding about the implementation** — dead code, an
unreachable branch, a defensive check nothing can trigger. Carry it into the scorecard as a finding
for Kyle, not as a gate failure.

Any other failure → redispatch with the surviving mutants inside the changed lines listed.

**Invariant HARDENER-CAP: 2 laps.** Here a lap is **one hardener dispatch plus the gate run after
it** — the pre-dispatch run above is not a lap and never consumes budget, which is the whole point
of moving it ahead of the first dispatch. Cap hit → stop and report the standing survivors by name
in the scorecard.

## Stage 4 — Scorecard

Write `scorecard.md` into the run-log directory:

- Per-stage wall-clock, and the run total.
- Laps per gate, with each lap's gate outcome and the reason it failed.
- Dispatch count.
- Final line coverage against the Stage 0 baseline — **measured, not gated**; say so where you
  report it. No mechanism available → say that, rather than omitting the line.
- Mutants generated / killed / survived / **timed out** / **uncovered** — the last two by name and
  count on every run, never summarised into the survivor number: a `Timeout` is a measurement that
  failed, and an uncovered changed line is the harshest finding this stage can produce. Say whether
  the run was scoped by line range or by whole file, since only the second kind can produce mutants
  outside the story's changed lines, and split those out where it did. Every **accepted survivor** by
  name, with the reason it cannot be killed and your assessment of that reason; every survivor still
  standing at the cap, likewise. On a whole-file run, the mutants outside the changed lines go in as
  a count per file, labelled a standing finding about the repo's existing suite rather than anything
  this run produced or failed.
- Any **implementation findings** the hardener raised — mutants that point at dead code or an
  unreachable branch rather than a test gap.
- Files touched, and the diff size.
- Every degradation, cap, and missing tool, by name (LOUD-DEGRADATION).

Then present it to Kyle. Gloss every identifier on first mention — a survivor called `M14` or a
gate called `G2` means nothing on its own — and give him the absolute path to the run-log
directory plus a copy-pasteable `code <path>` line for the full scorecard.

Kyle's seat is at the scorecard: he reads it and spot-checks. The relay never requires him to
read code mid-run. Every gate but one is an exit code rather than an opinion; the exception is G3's
accepted-survivor path, which is a judgment you make and record — which is why it reports under its
own outcome name, so what he is reading is never ambiguous about which kind it was.

## Autonomy boundary

- ✅ **Without asking:** the probe, creating the story branch and run log, installing the mutation
  runner as a dev dependency **onto the already-created story branch**, all dispatches, all gate
  runs, all stage commits, accepting a survivor on the recorded terms above — named, assessed, and
  reported as `PASSED-WITH-ACCEPTED(n)` rather than as a clean pass — writing and presenting the
  scorecard.
- ⛔ **Never without Kyle:** raising a cap, running two-stage when the mutation runner is missing or
  cannot measure the repo (unattended: stop instead), proceeding past a dirty tree in the target
  repo, merging the story branch, or reporting a gate as passed on an agent's word.
- ⛔ **Never:** substituting `general-purpose` for a stage agent that failed to resolve. Stop and ask
  for a fresh session instead — see Stage 0's precondition for what the substitution silently drops.
- ⛔ **Never:** merging from this skill at all. The branch leaves here unmerged, and goes through
  the repo's normal git workflow including `adversarial-review`.
