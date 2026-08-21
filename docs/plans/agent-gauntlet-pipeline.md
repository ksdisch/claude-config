# Build plan: Agent gauntlet pipeline — three-stage skeleton

**Status:** Planned 2026-08-20 (Fable session). Vision doc: [`../ideas/agent-gauntlet-pipeline.md`](../ideas/agent-gauntlet-pipeline.md). Backlog stub: `BACKLOG.md` → "[Feature] Agent gauntlet pipeline".
**Acceptance bar (from the stub):** a three-stage skeleton (specifier → coder → hardener) runs end-to-end on one real repo with deterministic gates, measured against a plain single-session build of the same story.

This plan settles the vision doc's four open questions, specs the four new files, and defines the pilot protocol. The builder session starts fresh from this file.

---

## 1. The four decisions

### D1 — Orchestration surface: a skill (`skills/gauntlet/`) chaining `Agent` dispatches, with every gate executed by the orchestrating session in Bash

Not a Workflow script, not an autonomous-milestone mode. Two facts decide it:

1. **Gates must be ground truth, not agent testimony.** Workflow scripts cannot execute shell — a gate inside a Workflow would be an agent running `node --test` and *reporting* the result through a schema. An agent's report of a deterministic check is no longer deterministic. When the main session runs the gate itself via Bash, the exit code is the gate. This is the whole point of Bob's design (each stage ends in a deterministic check, not a judgment call), so the surface must not compromise it.
2. **Workflow scripts cannot take timestamps** (`Date.now()` is unavailable by design). The skeleton's acceptance bar is a wall-clock measurement; the skill surface gets timestamps trivially (`date +%s` around each stage).

Also: the 3-stage skeleton is strictly sequential over a single story — `pipeline()` buys nothing. **Workflow is the recorded scale-up path**, not the starting point: when the relay grows stages that can run concurrently (cleaner ∥ QA prep) or relays multiple stories at once, revisit. Not an autonomous-milestone mode because that couples an experiment to a working tool; if the relay proves out, autonomous-milestone can *call* the skill later.

Risk accepted with this choice: the loop logic is model-followed skill text rather than code. Mitigation is the house convention already learned the hard way ([[skill-shell-snippets]] memory): the skill is written as numbered steps with named invariants, no copy-paste shell blocks, and hard iteration caps stated as invariants.

### D2 — Reuse vs. build, per skeleton stage: purpose-build all three agents; reuse decisions recorded for the two non-skeleton stages

| Stage | Decision | Why |
|---|---|---|
| Specifier | **Build** `agents/specifier.md` | Its own vision doc ([`specifier-subagent.md`](../ideas/specifier-subagent.md)) already decided standalone-first, gauntlet-consumes-later. Nothing existing produces Gherkin + a QA procedure. |
| Coder | **Build** `agents/gauntlet-coder.md` (slim) | No existing agent fits (code-simplifier is a cleaner; a bare general-purpose dispatch isn't version-controlled). An agent file pins `model:`/`effort:` per the planner/builder protocol and makes pilot runs reproducible. |
| Hardener | **Build** `agents/mutation-hardener.md`, dual-mode | Satisfies both its vision doc ([`mutation-testing-hardener.md`](../ideas/mutation-testing-hardener.md), which wants a read-only auditor first) and the gauntlet (which needs survivors killed): an `AUDIT` mode (report-only, silent-failure-hunter shape) and a `HARDEN` mode (may add or strengthen **tests only** — implementation files are read-only in both modes). The gauntlet dispatches `HARDEN`; standalone audits dispatch `AUDIT`. |
| Cleaner | Reuse `code-simplifier` plugin | Out of skeleton scope. Recorded per [`cleaner-agent-auto-stage.md`](../ideas/cleaner-agent-auto-stage.md). |
| QA | Extend `/smoke-test` | Out of skeleton scope. Recorded per [`qa-doc-to-executable-script.md`](../ideas/qa-doc-to-executable-script.md). |

### D3 — Tooling probe: Stage 0 of the skill, inline generic checks, loud degradation, no config file yet

The skill's first numbered stage probes the target repo before any dispatch:

1. **Baseline suite green** — run the repo's test command; a red baseline invalidates every downstream gate, so red → name the failures and **stop**. (Deliberately strict: the gauntlet builds on green, it doesn't rescue red repos.)
2. **Coverage mechanism present** — for Node ≥ 22, the built-in `--experimental-test-coverage` / `--test-coverage-lines=N` flags (verified available this session, Node 22.22.3: threshold failure is a nonzero exit — a pure exit-code gate); for Python, `pytest-cov`. Record the baseline coverage number in the run log.
3. **Mutation runner reachable** — *(superseded by the as-built skill: "reachable" is not enough. The 2026-08-20 pilot installed Stryker cleanly and still could not measure the repo, because its `command` runner treats a whole `node --test` suite as one opaque test and every mutant died by timeout rather than detection. The probe now trial-mutates and passes only on `Killed`.)* Stryker for JS/TS (v10.0.0 confirmed on the registry this session), mutmut for Python. Not installed in the target → install as a dev dependency **on the story branch** (a visible, committed, revertable change). Not installable → the hardener stage cannot gate: report the missing tool by name and stop (unattended) or let Kyle choose to run two-stage (attended). **Never silently skip a stage.**
4. Record language, runner, and probe results in the run log.

