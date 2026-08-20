# Backlog

Ideas and work for `claude-config`. New items land under **## Open**. Full write-ups
live in [`docs/ideas/`](docs/ideas/).

## Open

### [Feature] Session auto-close: the `/launch` companion that reaps finished sessions
- **Why:** `/launch` (PRs #75/#76) made opening sessions one command, but nothing ever closes them — finished Warp windows/tabs accumulate on the desktop until Kyle sweeps them by hand, and the more `/launch` gets used the faster they pile up. Sessions need the ability and insight to close sessions that are *for sure* done being used. The governing asymmetry: a launch mistake costs one ⌘V; a close mistake kills live work. Full write-up in [`docs/ideas/session-auto-close.md`](docs/ideas/session-auto-close.md).
- **Acceptance:** A plan doc in `docs/plans/` settling the four open design questions (Warp close mechanism, what "for sure done" means, where the reaper lives, consent model), then the build it specifies — or the plan session itself ships the build if it turns out light.
- **Size:** M
- **Added:** 2026-08-12
- **Ready to start:** paste the handoff from [`docs/ideas/session-auto-close.md` § Handoff prompt](docs/ideas/session-auto-close.md#handoff-prompt-ready-to-paste). Run on Fable 5 at `xhigh`, **on the Mac** — the feasibility question is a hands-on Warp experiment, and the design questions need deciding before any code.

### [Improvement] Two deferred nice-to-haves from PR #46's review
- **Why:** F4 — the silent-failure dimension shipped in `hunt-engine.template.js` passes the whole `ROOT` while `bug-hunt`'s own slicing rule mandates one slice per finder, so on a 6+-finder repo hunt it overlaps every other slice and must self-bound its coverage (the thing the skill says never to do silently); and because `agentType` resolves the agent definition, that dimension silently inherits `model: sonnet` regardless of session model, putting the one mandated lens on the fan-out's weakest model. F7 — `CLAUDE.md`'s newly-declared owner rung is missing two criteria both dependents attribute to it: `prompt-optimize`'s "long autonomous run where self-verification pays" on `xhigh`/`max`, and the ultracode `/config` prerequisite + silent-degradation caveat that currently live only in `handoff.md` and `ship-and-route`. An incomplete owner sends a reader who obeys "cite here, never each other" to the thinner text. Full record in PR #46's review comment.
- **Acceptance:** F4 — the example dimension shows the sliced form, SKILL.md step 1 says to fan the lens out per subsystem like the others, and the sonnet pin is disclosed so an adapter can override with `model:`. F7 — both clauses added to the owner rungs (a half-line each). Each shipped or explicitly declined with a reason.
- **Size:** S
- **Added:** 2026-07-27

### [Improvement] paper-figures scripts: close the four silent failures found in the first audit
- **Why:** The first real dispatch of `silent-failure-hunter` (over `skills/paper-figures/scripts/`, 2026-07-27) returned four genuine findings, none fixed yet: **(1)** `inject.py:60` prints `injected {len(images)}` — the *manifest* count, not the count actually replaced, so skipped placeholders (unmatched lead-in, missing file) report as success; both injectors already track the real number and discard it. **(2)** `contactsheet.py:65-78` silently falls back to inlining a full-resolution original when a per-image `sips` resample fails, with no log — the exact 26MB regression the script exists to prevent. **(3)** `checks.py:110-115` `except OSError: continue` drops which file couldn't be hashed. **(4)** `contactsheet.py:71-74` and `normalize.py:53-56, 85-89` run `sips` with no `timeout=`, so a hung child blocks forever indistinguishably from slow.
- **Acceptance:** (1) and (2) fixed — injection reports `n/total` and enumerates skips; the resample fallback logs per-file and summarizes. (3) and (4) fixed or declined with a reason. The scripts have a real test suite (`scripts/tests/`), so each fix lands with a test.
- **Size:** M
- **Added:** 2026-07-27

### [Exploration] Fleet manifest + `/reconcile`: make single-source true on demand
- **Why:** Drift between canonical and vendored copies is dangerous only because it's invisible — a declared `fleet.yml` + an on-demand `/reconcile` verb makes single-source (A1) and propagation (A2) checkable by running one command. See [`docs/ideas/fleet-manifest-reconcile.md`](docs/ideas/fleet-manifest-reconcile.md) for the full write-up.
- **Acceptance:** Prototype the credible first step (`fleet.yml` + `commands/reconcile.md` + the `claudify-repo` append-line) and judge whether the bet holds.
- **Size:** L
- **Added:** 2026-06-18
- **Ready to start:** a paste-able session prompt is written and waiting at [`docs/ideas/fleet-manifest-reconcile.md` § Handoff prompt](docs/ideas/fleet-manifest-reconcile.md#handoff-prompt-ready-to-paste). It carries the landmines from the 2026-07-28 purge that a cold session would otherwise re-hit. Run it on Fable 5 at `xhigh` — the five open design questions below need deciding before any code, and the doc's sizing assumption (7 repos) is already wrong (18).
- **Live instance (2026-07-28) — this drift published third-party PII.** Deleting the three `mock-sql-*` commands here (PRs #53, #54) removed them globally, but `/claudify-repo` copies without pruning, so all three stayed live in 18 vendored repos — **13 of them public on GitHub** — including the two real interviewer names the deletion was meant to remove. Confirmed by fetching from `raw.githubusercontent.com`, not just from disk. **Partially remediated** the same day: the three files were purged from the **default branch** of 17 repos via branch + PR + merge (`new-game-project-idea` skipped — duplicate clone of `constellation.git`) and verified absent there through the GitHub API. That first pass **missed every non-default branch** — `.claude/` was vendored long before those branches were cut, and deleting a file on `main` does nothing to a branch tip. A second pass found **78 such branches across 6 public repos** (234 files; `home-base` alone was 67) still serving the names to anonymous HTTP, and remediated them: **55 already-merged branches deleted**, **23 unmerged branches stripped at the tip** via `commit-tree` so no in-flight work was destroyed. A third pass then found the same gap **in this repo** — every prior pass had defined "the fleet" as the 18 vendored repos and assumed the source was clean; 17 of `claude-config`'s own 19 branches were serving the names publicly. Same treatment: **10 merged branches deleted, 7 unmerged stripped at the tip.**
- **Remediation scope, stated exactly.** Clean as of 2026-07-28, verified by `git ls-tree` over every fetched ref plus anonymous HTTP spot-checks: **all branch tips of the 13 public vendored repos, and all branch tips of `claude-config`.** **Not remediated, by decision:** commit history in every repo that ever carried the files — the blobs stay reachable by sha, here included. **Not remediated, tracked as follow-up:** ~95 *local* branches across 14 clones still carry the files (75 with no live remote), so a plain `git push origin <branch>` would republish to a public repo.
- **Three process lessons, all earned the hard way.** (1) "Verified absent" meant *default branches* and was written as if it meant everything — a check must name its own scope or it launders an assumption into a record. (2) The first branch sweep, run through the GitHub API, silently rate-limited and returned a clean **0**. (3) The second sweep used `git cat-file -e "$ref:commands/…"` in **zsh**, where `:c` is a parameter modifier that mangles the argument — it reported 0 of 19 while `git ls-tree` on the same refs found 17. Both false cleans were caught only by contradicting evidence, never by the check itself. **A verification that fails into a passing result is worse than no verification** — and twice here the failure mode was the shell, not the logic. **The drift was invisible for as long as it took someone to look, and the upstream delete gave no signal at all.** That is the bet's whole thesis, now with a worked example: the smallest real first step is a PORT-mode prune — on re-vendor, drop repo-local copies whose global source no longer exists, and remove their advertising rows. Note one edge the manual purge hit: `DogHood/CLAUDE.md` lists every command on a single line, so whole-line deletion would have destroyed 21 unrelated entries; any automated prune needs surgical excision plus a refuse-if-unsure guard.
- **Still outstanding from the same seam:** `.claude/skills/interview-prep/SKILL.md` is vendored into those same 18 repos. It was gitignored here on 2026-07-28 to unpublish it, but the vendored copies remain public. They expose dossier paths under `~/Cowork/second-brain/30-job-search/…` on seven lines, plus the employer name once as an example slug — not the practice-DB path, which the skill never referenced. Same fix, not yet applied.
- **Re-verified 2026-08-04** (cloud doc-hygiene sweep; `git ls-tree` over freshly fetched **default branches** of all 17 public repos — branch tips and private repos not re-swept): still live. 10 public repos carry `.claude/skills/interview-prep/SKILL.md` today — blind-cite, home-base, forge-gap, decay-pin, dim-stage, ghost-patch, constellation, clinical-data-etl, stopwatch, buoy-legal — each exposing the seven dossier-path lines, and 9 of the 10 also still advertise the skill in their `CLAUDE.md`. The good news, same sweep: `mock-sql` remains fully purged — 0 files and 0 `CLAUDE.md` advertising lines on every public default branch — and every project-specific item indexed in `docs/command-skill-reference.md` was confirmed present in its repo (DogHood included, via private read), so the index's unverifiable-by-checker half is verified accurate as of this date.

### [Exploration] The Coliseum: commands earn their keep on lived-invocation evidence
- **Why:** Lived-invocation data (which of the ~29 specs actually fire, overlap, or get hand-corrected) is a sharper curation signal than memory — a usage trace + `/retro` gives the repo its first subtraction pressure (A3 + A4). See [`docs/ideas/coliseum-commands-earn-their-keep.md`](docs/ideas/coliseum-commands-earn-their-keep.md) for the full write-up.
- **Acceptance:** Prototype the credible first step (`/retro` reader over a hand-seeded `usage.jsonl`, then the Stop-hook) and judge whether the bet holds.
- **Size:** L
- **Added:** 2026-06-18

### [Exploration] Telemetry-Forged Commands: the config writes itself from how you actually work
- **Why:** Your transcripts already hold the richest record of what's worth codifying — `/forge` mines repeated hand-driven sequences and drafts new commands as PRs you ratify, flipping authorship from write→propose-and-approve (A3). See [`docs/ideas/telemetry-forged-commands.md`](docs/ideas/telemetry-forged-commands.md) for the full write-up.
- **Acceptance:** Prototype the credible first step (read-only `commands/forge-scan.md` that prints your top 3 "you keep doing this by hand" clusters) and judge whether the signal exists.
- **Size:** L
- **Added:** 2026-06-18

### [Exploration] claude-config as a registry: versioned commands + a lockfile
- **Why:** Vendored copies silently decay and nobody knows how old they are — a `version:` field + a `.claude/claude.lock` turns drift into a readable number (`cc outdated`: "kickoff is 4 versions behind"), using the one primitive from npm that pays, with git as the registry (A2). See [`docs/ideas/claude-config-as-registry.md`](docs/ideas/claude-config-as-registry.md) for the full write-up.
- **Acceptance:** Prototype the credible first step (lockfile-write in `claudify-repo` PORT + seed `version: 2.0.0` on `kickoff`) and judge whether the bet holds.
- **Size:** L
- **Added:** 2026-06-18

### [Improvement] CONVENTIONS.md: the command frontmatter contract + a copy-paste stub
- **Why:** A short root `CONVENTIONS.md` states the command frontmatter contract (`description` / `argument-hint` / `allowed-tools`, their order, when each is optional) + a copy-paste stub — documentation as the validator for a prose-only, test-less repo (A3). See [`docs/ideas/conventions-md.md`](docs/ideas/conventions-md.md) for the full write-up.
- **Acceptance:** Create `CONVENTIONS.md` (contract + stub + omit-rules), link it from README, and add it to `install.sh` DENY; confirm a stub copy reproduces `smoke-test.md`'s field order and `begin`/`wrap`/`handoff` are documented as the intentional argument-less case.
- **Size:** M
- **Added:** 2026-06-23

### [Feature] Agent gauntlet pipeline: specifier → coder → cleaner → hardener → QA
- **Why:** Uncle Bob's working relay of five narrow-context agents, each stage gated by a deterministic tool — quality from loops between focused agents, not steering one long-context agent. Full write-up in [`docs/ideas/agent-gauntlet-pipeline.md`](docs/ideas/agent-gauntlet-pipeline.md).
- **Acceptance:** The three-stage skeleton (specifier → coder → hardener) runs end-to-end on one real repo with deterministic gates, measured against a plain single-session build of the same story.
- **Size:** L
- **Added:** 2026-08-20

### [Exploration] Values, not disciplines: stop imposing human TDD ritual on agents
- **Why:** Bob no longer imposes line-by-line TDD on agents (they revert to function-then-test anyway) — enforce the *values* via outcome gates instead. **Contradicts `/tdd` and `superpowers:test-driven-development`**; the capture's job is to force that call. Full write-up in [`docs/ideas/values-not-disciplines-for-agents.md`](docs/ideas/values-not-disciplines-for-agents.md).
- **Acceptance:** The A/B experiment in the doc run once, and a recorded adopt/reject/scope decision on the two conflicting items.
- **Size:** S
- **Added:** 2026-08-20

### [Exploration] Anti-plan-maxing: fiddle-until-right over heavy upfront planning
- **Why:** Bob calls plan-first agent runs "always a disaster" and argues the collapsed cost of change favors build-look-reorganize. **Contradicts the planner/builder protocol and plan-first skills**; likely outcome is scoping *when* plan-first applies, recorded deliberately. Full write-up in [`docs/ideas/anti-plan-maxing.md`](docs/ideas/anti-plan-maxing.md).
- **Acceptance:** A one-paragraph plan-first/iterate-first boundary written into CLAUDE.md (or a recorded rejection), after a two-week trial.
- **Size:** S
- **Added:** 2026-08-20

### [Feature] Mutation-testing "hardener" subagent
- **Why:** Nothing in the config measures test-suite strength — the hardener kills surviving mutants, the one signal coverage can't give. Full write-up in [`docs/ideas/mutation-testing-hardener.md`](docs/ideas/mutation-testing-hardener.md).
- **Acceptance:** `agents/mutation-hardener.md` (read-only auditor first, modeled on `silent-failure-hunter`) dispatched over one Stryker-equipped repo with a useful graded report.
- **Size:** M
- **Added:** 2026-08-20

### [Feature] CRAP-score gate: coverage × complexity as a deterministic quality loop
- **Why:** The config's hooks gate git behavior; nothing gates the code. A CRAP score is hooks-over-prompts applied to code quality. Verified 2026-08-20: the loop must anchor on the Stop hook — PostToolUse cannot block. Full write-up in [`docs/ideas/crap-score-gate.md`](docs/ideas/crap-score-gate.md).
- **Acceptance:** Report-only `/crap-check` on one coverage-wired repo, ranked worst-function output; promotion to a Stop-hook loop decided from its noise level.
- **Size:** M
- **Added:** 2026-08-20

### [Feature] Module dependency-rules checker: a spec file the agents cannot violate
- **Why:** Architecture is what agents erode and no test catches — a declared dependency graph plus a checker turns the design layer deterministic. Full write-up in [`docs/ideas/module-dependency-rules-checker.md`](docs/ideas/module-dependency-rules-checker.md).
- **Acceptance:** `deps.yml` + checker run by hand on one pilot repo, finding (or proving absent) real violations, before any hook wiring.
- **Size:** M
- **Added:** 2026-08-20

### [Exploration] Ephemeral specs: the end result is the specification
- **Why:** Bob persists checks (Gherkin, QA scripts), never spec prose — "there is no equivalent to source code." **Contradicts `spec-miner`'s** durable-spec premise; resolve whether its outputs are living documents or point-in-time mining aids. Full write-up in [`docs/ideas/ephemeral-specs.md`](docs/ideas/ephemeral-specs.md).
- **Acceptance:** A one-paragraph charter amendment on `spec-miner` recording the chosen reading.
- **Size:** S
- **Added:** 2026-08-20

### [Feature] Architecture viewer: clickable module/dependency map of a repo
- **Why:** Strategic review needs a structural surface; nothing in the inventory provides one, and the HTML-artifact rendering muscle already exists in-house. Full write-up in [`docs/ideas/architecture-viewer.md`](docs/ideas/architecture-viewer.md).
- **Acceptance:** One repo rendered as a self-contained HTML map (nodes, dependency arrows, one level of click-to-expand) that changes at least one real review.
- **Size:** M
- **Added:** 2026-08-20

### [Feature] Agent-tuned thresholds: widen human lint limits for agents
- **Why:** Bob runs CRAP 4 for humans, 6–8 for agents — numeric gates need per-audience thresholds, stated once where every future gate can cite it. Full write-up in [`docs/ideas/agent-tuned-thresholds.md`](docs/ideas/agent-tuned-thresholds.md).
- **Acceptance:** The principle landed as one CLAUDE.md sentence in the same PR as the first shipped numeric gate.
- **Size:** S
- **Added:** 2026-08-20

### [Feature] Specifier subagent: human doc → Gherkin + QA procedure
- **Why:** Converts vague intent into deterministic acceptance criteria before code exists; standalone it sharpens backlog `Acceptance:` lines. Full write-up in [`docs/ideas/specifier-subagent.md`](docs/ideas/specifier-subagent.md).
- **Acceptance:** `agents/specifier.md` run on one real backlog stub, output compared against the hand-written acceptance.
- **Size:** M
- **Added:** 2026-08-20

### [Exploration] Deterministic tools over steering instructions — coverage confirmation
- **Why:** Bob's "guidelines, not rules" observation is the already-adopted `hooks-over-prompts` convention; captured per capture-all instruction. The only delta: the convention lives in an auto-memory, not a durable tracked file. Full write-up in [`docs/ideas/deterministic-tools-over-steering.md`](docs/ideas/deterministic-tools-over-steering.md).
- **Acceptance:** Either hooks-over-prompts graduated to a CLAUDE.md paragraph, or this stub closed as confirmed-covered.
- **Size:** S
- **Added:** 2026-08-20

### [Improvement] Minimal initial prompt: salience audit for always-loaded instructions
- **Why:** Lost-in-the-middle means long CLAUDE.md files silently lose their middle; `/trim-context` audits size — this adds the positional-salience and hook-convertibility criteria. Full write-up in [`docs/ideas/minimal-initial-prompt.md`](docs/ideas/minimal-initial-prompt.md).
- **Acceptance:** One hand-run audit of the global CLAUDE.md (must-hold vs guidance + ranked hook-conversion list) and a decision on folding the pass into `/trim-context`.
- **Size:** M
- **Added:** 2026-08-20

### [Exploration] Loop-until-the-tool-says-okay as the core agent contract
- **Why:** Gates as loop conditions, not reports — the connective framing for the CRAP gate and dependency checker, with Bob's escape-valve warning attached. Likely absorbed by whichever gate ships first. Full write-up in [`docs/ideas/loop-until-tool-passes.md`](docs/ideas/loop-until-tool-passes.md).
- **Acceptance:** The first shipped gate implements loop-until-green with a max-iteration escape valve; then close this stub.
- **Size:** S
- **Added:** 2026-08-20

### [Improvement] Cleaner agent as an automatic between-tasks stage
- **Why:** `/simplify` + `code-simplifier` exist but only on demand; Bob runs cleaning as a standing stage because implementer mess is expected, not exceptional. Full write-up in [`docs/ideas/cleaner-agent-auto-stage.md`](docs/ideas/cleaner-agent-auto-stage.md).
- **Acceptance:** A `/simplify` offer wired into `ship-and-route`'s pre-review flow, trialed for a few merges.
- **Size:** S
- **Added:** 2026-08-20

### [Improvement] QA agent: compile the `/smoke-test` checklist into an executable script
- **Why:** `/smoke-test` ends at a checklist Kyle walks himself — the written procedure is already the input; the missing half is compilation to a Playwright script (pattern proven by Constellation's `/verify-planet`). Full write-up in [`docs/ideas/qa-doc-to-executable-script.md`](docs/ideas/qa-doc-to-executable-script.md).
- **Acceptance:** One existing checklist hand-compiled to a Playwright script that runs and yields a credible pass/fail before touching the skill.
- **Size:** M
- **Added:** 2026-08-20

### [Exploration] Born-do-die agent lifecycle — coverage confirmation
- **Why:** Fresh context per task is the planner/builder protocol's existing rule; captured per capture-all instruction. Residual: Bob's startup-cost caveat as a decomposition floor. Full write-up in [`docs/ideas/born-do-die-agent-lifecycle.md`](docs/ideas/born-do-die-agent-lifecycle.md).
- **Acceptance:** One protocol sentence added ("split only when the stage outlives its startup cost") or the stub closed as covered.
- **Size:** S
- **Added:** 2026-08-20

### [Exploration] Trajectory management — coverage confirmation + party-line delta
- **Why:** Clear-context-to-clear-trajectory is already why builder sessions start fresh; captured per capture-all instruction. Residual: trajectory contamination as a possible fourth `auto-handoff` trigger (party-line). Full write-up in [`docs/ideas/trajectory-context-clearing.md`](docs/ideas/trajectory-context-clearing.md).
- **Acceptance:** A decision on whether drift-detection is mechanizable enough to be a party-line exploration, or the stub closed as covered.
- **Size:** S
- **Added:** 2026-08-20

### [Feature] Concentrate steering density in narrow-scope subagents
- **Why:** Rules keep salience in small contexts — allocate steering budget inversely to task breadth. Implicit in existing agent files, stated nowhere. Full write-up in [`docs/ideas/steering-density-in-subagents.md`](docs/ideas/steering-density-in-subagents.md).
- **Acceptance:** One paragraph wherever agent-authoring guidance lives, citing `adversarial-reviewer` and `silent-failure-hunter` as worked examples.
- **Size:** S
- **Added:** 2026-08-20

### [Improvement] Interrogate-the-agent architecture review
- **Why:** Bob's post-build ritual — make the agent explain the structure it just created, then redesign from the answer; a cadence `feature-dev:code-explorer` and `/project-guide` don't provide. Full write-up in [`docs/ideas/interrogate-agent-architecture-review.md`](docs/ideas/interrogate-agent-architecture-review.md).
- **Acceptance:** The raw-prompt version tried after one multi-file build; a decision from the answer on whether it earns a durable home.
- **Size:** S
- **Added:** 2026-08-20

### [Feature] Prefer deep modules (small interface, deep implementation) for agent legibility
- **Why:** Narrow interfaces let agents work against a module without loading its guts into context — Ousterhout's idea re-justified as context economy, worth one stated rule. Full write-up in [`docs/ideas/deep-modules-for-agent-legibility.md`](docs/ideas/deep-modules-for-agent-legibility.md).
- **Acceptance:** One CLAUDE.md sentence, optionally plus an adversarial-reviewer checklist line.
- **Size:** S
- **Added:** 2026-08-20

### [Feature] Tests as agent documentation: keep tests readable as the behavioral spec
- **Why:** Agents read tests to learn the system — test readability is a functional interface for every future session, not a nicety. Full write-up in [`docs/ideas/tests-as-agent-documentation.md`](docs/ideas/tests-as-agent-documentation.md).
- **Acceptance:** One global CLAUDE.md paragraph; applied opportunistically in review.
- **Size:** S
- **Added:** 2026-08-20

### [Exploration] Study-and-rebuild tool adoption ("point your agents at my tools")
- **Why:** Treat external tools as specifications of essence — agents study them and build a customized house version, trading cheap build cost for zero dependency surface. Needs a rebuild-vs-install boundary. Full write-up in [`docs/ideas/point-agents-at-tools.md`](docs/ideas/point-agents-at-tools.md).
- **Acceptance:** The pattern applied deliberately once (the CRAP gate is the candidate) and a judgment on whether it deserves a written rule.
- **Size:** S
- **Added:** 2026-08-20

### [Feature] Spot-check dashboard: monitor scores instead of reading code
- **Why:** Bob's supervision posture — watch the scores, sample the code, never full-review. Almost certainly ships as the CRAP gate's report mode; stubbed so the posture half isn't lost in the enforcement half. Full write-up in [`docs/ideas/crap-spot-check-dashboard.md`](docs/ideas/crap-spot-check-dashboard.md).
- **Acceptance:** `/crap-check`'s report-only output serves as the v0 dashboard.
- **Size:** S
- **Added:** 2026-08-20

### [Exploration] Parallel coders — coverage confirmation
- **Why:** Parallel implementation agents are already the Workflow tool / ultracode substrate; captured per capture-all instruction with no identified residual delta. Full write-up in [`docs/ideas/parallel-coders-convention.md`](docs/ideas/parallel-coders-convention.md).
- **Acceptance:** Close as confirmed-covered unless practice surfaces a gap.
- **Size:** S
- **Added:** 2026-08-20
