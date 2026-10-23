# Skill repos evaluation: pstack and Addy Osmani's agent-skills vs. Matt Pocock's set

**Date:** 2026-10-17 · **Question:** should any skills from these two repos join the setup, which ones, why, and how would they be called?
**Bottom line:** cherry-pick two pstack skills (`blast-radius`, `correct`) by vendoring. Install neither repo as a plugin. Adopt nothing from osmani, and take one idea from it into the gates program.

## Sources pinned

Everything below comes from the actual `SKILL.md` files in shallow clones made 2026-10-17. I did not rely on READMEs or aggregator listings, which disagreed on counts.

| Repo | What it is | Commit read | Licence |
|---|---|---|---|
| `addyosmani/agent-skills` | "osmani". 25 skills, 9 commands, 4 agents. Plugin `agent-skills` v0.6.13, marketplace `addy-agent-skills` | `aeac41d` | MIT |
| `cursor/plugins` → `pstack/` | **Canonical pstack** (Lauren Tan, Cursor-native) | `101b274` | MIT (© 2026 Lauren Tan) |
| `cursor/plugins` → `harness/pstack/claude-code/` | **Official Claude Code build** of pstack, v0.15.25, shipped in Cursor's own `.claude-plugin/marketplace.json`. 54 skills, 2 agents | `101b274` | MIT |
| `michael-denyer/pstack-claude` | Most-starred third-party port (63 skills) | `5bd4529` | MIT |

The official Claude Code build makes the third-party ports moot. It is also safer: it keeps `disable-model-invocation: true` on 53 of 54 skills. The Denyer port drops that flag, so its 63 descriptions would steer every session (about 12.6k chars). Which pstack Kyle "meant" doesn't change the verdicts, so I didn't ask.

The flagged `automate-me` concern checks out, but it isn't a red flag. The skill reads this workspace's transcripts and writes a `<handle>-mode` skill to `.claude/skills/` or `~/.claude/skills/`. It is user-invoked only, says to stay inside the workspace's transcript folder, and lands its output through a worktree and a PR. It is skipped anyway (see the verdicts).

**Steering weight** uses `/retire`'s yardstick: description chars that load into every session. User-invoked skills (`disable-model-invocation: true`) cost zero model-side chars and only take a slot in the slash menu.

| Set | Model-invocable skills | User-only skills | Agents | Always-on chars |
|---|---|---|---|---|
| osmani | 25 | 0 | 4 | ~9,600 (8,850 skills + 754 agents) |
| pstack (official) | 1 (`setup-pstack`) | 53 | 2 | ~800 (275 + 524) |
| Matt (installed) | 11 | 16 | 0 | ~2,150 |
| superpowers (installed) | 14 | 0 | 0 | ~1,970 (122 auto picks in the 2026-09-18 inventory) |

## 1. Inventory

### osmani: `addyosmani/agent-skills`

**Triggers:** every skill is model-invoked from its description. The plugin also registers 9 slash commands: `/spec`, `/plan`, `/build [auto]`, `/test`, `/review`, `/code-simplify`, `/ship`, `/constraints`, `/webperf`. Its SessionStart router hook ships but is deliberately not wired for Claude Code (`hooks/session-start.sh` says so). Agents: `code-reviewer`, `security-auditor`, `test-engineer`, `web-performance-auditor`. **House style:** long skills (1.3k–3.5k words) with fixed sections (Overview / When to Use / When NOT / Process / Common Rationalizations table / Red Flags / Verification).

