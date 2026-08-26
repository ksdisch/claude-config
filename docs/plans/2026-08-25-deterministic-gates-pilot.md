# Deterministic gates pilot: dependency-conformance + CRAP report, Constellation first

**Decided:** 2026-08-25, grill-with-docs rounds 2–4 (Kyle + Fable). Governance recorded in
[`docs/adr/0001-gates-earn-the-veto.md`](../adr/0001-gates-earn-the-veto.md); vocabulary
(Gate, Instrument, Preflight, Promotion, Demotion) in [`CONTEXT.md`](../../CONTEXT.md).
Both merge with the `docs/context-glossary` branch **before** this plan executes — cite
them, don't restate them.

**The bet being executed:** adopt two of Uncle Bob's deterministic gates (source: the
Pocock/Martin discussion behind the 2026-08-20 idea-mine) as report-only checks that feed
`adversarial-review`'s propose-first step as **Preflight evidence**. Review keeps the merge
veto everywhere; a Gate earns the veto per-repo later (Promotion, Kyle's explicit call) or
loses its shot (Demotion). Nothing in this plan wires any blocking behavior.

## Scope fence (violating this is failing the plan)

- **Build:** dependency-cruiser config-as-spec-file + `scripts/crap-check.mjs` in
  Constellation; global `/crap-check` command + Preflight step + backlog/docs updates in
  claude-config. That's all.
- **Do not** touch the gauntlet (re-pilot is parked), build a house `deps.yml` format,
  add eslint, wire any pre-push/Stop hook, gate coverage, or run mutation testing.
- Both PRs go through the normal git workflow incl. propose-first review. The
  claude-config PR touches behavioral files → floor is at least SINGLE ROUND.

## Phase 1 — Constellation (`~/Projects/constellation`, branch `feat/deterministic-gates-pilot`)

1. **Install dev deps** `dependency-cruiser` and `@vitest/coverage-v8`; commit alone
   (mirrors gauntlet Stage 0's "commit the install visibly" rule).
2. **Draft the dependency spec** — a native dependency-cruiser config (the config *is*
   Bob's "tight little specification file"; no translation layer). Encode the **intended**
   architecture, not baselined reality. Sources: Constellation `CLAUDE.md` prose (e.g. the
   `protocol.ts` → `src/game` + `src/phone` + `server` + `scripts` dependents note) and the
   module surface `src/game` / `src/phone` / `src/shared` / `server/` / `scripts/`.
   Candidate rules to draft from (verify against the repo, don't assume): game ↮ phone
   directly (they meet only through shared protocol / the relay); `src/shared` imports no
   app module; `server` doesn't reach into `src/game`/`src/phone` internals.
   **⛔ GATE — interactive stop:** present the drafted rules to Kyle in plain language,
   rule by rule, and get approval **before** committing. The spec encodes his
   architecture, not the builder's guess.
3. **Entry bar (decision Q4-iii):** hand-run `npx depcruise` over the tree with the
   approved config. Record in the PR body: every violation found, or the explicit
   statement that none exist. A violation is a finding for Kyle (fix vs. amend the rule is
   his per-violation call), never something to silently rule-around.
4. **Write `scripts/crap-check.mjs`** (report-only, always exit 0): run
   `vitest run --coverage` with JSON reporter output; compute per-function cyclomatic
   complexity using the repo's own `typescript` package (no new lint framework); score
   `CRAP = comp² × (1 − cov)³ + comp`; print a ranked worst-functions table flagging
   every score **> 6** (agent calibration per Bob; humans run < 4). Keep it small
   (~40–80 lines) — the video's own advice is that this is an agent-written throwaway
   tool, not a product.
5. **Run it**; put the top of the first report in the PR body.
6. **Constellation `CLAUDE.md`:** add a short **"Wired gates (Preflight)"** note listing
   the two exact commands, so any session composing a merge proposal knows what to run.
   This list is what the Preflight step (Phase 2) reads.
7. PR + propose-first review per that repo's workflow.

## Phase 2 — claude-config (branch `feat/deterministic-preflight`) — after Phase 1 merges

1. **`skills/adversarial-review/SKILL.md`, step 3 (Gate proposal):** insert the Preflight
   pass — before composing the SKIP / SINGLE ROUND / FULL LOOP recommendation, run every
   gate listed in the target repo's "Wired gates (Preflight)" note over the diff and cite
   the results as evidence in the recommendation (clean Preflight argues scope down; a
   finding argues it up). No wired gates → one honest line saying so; nothing else
   changes. The Preflight itself never blocks and never substitutes for the review.
2. **Global `CLAUDE.md` (repo root, symlinked to `~/.claude/CLAUDE.md`):** in the
   review-gate paragraph of the Git Workflow section, one sentence establishing Preflight
   evidence in scope recommendations; plus **one** sentence stating the agent-tuned
   numeric-threshold principle (agents get wider limits than humans — CRAP starts at 6 vs
   the human 4 — stated once here so every future numeric gate cites it). Two sentences
   total; resist writing more.
3. **New `commands/crap-check.md`:** thin invoker — locate the target repo's wired CRAP
   tooling via its "Wired gates (Preflight)" note, run it, present the ranked report
   (flagging > 6), and say plainly when a repo has nothing wired. It never generates or
   installs tooling. Same commit: row in `docs/command-skill-reference.md` **and** card in
   `docs/usage-playbook.md` (the pre-push `check-doc-sync.py` enforces this).
4. **`BACKLOG.md` updates:** mark the CRAP-gate and module-dependency-rules-checker stubs
   shipped (pointing at the Constellation pilot + this command); close
   agent-tuned-thresholds (sentence landed); close loop-until-tool-passes as **superseded
   by ADR 0001's Promotion model** (report-first replaced loop-until-green — say that,
   don't pretend the acceptance was met as written); mark the spot-check-dashboard stub's
   acceptance met by `/crap-check`'s report mode; annotate the gauntlet item "re-pilot
   parked 2026-08-25 per ADR 0001"; **add the month-one verdict entry**: due
   ~2026-09-25 — promote / demote / extend each gate, evidence = PR comments citing
   Preflight results, criteria in ADR 0001.
5. PR + review at SINGLE ROUND minimum (behavioral floor: CLAUDE.md, skills, commands).

## Success / kill criteria (already decided — do not re-litigate)

- **Entry bar:** Phase 1 step 3 finds real violations or proves them absent.
- **Month-one payoff metric:** count of propose-first scope downgrades actually taken on
  Preflight evidence.
- **Kill rule:** zero actionable signal + ≥1 false block in month one → Demotion, not
  tuning.

---

**Run-config note:** Opus 5 at `high` — well-specified two-repo build with one judgment
gate (the rules approval, which stops for Kyle regardless). Launch in the Phase 1 repo:
`cd ~/Projects/constellation && claude --model claude-opus-5 --effort high`, prompt it to
execute this plan file top to bottom, Phase 1 first.
