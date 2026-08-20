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
3. **Mutation runner reachable** — Stryker for JS/TS (v10.0.0 confirmed on the registry this session), mutmut for Python. Not installed in the target → install as a dev dependency **on the story branch** (a visible, committed, revertable change). Not installable → the hardener stage cannot gate: report the missing tool by name and stop (unattended) or let Kyle choose to run two-stage (attended). **Never silently skip a stage.**
4. Record language, runner, and probe results in the run log.

No `.gauntlet.json` per-repo config yet — that earns its keep once ≥ 2 repos run the gauntlet (same logic the threshold-registry decision uses in [`agent-tuned-thresholds.md`](../ideas/agent-tuned-thresholds.md)).

### D4 — The human sits at the scorecard; adversarial-review remains the merge gate, undisturbed

- The gauntlet is a **build-time** quality loop. Its output branch, if it is to merge, goes through the standing `adversarial-review` loop exactly like any other branch. One gate per merge = the review loop, unchanged. **The gauntlet's stages never substitute for it.**
- Kyle's seat is Bob's seat: he reads the run scorecard (stage timings, laps per gate, survivor counts, gate outcomes) and spot-checks; the relay never requires him to read code mid-run.
- The substitution question (does a future QA stage ever replace the review loop?) **re-opens only after the QA stage exists and has a track record** — recorded here as deferred, per the vision doc's instruction that this is a decision to record, not assume.
- Per-audience thresholds ([`agent-tuned-thresholds.md`](../ideas/agent-tuned-thresholds.md)): not triggered — the skeleton's gates are binary (suite green; survivors = 0), not numeric. The CLAUDE.md threshold sentence ships with the first *numeric* gate (the CRAP-score gate), not with this.

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
- **Stage 3 — Harden.** Orchestrator writes/updates the Stryker config scoped to the source files the story branch touched (diff vs merge-base — keeps runtime sane, matches the hardener vision doc's diff-scope decision), then dispatches `mutation-hardener` in `HARDEN` mode. **Gate G3:** orchestrator runs Stryker itself and reads the survivor count from the JSON report — survivors = 0 **and** suite still green. Failure → redispatch with the surviving mutants listed. **Invariant HARDENER-CAP: max 2 laps.** Cap hit → stop and report.
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

1. **Control arm first** (cheaper; sets the human-baseline-equivalent): one `general-purpose` dispatch (pinned `model: opus`, `effort: high` — same tier as the gauntlet coder, so the comparison measures the *pipeline*, not the model) in a worktree on branch `feat/control-<slug>`, given the **raw story text only** (never the specifier's Gherkin — the specifier is part of the treatment) with "build this as you normally would: implementation + tests, suite green." Wall-clock it.
2. **Gauntlet arm:** run `/gauntlet` per §3.1 on `feat/gauntlet-<slug>`.
3. **Symmetric measurement over both arms** (all deterministic, run by the orchestrating session): full suite pass/fail · line coverage vs. the 98.44 % baseline · Stryker over each arm's touched source files with survivor counts · diff size · wall-clock · dispatch count.
4. **One symmetric quality judgment:** a single zero-context judge dispatch given both diffs unlabeled ("two implementations of the same story — grade each on the bug-hunt severity rubric"). One dispatch, both arms, no asymmetry. (Running full adversarial-review over both arms would be a better instrument but costs 2 full review loops; not worth it for the skeleton.)
5. **Report:** `docs/reports/2026-XX-XX-gauntlet-pilot.md` in claude-config — scorecard tables for both arms + a verdict paragraph against the acceptance bar. Update the backlog stub with the outcome.
6. Whichever branch is worth landing in party-line goes through party-line's normal git workflow **including adversarial-review** (D4). The other branch is deleted after the report cites its numbers.

**Honest-failure clause:** if the gauntlet arm hits a cap, loses to control on both time and quality, or G1's structural gate proves too weak to matter, the report says so plainly — the backlog stub's bet gets an evidence-based *no* rather than a rescued demo. Bob's own warning is the kill criterion: slower than the human path with no quality delta = lost game.

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