| Skill | Purpose | Trigger (description cue) |
|---|---|---|
| `using-agent-skills` | Router meta-skill: picks which skill applies | session start; "which skill applies" |
| `idea-refine` | Diverge/converge on a vague idea | "ideate", "refine this idea" |
| `interview-me` | One-question-at-a-time intent interview to ~95% confidence | underspecified ask; "interview me", "grill me" |
| `spec-driven-development` | Write a spec/PRD before code | new project/feature with no spec; `/spec` |
| `planning-and-task-breakdown` | Spec → ordered tasks | have a spec, need tasks; `/plan` |
| `incremental-implementation` | Thin verifiable slices | any multi-file change; `/build` |
| `test-driven-development` | Red-green-refactor | any logic, bug fix, or behaviour change; `/test` |
| `debugging-and-error-recovery` | Root-cause debugging | tests fail, build breaks, unexpected error |
| `code-review-and-quality` | Five-axis review | before merging any change; `/review` |
| `code-simplification` | Behaviour-preserving clarity refactor | code works but is hard to read; `/code-simplify` |
| `doubt-driven-development` | Fresh-context adversarial reviewer on every non-trivial decision | high stakes, unfamiliar code, "stress-test" |
| `constraint-driven-development` | Interview → `CONSTRAINTS.md` quality bar; watch diffs for a weakened bar | no bar written down; agent silencing checks; `/constraints` |
| `source-driven-development` | Ground framework code in official docs, cite them | writing framework code from memory |
| `context-engineering` | Set up rules files and agent context | session start, degraded output |
| `api-and-interface-design` | Stable API/module boundaries | designing APIs or public interfaces |
| `frontend-ui-engineering` | Accessible, production-quality UI | building UI |
| `browser-testing-with-devtools` | Real-browser checks via Chrome DevTools MCP | anything in a browser (needs `chrome-devtools` MCP) |
| `performance-optimization` | Frontend/backend/query performance | perf requirements or regressions; `/webperf` |
| `security-and-hardening` | OWASP, deps, privacy hardening | untrusted input, auth, third-party integrations |
| `observability-and-instrumentation` | Logging, metrics, tracing, alerts | shipping anything that runs in production |
| `deprecation-and-migration` | Sunset APIs; expand/contract migrations | removing or migrating systems |
| `documentation-and-adrs` | ADRs and decision docs | architecture decisions, public API changes |
| `git-workflow-and-versioning` | Commits, branches, PRs, releases | "making any code change" |
| `ci-cd-and-automation` | Pipelines and quality gates in CI | setting up or changing CI |
| `shipping-and-launch` | Pre-launch checklist, staged rollout, rollback | before a production deploy; `/ship` |

### pstack: official Claude Code build (`cursor/plugins/harness/pstack/claude-code`)

**Triggers:** every skill except `setup-pstack` is typed only, as `/pstack:<name>`. Skill bodies are written in Cursor's vocabulary (`Task`, `AskQuestion`, `.cursor/…`, `pstack-models.mdc`). Each one opens by telling the agent to read `docs/harness/claude-code.md`, a mapping table it then applies at run time. Several skills default subagents to Grok (`grok-4.7-xhigh-fast`). The adapter says to omit non-Claude slugs in Claude Code, so those seats fall back to the session model. Agents: `poteto-agent`, `comment-sicko`. **House style:** short and blunt (40–1,500 words), many skills calling each other, and a separate `principle-*` layer that `poteto-mode` cites.