No `.gauntlet.json` per-repo config yet — that earns its keep once ≥ 2 repos run the gauntlet (same logic the threshold-registry decision uses in [`agent-tuned-thresholds.md`](../ideas/agent-tuned-thresholds.md)).

### D4 — The human sits at the scorecard; adversarial-review remains the merge gate, undisturbed

- The gauntlet is a **build-time** quality loop. Its output branch, if it is to merge, goes through the standing `adversarial-review` loop exactly like any other branch. One gate per merge = the review loop, unchanged. **The gauntlet's stages never substitute for it.**
- Kyle's seat is Bob's seat: he reads the run scorecard (stage timings, laps per gate, survivor counts, gate outcomes) and spot-checks; the relay never requires him to read code mid-run.
- The substitution question (does a future QA stage ever replace the review loop?) **re-opens only after the QA stage exists and has a track record** — recorded here as deferred, per the vision doc's instruction that this is a decision to record, not assume.
- Per-audience thresholds ([`agent-tuned-thresholds.md`](../ideas/agent-tuned-thresholds.md)): not triggered — the skeleton's gates are binary (suite green; survivors = 0, counted inside the changed lines per §4.1), not numeric. The CLAUDE.md threshold sentence ships with the first *numeric* gate (the CRAP-score gate), not with this.

---

## 2. Pilot repo and story

**Repo: `~/Projects/party-line`** — chosen over every other candidate after a live survey (2026-08-20):

- 919 tests, 0 failures, 7.5 s wall-clock, via native `node --test` — no DB, no Docker, no infra. (personal-health-elt has pytest-cov wired but its *entire* 260-test suite skips without Postgres; clinical-data-etl has 4 pre-existing failures — both disqualifying for a gate pilot.)
- Node 22 native coverage with exit-code thresholds; 98.44 % line-coverage baseline measured this session.
- Zero runtime dependencies — Stryker installs clean as the only devDependency.

**Story (recommended): the "quiet on purpose vs. broken" contract change** — sub-item (i) of party-line's open backlog item "[Build] Loop-in integrity": the two flows currently collapse three not-sent reasons (`user_present`, `config_off`, `no_transport`) into one silent success, so a dropped Remote Control bridge reads as everything working. Distinguishing them is a real S/M-sized feature: pure JS, unit-testable behavior, no attended leg, real backlog value. Builder: read the full stub (`~/Projects/party-line/BACKLOG.md`, "Loop-in integrity") before committing to it; sub-items (ii) (needs Kyle with phone in hand) and (iii) (touches a Python driver) are **not** part of the pilot story. Fallback criteria if (i) proves unsuitable on close read: small, JS-only, unit-testable, no external service, real backlog item.

