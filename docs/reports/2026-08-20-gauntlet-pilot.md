# Agent gauntlet pipeline — skeleton pilot report

**Date:** 2026-08-20 · **Plan:** [`../plans/agent-gauntlet-pipeline.md`](../plans/agent-gauntlet-pipeline.md) · **Skeleton PR:** [#102](https://github.com/ksdisch/claude-config/pull/102)
**Pilot repo:** `~/Projects/party-line` · **Story:** BACKLOG "[Build] Loop-in integrity", sub-item (i) — distinguish "quiet on purpose" from "broken" in the not-sent caller contract.

**Acceptance bar (from the backlog stub):** *a three-stage skeleton (specifier → coder → hardener) runs end-to-end on one real repo with deterministic gates, measured against a plain single-session build of the same story.*

---

## Verdict

**The skeleton did not run end-to-end.** Stages 0, 1 and 2 ran and their gates passed on real exit codes. **Stage 3 never dispatched its agent**, because the gate it depends on was measuring the wrong thing — and by the time that was established, the answer was already known from the measurement itself.

**Against the plain build, the gauntlet lost on time, tied on the deterministic measures, and lost narrowly on judged quality.** It took **6.7× the wall-clock** (1 h 35 m vs 14 m 13 s) and produced an outcome indistinguishable from the control arm on every deterministic axis — including the one the third stage exists to move: mutation survivors in the story's own changed lines were **zero in both arms**. An unlabeled zero-context judge, given both diffs, preferred the **control** arm by a modest margin, and named the gauntlet arm as the over-engineered one.

Bob's own kill criterion — *slower than the human path with no quality delta* — is met. This is an evidence-based **no** on the skeleton as specified, and the plan's honest-failure clause governs: no demo is being rescued here.

What the pilot *did* buy is worth more than the run: four specific, fixable defects in the design, three of them invisible until a real repo was put through it. They are listed under [What broke](#what-broke) and they are the reason this is a "fix and re-run" rather than an "abandon".

---

## The measurements

Both arms built the same story from the same text, in isolated worktrees, at the same model tier (opus / high). Every number below was produced by a command run by the orchestrating session, not reported by an agent.

| Axis | Control arm | Gauntlet arm | Winner |
|---|---|---|---|
| **Wall-clock** | **14 m 13 s** | 1 h 35 m | Control, 6.7× |
| **Agent dispatches** | **1** | 2 (specifier, coder) + 0 hardener | Control |
| **Suite** | exit 0 · 932 pass, 0 fail (+13) | exit 0 · 946 pass, 0 fail (+27) | Tie (both green) |
| **Line coverage** (baseline 98.44 %) | 98.46 % | 98.47 % | Tie |
| **Mutation survivors — story's changed lines** | **0** | **0** | **Tie** |
| Mutation survivors — pre-existing lines in the same file | 40 | 39 | — (neither arm's work) |
| **Diff** (excluding lockfile) | 13 files, +430 / −50 | 13 files, ~+552 | Control, marginally |
| **Unlabeled judge** | preferred | — | **Control**, modest margin |
| Extra artifacts | — | Gherkin spec (18 scenarios) + human QA procedure | Gauntlet |

Mutation runs used an identical Stryker 10.0.0 configuration against both arms — 385 mutants over `handoff/notify.mjs` for the gauntlet arm, 373 for the control arm, 0 timeouts in each.

### The number that decides it

The hardener stage exists to drive mutation survivors in the new code to zero. **The control arm's plain, unguided build already had zero survivors in its changed lines.** So did the gauntlet arm's. On this story, on this repo, the third stage had nothing to do — and a stage with nothing to do cannot justify 6.7× the wall-clock.

One story is not a sample. But it is the story the plan chose, on the repo the plan chose, and it says something specific: **when an Opus-tier coder writes tests alongside the implementation, the marginal defect the mutation stage is hunting may simply not be there.**

---

## Judge assessment (unlabeled)

A single zero-context judge was given both diffs with no arm labels, told they were two implementations of the same story, and asked to grade each on the house `bug-hunt` severity rubric.

It applied both diffs to `main` in isolated trees, ran the suite in each, and mutation-checked the tests by flipping the classification logic to see what went red. Its finding IDs below are its own.

**Verdict: the control arm is better, by a modest margin — "not a rout."** Both satisfy the acceptance line, both err in the correct direction on an unknown `disabledReason` (toward speaking up), both keep retry ruled out and the ask ungated, and both test suites die under the mutations that matter.

| Axis | Winner | Judge's margin |
|---|---|---|
| Doc coherence — no stale instruction left behind | **Control** | Clear |
| Honouring the §14.3 adjacency constraint | **Control** | Clear |
| Scope discipline | **Control** | Moderate |
| Cross-reference integrity | Gauntlet | Clear |
| Accuracy of the composed sentences | Gauntlet | Moderate |
| Test coverage breadth | Gauntlet | Narrow |

Two findings matter for what the gauntlet is *for*:

- **The gauntlet arm was the over-engineered one.** The judge called it "the clearest instance in either diff": four keys beyond the story's three reasons, per-form closing lines, and a stacking rule that can produce a four-sentence ~330-character notice where the surrounding contract's idiom is "one plain line." One key (`also-desktop-dark`) it judged **unreachable by measurement** — `localSent` is always true in these interactive-only flows, so that key, its clause, its design paragraph and its test cover a state the caller cannot be in.
- **The control arm won on the constraint the specifier was proudest of finding.** The specifier correctly identified that §14.3 forbids any tool call between the push and the ask. But the gauntlet coder resolved it by relaxing the rule in prose while leaving the absolute wording standing beside the relaxation in both skill docs; the control arm sidestepped it entirely by putting the sentence inside the ask text, which the judge found "compliant under any reading."

Also worth recording: the judge found one of the gauntlet arm's 27 new tests passes unchanged against the old code (a scope guard, not a behaviour pin), and one CLI test tautological — it asserts the CLI's output equals the function that produced it. **Neither is something G2 or G3 could catch.** G2 checks that a test file was touched; G3 checks mutation survivors in changed lines, and both arms had zero. A test that pins nothing still contributes to a green suite and a clean mutation score.

**An inference, flagged as such:** the gauntlet arm's over-engineering is plausibly *caused by* its own specifier. Eighteen Gherkin scenarios is a larger surface than the story needed, and a coder told "every scenario needs a corresponding unit test" will build to all eighteen. If that holds up on a second story, the specifier stage has a cost the plan didn't price — it converts an under-specified story into an over-specified one, and the coder pays.

---

## What broke

Four defects, each named rather than absorbed (the skill's own LOUD-DEGRADATION rule). Three are in the pipeline; one is in how I ran the pilot.

### 1. Stage 3 scopes mutation testing by **file**, when the gate means **changed lines**

The load-bearing defect, and the reason Stage 3 never dispatched.

`skills/gauntlet/SKILL.md` Stage 3 scopes the mutation run to "the source files the story branch touched." The story touched 104 lines of `handoff/notify.mjs` — a ~500-line pre-existing module. File-level scope drags that whole module's accumulated mutation debt into the gate:

| Scope | Survivors | G3 outcome |
|---|---|---|
| File-level (as specified) | 39 | **FAILED** |
| Changed-line-level (what the gate means) | **0** | **PASSED**, no dispatch spent |

Followed literally, the orchestrator dispatches `mutation-hardener` against 39 survivors in `oneLine()`, `clip()`, `composePushMessage()` and `composeSlackMessage()` — code this story never wrote — burns both HARDENER-CAP laps on pre-existing debt, and records a false "G3 failed" against a change that is in fact fully hardened.

Stage 3 was **stopped rather than run to the cap**: spending two dispatches to confirm an already-determined result is waste, not evidence.

**Fix:** scope G3 to mutants whose line falls inside the branch's changed-line ranges. The intersection is cheap — the pilot computed it in one short script against Stryker's JSON report.

### 2. Stryker cannot measure a `node --test` repo without an out-of-repo config, and the probe never asked

D3 specified the probe as checking whether a mutation runner is **reachable**. Stryker installed cleanly, so the probe passed. The real question is whether it can **measure the repo**, and the answer was no:

Stryker's `command` test runner has no per-test granularity — its dry run reports `Ran 1 tests in 8 seconds`, treating the entire 946-test suite as one opaque test. Two full runs were abandoned after **every mutant died by timeout rather than by detection** (131/132, then 40/40 even at a 25-second timeout): four to eight concurrent full-suite runs thrash the machine. A timeout kill is not evidence that a test caught anything.

Roughly **45 of the gauntlet arm's 95 minutes** went into discovering this. The resolution was a Stryker config written **outside** the repo — which the skill's own escape clause permits — pointing `commandRunner.command` at the three covering test files. That produced the clean 385-mutant run. It cannot be done on the command line: `--commandRunner.command` is not a recognised flag.

**Fix:** Stage 0's mutation probe must run a **timed trial mutation** (a handful of mutants) and check that mutants die by *detection*, not by timeout — and it must know that a `node --test` repo needs the out-of-repo config with a scoped command. "The binary installed" is not a probe.

### 3. Agent files merged in a session are not dispatchable in that session

All three agent types — `specifier`, `gauntlet-coder`, `mutation-hardener` — failed to resolve: `Agent type 'specifier' not found`. They had been merged to `main` earlier in the same session, but Claude Code loads the agent registry at session start.

Fallback used: `general-purpose` with each brief pasted verbatim, the pattern `adversarial-review` already documents. What that costs, stated rather than hidden:

- `model:` passed by hand instead of read from frontmatter.
- `effort:` cannot be passed through the `Agent` tool at all — the subagent inherits the session's. It matched all three files' `effort: high` **by coincidence, not by mechanism**.
- **`tools:` restrictions are not enforced.** The specifier's file deliberately grants no `Bash` — that restriction is what backs its promise never to claim anything about tests passing. Under the fallback it had the full tool set, and the restriction was prose.

**Fix:** the plan's build order already has the right shape (merge in step 3, pilot in step 4) but not the right granularity — the pilot needs a **fresh session**, and the skill should say so in Stage 0.

### 4. The orchestrator committed mid-dispatch (my error, and a gap in the skill)

The first stage-2 commit (`0e959fd`) was taken on a tree-stability heuristic while the coder was still working, capturing only the code-and-tests half; G2 ran against a partial commit. The rest of the same dispatch landed in `878d7ea` and G2 was re-run on the complete work. Both commits are **one lap** — one dispatch produced all of it.

The skill made this easy to get wrong: STAGE-COMMITS says agents "leave the tree dirty and report" but never says **wait for the agent's report before committing**.

**Fix:** one clause in STAGE-COMMITS.

### 5. The two arms are contaminated (pilot setup, not pipeline)

I placed the control worktree at `.claude/worktrees/control-quiet-vs-broken` — **inside the repo the gauntlet coder searches**. Its grep for `disabledReason` surfaced the control arm's `PROJECT.md` / `BACKLOG.md` / `HANDOFF.md` prose describing that arm's approach.

The coder stopped there, did not read the control's source, and disclosed the exposure unprompted in its report. But the two designs converge on high-level shape — both compose `not-sent-<reason>=` lines in `notify.mjs` and print them *before* the push — so **no independence claim can be made about the approach**. The clause wording, key scheme and tests differ.

This does not affect the deterministic measurements (timing, suite, coverage, mutation), which are what the verdict rests on. It does weaken the judge's comparison.

**Fix:** put control worktrees outside the target repo.

---

## What worked

Stated plainly, because the failure above is not total:

- **The gates were real.** Every one was a command the orchestrating session ran and read an exit code from. No stage advanced on an agent's account of itself. G2 in particular caught something worth catching: it re-ran and re-verified after the partial-commit error, on actual output.
- **G1 did its job at its stated reach.** 18 scenarios with Given/When/Then, verified structurally. The skill is honest that this checks shape and not quality, and that honesty held up — the spec's quality showed up downstream, in the coder's 27 tests.
- **The specifier surfaced a real constraint** the story text never mentioned: §14.3 forbids any tool call between the push and the ask, so the "broken doorbell" notice cannot be a tool call. It also recorded eight assumptions (A1–A8) rather than papering over them. **But the control arm found the same constraint unaided and handled it better** (see the judge section), so this pilot cannot claim the stage paid for itself — only that it wasn't idle.
- **`stage-N:` commits made the run diffable.** Reconstructing exactly what each stage produced, including the partial-commit error, was mechanical.
- **Staging paths by name kept the tree clean.** Stryker's `.stryker-tmp/` and `reports/` appeared mid-run as untracked directories and stayed out of every stage commit without any special handling — the round-3 review fix (F15) working exactly as intended in the field.

---

## Recommendation

**Fix the four pipeline defects and re-run the pilot on a second story, in a fresh session, before drawing a conclusion about the idea.** The skeleton failed here, but three of the four failures are configuration-shaped rather than conception-shaped, and the fourth (file-vs-line scope) is a ten-line change.

What the re-run must *not* assume: that a second story will produce a survivor for the hardener to kill. If a fixed pipeline runs clean and the hardener still finds nothing on a second and third story, that is the real answer — **the mutation stage is hunting a defect class that an Opus-tier coder writing tests alongside implementation does not produce often enough to pay for.** The honest move then is to drop the hardener from the relay and keep it as the standalone `AUDIT`-mode auditor its own vision doc originally wanted.

**The specifier stage is on notice too, and that is the pilot's least expected result.** It was supposed to be the highest-leverage stage. Instead the judge found the gauntlet arm over-engineered, with one feature unreachable by measurement, while the unguided control arm hit the same constraint and handled it better. The plausible mechanism — flagged as inference, not fact — is that 18 scenarios plus "every scenario needs a test" converts an under-specified story into an over-specified one. **The second pilot should measure this directly:** compare a gauntlet run against a run of coder-plus-gates with no specifier. If the specifier is a net negative, the skeleton isn't three stages that need fixing; it's one stage that works and two that don't.

Two things the gates provably cannot catch, which bound how much any version of this pipeline can promise: the judge found one gauntlet test that passes unchanged against the old code and one that is tautological. G2 checks that a test file was touched; G3 checks mutation survivors. A test that pins nothing satisfies both.

The 39 pre-existing survivors in `handoff/notify.mjs` are, separately, a real standing finding about party-line's test suite: its markdown-stripping regexes, code-point clipper, and Slack clipping fallback are executed by tests but not pinned by them. Worth a `mutation-hardener` `AUDIT` dispatch on its own.

---

## Artifacts

| What | Where |
|---|---|
| Gauntlet run log + scorecard | `~/.claude/gauntlet/party-line/2026-08-20-quiet-vs-broken/` |
| Out-of-repo Stryker config (the one that worked) | same directory, `stryker.conf.json` |
| Gauntlet arm branch (unmerged) | party-line `feat/gauntlet-quiet-vs-broken` — 4 commits, `83cbc85` → `878d7ea` |
| Control arm branch (unmerged) | party-line `feat/control-quiet-vs-broken` — 1 commit, `3d581b7` |
| Gherkin spec + QA procedure | on the gauntlet branch, `docs/specs/quiet-vs-broken.feature` and `-qa.md` |

Open the scorecard with `code ~/.claude/gauntlet/party-line/2026-08-20-quiet-vs-broken/scorecard.md`.

**Neither branch has been merged.** Per plan decision D4 the gauntlet never self-merges; whichever arm is worth landing goes through party-line's own git workflow including `adversarial-review`. That decision is Kyle's and is not made by this report.