| Skill | Purpose | Trigger |
|---|---|---|
| `poteto-mode` | Lauren Tan's whole working style: non-negotiables, principles, autonomy, subagents, replies | `/pstack:poteto-mode` |
| `poteto-help` | Guide to pstack and picking a skill | `/pstack:poteto-help` |
| `setup-pstack` | Configure per-role models (no-op in Claude Code, per the adapter) | model-invoked + typed |
| `automate-me` | Mine transcripts plus an interview into a personal `-mode` skill | typed |
| `architect` | Sketch types and module shape before code, then supervise | typed |
| `arena` | N parallel candidates, cross-judge, graft the best parts into one | typed |
| `swarm` | Fan out N workers, drain, one report | typed |
| `figure-it-out` | Design an auditable phased playbook for big work | typed |
| `interrogate` | Multi-model adversarial code review (Claude + Grok) | typed |
| `blast-radius` | What a change breaks outside the diff; prove the one fact that makes it safe by running code | typed |
| `correct` | Find the mistakes agents keep repeating and make them impossible (architecture → types → lint → test → docs) | typed |
| `create-verification-skill` | Generate a project-local `verify-<app>` skill plus a feature map, proven end to end | typed |
| `maintain-verification-skill` | Periodic audit that keeps that verify skill honest | typed |
| `show-me-your-work` | Append-only TSV decision log for long or unattended runs, audited against the transcript | typed |
| `benchmark-checklist` | Vet a perf measurement before reporting it | typed |
| `how` | Explain how a subsystem works | typed |
| `why` | Parallel MCP-backed archaeology of why code is shaped this way | typed |
| `teach` | `how` + `why` woven into one explanation | typed |
| `recall` | Rebuild recent working context from history | typed |
| `reflect` | Three reviewers mine the transcript into skill edits | typed |
| `ketchup` | Catch up on what changed since your last message, with visuals | typed |
| `bro` | Restate the last message in plain words | typed |
| `in-your-own-words` | Restate the user's goal | typed |
| `sharpen` | Pre-task framing: expert approach, real goal, right spec level | typed |
| `tdd` | TDD only when asked or cheap | typed |
| `no-comments` | Run `comment-sicko` over the diff, fix accepted findings | typed |
| `unslop` | Strip AI tells from prose (bans em dashes) | typed |
| `technical-writing` | Diátaxis + Google style + STE writing standard | typed |
| `typescript-best-practices` | TS rules, `paths`-scoped to `*.ts(x)` | typed |
| `make-bot-ui` | UI that wakes a Grok Bot over a webhook | typed |
| 25 × `principle-*` | Short rules (54–451 words) that `poteto-mode` cites: attack-the-premise, boundary-discipline, build-the-lever, encode-lessons-in-structure, exhaust-the-design-space, experience-first, explain-the-number, fix-root-causes, foundational-thinking, guard-the-context-window, laziness-protocol, make-operations-idempotent, migrate-callers-then-delete-legacy-apis, minimize-reader-load, model-the-domain, never-block-on-the-human, outcome-oriented-execution, prove-it-works, redesign-from-first-principles, separate-before-serializing-shared-state, sequence-verifiable-units, subtract-before-you-add, test-behavior-not-implementation, type-system-discipline | typed |

## 2. Comparison with the baselines

### Overlap map