---

## 3. File specs

Four new files in claude-config, all behavioral (skills/agents — the class that can never skip adversarial review). Doc-sync rule fires: 4 rows in `docs/command-skill-reference.md` + 4 cards in `docs/usage-playbook.md`, same branch.

### 3.1 `skills/gauntlet/SKILL.md` — the orchestrator

Frontmatter `description`: triggers on `/gauntlet`, "run the gauntlet", "relay this story"; NOT for pre-merge review (adversarial-review), not for proactive defect hunts (bug-hunt). Input: target repo path + a story (inline text or a backlog item pointer).

Body, as numbered stages with named invariants (**no copy-paste shell blocks** — the [[skill-shell-snippets]] lesson):

- **Stage 0 — Probe** (per D3). Also: create the story branch in the target repo (`feat/gauntlet-<slug>`), create the run log directory `~/.claude/gauntlet/<repo-name>/<date>-<slug>/` (outside the repo, mirroring the reviews-mailbox pattern), record start timestamp.
- **Stage 1 — Specify.** Dispatch `specifier` with the story text and repo path. It writes two files into the repo: `docs/specs/<slug>.feature` (Gherkin) and `docs/specs/<slug>-qa.md` (human-POV QA procedure). **Gate G1 (structural):** both files exist; the `.feature` file contains ≥ 1 `Scenario` with at least one each of `Given`/`When`/`Then`. Orchestrator commits them with a stage-tagged message. G1 is honest about what it can check — spec *presence and shape*, not spec *quality*; spec quality is judged by whether the coder's tests satisfy Kyle at the scorecard.
- **Stage 2 — Code.** Dispatch `gauntlet-coder` with the story, the Gherkin file path, and repo conventions pointer (CLAUDE.md). It writes unit tests + implementation and runs the suite itself as it works. **Gate G2 (run by the orchestrator, not trusted from the agent):** full suite exit 0 **and** the branch diff touches at least one test file (implementation-without-tests fails the gate). Failure → redispatch the coder with the gate's actual output appended. **Invariant CODER-CAP: max 3 laps** (a lap = one dispatch + one gate run). Cap hit → stop, scorecard records the failure, branch left as-is for Kyle.
- **Stage 3 — Harden.** *(As-built supersedes this bullet on two points, both from the 2026-08-20 pilot — the skill is authoritative: (a) the Stryker scope is passed **per run on the command line**, never written into a tracked config, and where a config is unavoidable it lives outside the repo; (b) **G3 counts only mutants inside the branch's changed lines**, not every mutant in the touched files — at file level the pilot saw 39 survivors against 0 in the story's own lines. See §4.1.)* Orchestrator scopes the mutation run to the source files the story branch touched (diff vs merge-base — keeps runtime sane, matches the hardener vision doc's diff-scope decision), then dispatches `mutation-hardener` in `HARDEN` mode. **Gate G3:** orchestrator runs Stryker itself and reads the survivor count from the JSON report — survivors = 0 **and** suite still green. Failure → redispatch with the surviving mutants listed. **Invariant HARDENER-CAP: max 2 laps.** Cap hit → stop and report.
- **Stage 4 — Scorecard.** Write `scorecard.md` to the run log dir: per-stage wall-clock, laps per gate, gate outcomes per lap, dispatch count, final coverage vs baseline (measured, **not** gated — the vision doc names "tests green + mutation survivors = 0" as the skeleton's only gates), mutants generated/killed/survived, files touched. Present it to Kyle (glossed per the no-bare-identifiers rule). The branch does **not** merge here — merging is the normal git workflow + adversarial-review, outside the skill.

Cross-cutting invariants, stated once in the skill: **GATES-ARE-LOCAL** (every gate is a command the orchestrator runs; an agent's claim that a gate passes is never accepted); **LOUD-DEGRADATION** (a missing tool or hit cap is always named in the scorecard, never absorbed); **STAGE-COMMITS** (each stage's work is committed with a stage-tagged message before its gate runs, so laps are reproducible and diffable); **BRANCH-PINNED** (before/after every dispatch, assert still on the story branch with no stray checkouts — stage agents edit files, so this replaces adversarial-review's stricter untouched check).

### 3.2 `agents/specifier.md`

- Frontmatter: `tools: Read, Grep, Glob, Write` (no Bash — it reads conventions and writes two files, nothing more); `model: opus`, `effort: high` (the wrong-thing-catcher is the highest-leverage stage; this is judgment work).
- Inputs: `STORY` (text), `REPO_PATH`, `OUT_FEATURE`, `OUT_QA` (paths chosen by the orchestrator).
- Behavior: read the story and enough of the repo to ground it (existing behavior, naming, test conventions); write the Gherkin acceptance test (concrete, testable scenarios — no "should work correctly" mush) and the QA procedure in Bob's register ("You are a human operating this system at the UI; prove it works"). Return one summary line; the files are the deliverable.
- Standalone use (per its vision doc): also usable outside the gauntlet to sharpen a backlog stub's `Acceptance:` line.

### 3.3 `agents/gauntlet-coder.md`

- Frontmatter: `tools: Read, Grep, Glob, Bash, Write, Edit`; `model: opus`, `effort: high` (well-specified build → Opus, per the protocol).
- Inputs: `STORY`, `FEATURE_PATH` (the Gherkin), `REPO_PATH`, and on re-laps `GATE_OUTPUT` (the failing gate's actual output).
- Behavior: write unit tests for the scenarios and the implementation to pass them; run the suite locally as it works; leave the tree committed... **no — leave the tree dirty and report**; the orchestrator commits (STAGE-COMMITS invariant keeps commit authorship/point-of-record in one place). Never touch files outside the story's scope. Never weaken or delete existing tests to get green — if an existing test genuinely conflicts with the story, stop and report the conflict instead.
- Explicitly *not* line-by-line TDD ritual — outcome gates enforce the values (this is the open "values, not disciplines" question; the gauntlet takes the outcome-gate side by construction and the pilot is evidence for that separate backlog item).

### 3.4 `agents/mutation-hardener.md`

- Frontmatter: `tools: Read, Grep, Glob, Bash, Write, Edit`; `model: sonnet`, `effort: high` (killing survivors is grind-shaped; silent-failure-hunter precedent — revisit to opus if survivors persist at cap).
- Inputs: `MODE` (`AUDIT` | `HARDEN`), `REPO_PATH`, `SCOPE` (files to mutate — the story diff in gauntlet use), `SURVIVORS` (on re-laps: the surviving mutants from the orchestrator's run).
- `AUDIT` mode: run the mutation tool, report survivors graded on the bug-hunt rubric, **edit nothing** (the vision doc's read-only auditor, delivered). `HARDEN` mode: add or strengthen tests to kill the listed survivors; **implementation files are read-only in both modes** — a mutant that can only be killed by changing the implementation is a *finding about the implementation*, reported not "fixed".
- Zero survivors on first run is a valid result — say so plainly; never invent work.

---

## 4. Pilot protocol (the measurement)

Two arms, same story, isolated worktrees, no shared context:

1. **Control arm first** (cheaper; sets the human-baseline-equivalent): one `general-purpose` dispatch (pinned `model: opus`; `effort` **cannot** be pinned per dispatch — it is inherited from the orchestrating session, which §4.1 therefore requires to run at `high`, the same tier as the gauntlet coder, so the comparison measures the *pipeline*, not the model) in a worktree on branch `feat/control-<slug>`, given the **raw story text only** (never the specifier's Gherkin — the specifier is part of the treatment) with "build this as you normally would: implementation + tests, suite green." Wall-clock it.
2. **Gauntlet arm:** run `/gauntlet` per §3.1 on `feat/gauntlet-<slug>`.
3. **Symmetric measurement over both arms** (all deterministic, run by the orchestrating session): full suite pass/fail · line coverage vs. the 98.44 % baseline · Stryker over each arm's touched source files, with survivor counts read **inside each arm's changed lines** (§4.1) and the file-level number recorded beside it as context · diff size · wall-clock · dispatch count.
4. **One symmetric quality judgment:** a single zero-context judge dispatch given both diffs unlabeled ("two implementations of the same story — grade each on the bug-hunt severity rubric"). One dispatch, both arms, no asymmetry. (Running full adversarial-review over both arms would be a better instrument but costs 2 full review loops; not worth it for the skeleton.)
5. **Report:** `docs/reports/2026-XX-XX-gauntlet-pilot.md` in claude-config — scorecard tables for both arms + a verdict paragraph against the acceptance bar. Update the backlog stub with the outcome.
6. Whichever branch is worth landing in party-line goes through party-line's normal git workflow **including adversarial-review** (D4). The other branch is deleted after the report cites its numbers.

**Honest-failure clause:** if the gauntlet arm hits a cap, loses to control on both time and quality, or G1's structural gate proves too weak to matter, the report says so plainly — the backlog stub's bet gets an evidence-based *no* rather than a rescued demo. Bob's own warning is the kill criterion: slower than the human path with no quality delta = lost game.

### 4.1 Second pilot — three arms (added 2026-08-21)

The first pilot ran this protocol and **failed the acceptance bar** ([`../reports/2026-08-20-gauntlet-pilot.md`](../reports/2026-08-20-gauntlet-pilot.md)). Its four pipeline defects are fixed in `skills/gauntlet/SKILL.md`; the re-run changes the protocol in three ways.

1. **A third arm, to price the specifier.** The judge called the gauntlet arm the over-engineered one while the unguided control arm found the same constraint and handled it better — plausibly because 18 Gherkin scenarios plus "every scenario needs a test" over-specifies a small story. That is an inference, and the way to settle it is to measure it. The arms are: **control** (one `general-purpose` dispatch, raw story only, exactly as step 1 above specifies), **coder-only** (the coder's brief and the G2/G3 gates, but no spec and no specifier), and **full gauntlet**. If coder-only matches or beats full gauntlet at lower cost, the skeleton is not three stages needing repair — it is one stage that works and two that don't.

   **How the coder-only arm is actually dispatched, because the obvious reading doesn't run.** `agents/gauntlet-coder.md` refuses a spec-less dispatch by design — *"Dispatched without a readable `FEATURE_PATH`, report that and stop. Building without the spec defeats the relay."* — so "the coder with the raw story instead of the `.feature`" produces nothing. Dispatch this arm the way the control arm is dispatched instead: **`general-purpose`, pinned `model: opus`, with the coder's brief pasted verbatim minus its `FEATURE_PATH` clauses and its every-scenario-needs-a-test rule**, then run G2 and G3 over the result exactly as the skill specifies. That also makes the experiment cleaner than the alternative, because control and coder-only then share a dispatch mechanism and differ *only* in the brief and the gates — which is the thing being measured. **The named asymmetry:** this arm's `tools:` restrictions are unenforced (a `general-purpose` subagent gets the full tool set, where the real `gauntlet-coder` is held to Read/Grep/Glob/Bash/Write/Edit), so the full-gauntlet arm is the only one running under real tool restrictions. Record it in the report rather than letting the judge comparison carry it silently.

   **Precondition on the orchestrating session: run it at `--effort high`.** `effort` cannot be passed per dispatch, so every `general-purpose` arm inherits the session's — the first pilot matched the agent files' `effort: high` *by coincidence, not by mechanism*, and its own report says so. Pinning the session is what turns that coincidence into the mechanism, and without it the headline comparison quietly becomes a model-tier comparison instead of a pipeline one.
2. **Every arm's worktree lives outside the target repo.** The first pilot put the control worktree at `party-line/.claude/worktrees/`, inside the tree the gauntlet coder greps; the coder surfaced the control arm's `PROJECT.md` / `BACKLOG.md` prose describing that arm's approach and disclosed it unprompted. The deterministic measurements survive that, but no independence claim about the *approach* does. Put every arm under a sibling directory (e.g. `~/Projects/_gauntlet-arms/<slug>-<arm>/`) so no arm can reach another by path.
3. **Mutation is measured at changed-line scope, symmetrically.** Each arm is mutated at its own changed-line ranges (`--mutate file:startLine-endLine`, verified supported on the installed Stryker), against the repo's full test suite at concurrency 1 — the same instrument for every arm. The file-level number is recorded beside it as context rather than as the comparison.

Everything else holds: same story text to every arm, same model tier, the step-3 deterministic measures run by the orchestrating session, and **one** unlabeled zero-context judge given all three diffs at once. Run it **from a fresh session** — Stage 0's precondition — with the story picked against: small, JS-only, unit-testable, a real backlog item, and no attended leg. **Candidate recorded 2026-08-21:** party-line's `[Chore] One unidentified unit-test failure`, scoped to the half its own acceptance line calls certainly worth fixing — a runner that keeps every `not ok` line with its subtest name instead of `# pass`/`# fail` counts, plus a bounded repeat mode. Flake *identification* is explicitly out of the story. **What this pick does not test, stated up front:** it is all-new `.mjs`, so the changed-line ranges cover the whole module — the file-level and changed-line survivor counts are the same number by construction. The pilot therefore exercises the fresh-session precondition, the trial-mutation probe, the range-scoped `--mutate` run against the full-suite-at-concurrency-1 config, and the commit-timing rule — but returns **no evidence either way** about the changed-line *narrowing*, whose entire content is the difference between those two numbers (39 vs 0 in the first pilot); with the whole module changed, range-scoping and file-scoping coincide. Two ways to close that gap, and it is Kyle's call which: add a second scope file that already exists (so the story edits into pre-existing code), or accept the limitation and record it in the report rather than letting a null result read as a confirmation.

**What a second null result means, stated before the run rather than after:** if the hardener again finds nothing inside the changed lines, the mutation stage is hunting a defect class an Opus-tier coder writing tests alongside implementation does not produce often enough to pay for, and it comes out of the relay to live on as the standalone `AUDIT` auditor its vision doc wanted.

## 5. Build order (builder session)

1. Branch `feat/agent-gauntlet-skeleton` in claude-config.
2. Write the four files (§3) + doc-sync rows/cards, commit.
3. PR + **adversarial-review loop** (behavioral files — no escape hatch), fix/dispute per the skill, merge on CLEAR. End on pulled main (deploy-wiring memory: the symlinks serve the repo checkout).
4. Run the pilot (§4). The gauntlet skill run happens *from* a session whose `~/.claude/skills` already serves the merged files.
5. Write + land the pilot report (docs-only PR, escape hatch stated). Update the backlog stub.

Steps 1–3 and 4–5 may be separate sessions if context runs long; the seam is after the merge in step 3.

## 6. Deferred, recorded

- Cleaner + QA stages (own vision docs; skeleton must prove the relay first).
- CRAP/complexity numeric gates + the per-audience threshold sentence (ship together).
- `.gauntlet.json` per-repo config (≥ 2 repos).
- Workflow-tool orchestration (when stages parallelize).
- Stop-hook enforcement of gates (the skill's in-loop gates are the skeleton's mechanism; a Stop-hook loop is the harden-later option per [`crap-score-gate.md`](../ideas/crap-score-gate.md)).
- QA-substitutes-for-adversarial-review question (re-opens only with a QA-stage track record).

---

**Run-config note:** builder session on **Opus 5, effort high** — this is a well-specified multi-file build plus a long-running pilot execution; the judgment calls are settled above. Start fresh from this plan file, never from the planning transcript. Launch: `claude --model claude-opus-5 --effort high` in `~/Projects/claude-config`.