| Job | Matt | superpowers | Kyle's own | osmani | pstack |
|---|---|---|---|---|---|
| Intent interview / stress-test | `grilling`, `grill-with-docs` | `brainstorming` | CLAUDE.md clarifying-questions rule | `interview-me`, `idea-refine` | `sharpen`, `in-your-own-words` |
| Spec → tickets → build | `to-spec`, `to-tickets`, `implement(-spec)`, `wayfinder` | `writing-plans`, `executing-plans`, `subagent-driven-development` | `wayfinder-map` | `spec-…`, `planning-…`, `incremental-implementation` | `architect`, `figure-it-out` |
| TDD | `tdd` | `test-driven-development` | — | `test-driven-development` | `tdd` |
| Debugging | `diagnosing-bugs` | `systematic-debugging` | — | `debugging-and-error-recovery` | `principle-fix-root-causes`, `-attack-the-premise` |
| Code review | `code-review` | `requesting-/receiving-code-review` | built-in `/code-review` (low…ultra) | `code-review-and-quality`, `doubt-driven-…` | `interrogate`, `arena` |
| Simplify / comments | — | — | built-in `/simplify`, `code-simplifier` plugin | `code-simplification` | `no-comments`, `principle-laziness-protocol` |
| Module design | `codebase-design`, `improve-codebase-architecture` | — | `architecture-viewer` | `api-and-interface-design` | `principle-minimize-reader-load`, `-type-system-discipline` |
| ADRs / domain docs | `domain-modeling` | — | `docs/adr/` | `documentation-and-adrs` | — |
| Docs-grounded code | `research` | — | context7 plugin (its instructions already mandate fetching docs) | `source-driven-development` | — |
| Catch-up / re-pitch | `wait-what` | — | `visual-summary` | — | `ketchup`, `bro` |
| Context recovery / handoff | `handoff` | — | `/handoff-session`, `pre-compact`, ghost | `context-engineering` | `recall` |
| Session retro → skill edits | `retro` | `writing-skills` | `revise-claude-md` plugin, `/retire` | — | `reflect`, `automate-me` |
| Working-style persona | — | `using-superpowers` | `operating-constraints.md` + global CLAUDE.md | `using-agent-skills` | `poteto-mode` |
| Quality bar as enforced checks | — | `verification-before-completion` | gates program (ADR 0001, `check-doc-sync.py`, constellation's `gate:deps`/`gate:crap`) | `constraint-driven-development` | `correct`, `principle-encode-lessons-in-structure` |
| Security / perf / UI | — | — | built-in `/security-review`, `frontend-design` plugin | `security-…`, `performance-…`, `frontend-ui-…` | `benchmark-checklist` |

### What's genuinely new

Nothing in any baseline does these:

- **`blast-radius` (pstack).** It looks past the diff: the library source, wire formats, teardown timing, code three hops away. It then grades its own confidence on a five-step ladder ("you said so" → "you reproduced it in the running app") and proves the single safety fact with a script. `/code-review` checks the diff itself. Nothing checks what the diff breaks elsewhere and then proves the claim.
- **`correct` (pstack).** It turns repeated agent mistakes into structure, preferring architecture, then types, then a lint whose error names the fix, then a test, and docs last. Each new check must fail on a real past mistake, and a table records which rule each enforcer covers. Kyle's gates program and `check-doc-sync.py` already do this ad hoc. `correct` makes it a repeatable verb, the additive counterpart to `/retire`.
- **`create-verification-skill` / `maintain-verification-skill` (pstack).** These generate a per-repo verify skill. Kyle hand-built the equivalents (DogHood `/verify`, Constellation `/verify-planet`, stopwatch `/run-tests`). The built-in `run` skill looks for exactly this kind of project skill.
- **`show-me-your-work` (pstack).** An append-only decision TSV that is audited against the transcript. Useful for unattended runs, which today rely on the merge brief.
- **`constraint-driven-development` (osmani).** Its "Floor" check flags diffs that weaken the bar: new `@ts-ignore`/`eslint-disable`, skipped or deleted tests, stripped assertions, lowered thresholds. No gate Kyle has today checks for that.

Everything else duplicates Matt, superpowers, built-ins, or Kyle's own CLAUDE.md, often twice over.

### Philosophy and style

- **osmani is a lifecycle textbook.** It is broad, model-invoked, and checklist-heavy, with an anti-rationalization table in 24 of 25 skills (superpowers already uses that device). Its triggers are deliberately wide ("Use when making any code change", "before merging any change", "any logic, fixing any bug"). Installing it would put a third TDD, debugging, review, and planning skill into automatic routing, all competing with superpowers and Matt on every coding prompt. That is about 9.6k always-on chars, roughly 4.5× superpowers.
- **pstack is one engineer's opinionated operating system.** It is terse and user-invoked. Its distinctive bets are proof by running code, model diversity, and encoding lessons as structure rather than prose. Its weaknesses in Claude Code are that every skill translates Cursor names at run time and that the multi-model skills lose their premise without Grok. `poteto-mode` competes with Kyle's own operating constraints rather than complementing them.
- **Matt is closest to pstack in mechanics.** Both make most skills user-invoked, keep them short, and route between them. Matt's centre of gravity is the issue tracker and domain docs (spec → tickets → wayfinder). pstack's is verification and parallel agents. They complement each other more than they compete.
- **`unslop` clashes with house style.** It bans em dashes outright, while Kyle's docs use them throughout. Matt's `writing-for-agents` already covers agent-facing prose.

## 3. Verdicts

The weight column counts always-on description chars. A vendored copy keeps `disable-model-invocation: true`, as `teach-research` and `/handoff-session` already do here, so it adds one slash-menu entry and nothing to routing.

| Skill (repo) | Verdict | Why | When to call it | Install route | Weight added |
|---|---|---|---|---|---|
| `blast-radius` (pstack) | **Adopt** | The only skill in any set that proves what a change breaks outside the diff; it feeds the review-gate proposal directly | `/blast-radius <PR or diff>` before proposing a merge review scope on a small diff you don't trust, or "what could this break". A proven safety fact argues the scope down; a confirmed risk argues it up. Pairs with `/code-review`; doesn't replace it | Vendor, adapted (drop the Cursor adapter line and the `arena`/`why`/`unslop` hops; replace step 6 with "for a wide change, run `/code-review xhigh`") | 0 always-on; 1 menu entry, ~700 words when typed |
| `correct` (pstack) | **Adopt** | Gives the gates program a verb; the additive counterpart to `/retire` (retire subtracts prose, correct converts prose rules into enforcers) | `/correct` in a project repo after the same correction lands twice (e.g. stopwatch's stale-SW-cache false alarm, which `/fix-bug` already names as its #1) | Vendor, adapted (Cursor paths → Claude paths; it writes a rule ↔ enforcer table into the target repo's `CLAUDE.md`, so every run there gets the CLAUDE.md review floor) | 0 always-on; 1 menu entry, ~435 words |
| `create-verification-skill` + `maintain-verification-skill` (pstack) | **Defer** | Real value, but every active repo already has a hand-built verifier | Next new project that has no verify skill: vendor both then | Vendor when triggered | 0 now |
| `show-me-your-work` (pstack) | **Defer** | Useful for unattended runs; the merge brief covers today's volume | When an unattended or orchestrated run has to be audited after the fact and the brief isn't enough | Steal the TSV format, or vendor then | 0 now |
| `constraint-driven-development` (osmani) | **Steal the idea** | Its Floor (no new suppressions, no skipped tests, no lowered thresholds) is a strong candidate gate; the 3.5k-word interview skill isn't needed | Propose a "bar-weakening" diff check as a candidate gate under ADR 0001, on a repo of Kyle's choosing | Idea only | 0 |
| `poteto-mode`, `automate-me`, 25 × `principle-*`, `poteto-help`, `setup-pstack` (pstack) | Skip | A competing working-style layer; the principles largely restate `operating-constraints.md` (laziness-protocol ≈ scope discipline, prove-it-works ≈ no false progress, never-block-on-the-human ≈ unattended runs); `setup-pstack` is a no-op in Claude Code | — | — | — |
| `interrogate`, `arena`, `swarm`, `why`, `reflect` (pstack) | Skip | Built around Claude + Grok diversity, which collapses to one model here; covered by `/code-review` up to `ultra`, `ultracode` effort, superpowers dispatching, and Matt's `retro` | — | — | — |
| `architect`, `figure-it-out`, `tdd`, `teach`, `how`, `recall`, `ketchup`, `bro`, `in-your-own-words`, `sharpen` (pstack) | Skip | Duplicates `wayfinder`/`writing-plans`/`brainstorming`, Matt's `tdd` and `teach` (same bare names), `wait-what`, `visual-summary`, `/handoff-session`, ghost, and the clarifying-questions rule | — | — | — |
| `benchmark-checklist` (pstack) | Skip | No current perf-measurement work; `diagnosing-bugs` covers perf regressions | Revisit if a perf project starts | — | — |
| `no-comments`, `unslop`, `technical-writing`, `typescript-best-practices`, `make-bot-ui` (pstack) | Skip | `code-simplifier`/`/simplify`; em-dash ban fights house style; `writing-for-agents`; per-repo CLAUDE.md conventions; Grok-Bot specific | — | — | — |
| `doubt-driven-development` (osmani) | Skip | Fresh-context adversarial review of every non-trivial decision duplicates `/code-review`, `grilling`, and `verification-before-completion`, at high routing weight | — | — | — |
| `source-driven-development` (osmani) | Skip | context7's server instructions already mandate docs-first; Matt's `research` | — | — | — |
| Lifecycle set: `using-agent-skills`, `idea-refine`, `interview-me`, `spec-driven-development`, `planning-and-task-breakdown`, `incremental-implementation`, `test-driven-development`, `debugging-and-error-recovery`, `code-review-and-quality`, `code-simplification`, `documentation-and-adrs`, `git-workflow-and-versioning`, `context-engineering`, `api-and-interface-design` (osmani) | Skip | Each is the third copy of a job Matt and superpowers already route; broad triggers would contest every coding prompt | — | — | — |
| Domain checklists: `security-and-hardening`, `performance-optimization`, `observability-and-instrumentation`, `deprecation-and-migration`, `ci-cd-and-automation`, `shipping-and-launch`, `frontend-ui-engineering`, `browser-testing-with-devtools` (osmani) | Skip | Generic knowledge the model already has; built-in `/security-review`, `frontend-design`; browser testing needs a `chrome-devtools` MCP that isn't configured (Playwright and claude-in-chrome are) | — | — | — |
| Commands `/spec /plan /build /test /review /code-simplify /ship /constraints /webperf` (osmani) | Skip | Wrappers over the skipped skills; `/ship` collides with DogHood's `/ship`, `/review` with an existing review skill | — | — | — |

## 4. Plans for the adopts

**`blast-radius`.** Vendor to `skills/blast-radius/SKILL.md` with `disable-model-invocation: true`. Inline the `why` step-2 git and `gh pr view` commands. Replace the `arena` step with `/code-review xhigh`. Drop the `unslop` instruction. Add the attribution footer and a `THIRD-PARTY.md` section (cursor/plugins `101b274`, `harness/pstack/claude-code/skills/blast-radius`, MIT © 2026 Lauren Tan), plus a reference-doc row and playbook card (run config: Opus, `high`), all in the same commit. First real use: the next small-but-untrusted PR. Cite its "one safety fact" line in the review-gate proposal.

**`correct`.** Vendor to `skills/correct/SKILL.md` with `disable-model-invocation: true`. Map the Cursor paths. Add a note that the rule table it writes into a target repo's `CLAUDE.md` follows that repo's branch and PR flow and gets the behavioural-file review. Same attribution, `THIRD-PARTY.md` section, row, and card in one commit (run config: Fable, `high`, since choosing the enforcement level is a judgment call). First real use: stopwatch, where `/fix-bug` already lists known false alarms that could become checks.

Both land on one branch and one PR. It touches `skills/**`, so it gets a `/code-review` and stops for Kyle's merge call.

## 5. Recommendation

**Cherry-pick. Don't install either repo as a plugin.**

- **osmani wholesale** would add about 9.6k always-on chars (4.5× superpowers) and a third automatic TDD, debug, review, and planning route, plus two command-name collisions. Its one new idea fits better as a gate than as a skill.
- **pstack wholesale** is cheap on routing weight (about 800 chars), but it adds 53 slash entries, bare-name clashes with Matt (`tdd`, `teach`), a persona layer that competes with `operating-constraints.md`, and run-time Cursor translation in every skill. That's a poor trade for the two skills worth having. If Kyle ever wants to try it whole, the route is `/plugin marketplace add cursor/plugins` and then `pstack`. Never use the third-party ports, which strip the user-invoked flag.
- **Weight net of the adopts:** +0 always-on chars, +2 slash entries. If the two adopted skills go unused, `/retire` is the way back out.
