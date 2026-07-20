---
name: replenish
description: Use when a project's backlog has run dry and the pipeline needs refilling from several angles at once — new ideas AND not-yet-known bugs in one combined run. Triggers: "replenish the backlog", "refill the pipeline", "planned column is empty — what's next?", a combined "multi-lane brainstorm + bug audit", "/replenish". NOT for: executing existing backlog items (autonomous-milestone), a single-theme ideation pass (/brainstorm alone), fixing a known bug (systematic-debugging), or grooming/sorting the existing backlog corpus. Requires the /brainstorm command and the bug-hunt skill to be available — globally, or vendored into the repo via /claudify-repo.
---

# Replenish

A **backlog-refilling combinator**. It runs the `bug-hunt` engine plus N `/brainstorm` modes as **parallel agent-team lanes in one session** — one shared orient, one steering round, one combined review gate, one capture change — and lands a replenished, ranked backlog: vision docs, backlog stubs, `[Bug]` stubs, and a verified bug-triage report.

It is **composable, not a fork** (the same seam philosophy as bug-hunt → systematic-debugging). The engines' own specs are binding and loaded at runtime; this skill owns only the combinator. If an instruction here seems to conflict with an engine, the rule is: engine phases run **verbatim inside their lane**; replenish only *replaces their orients*, *pre-answers their interviews*, and *consolidates their user gates* — it never weakens a gate's substance.

**REQUIRED SUB-SKILLS:** before planning anything, load both engine specs — `/brainstorm` (mode catalog, lens/critic/refine machinery, capture formats) and `bug-hunt` (effort tiers, finders → adversarial verify → synthesize, severity, dated report, triage, handoff). **Preflight:** if either is unavailable in this environment (e.g. a vendored repo that lacks them), stop and say so — vendor all three together via `/claudify-repo`.

## Ownership map

| The engines own (run verbatim in-lane) | Replenish owns (the five deltas) |
|---|---|
| Lens sets, two-sided critic gates + verbatim inadmissible lines, Soul-Keeper, refine passes, survivor-card format, capture formats + ideas/backlog auto-discovery | 1. One shared orient / soul brief for every lane |
| Finder slicing (subsystem × lens), adversarial **verify-each**, severity rubric, dated `docs/bug-hunt/` report, triage rules, systematic-debugging handoff | 2. One combined steering round that pre-answers both engines' interviews |
| Model routing and per-run token discipline | 3. Cross-lane parallel scheduling + a summed budget ceiling |
| | 4. Cross-lane dedup + ONE merged review HARD STOP |
| | 5. One combined capture in a single docs-only change |

## Phase 0 — Shared Orient (once, main thread, cheap)

Run brainstorm's Orient recipe **once for all lanes** and write the soul brief to a scratch file (`/tmp/<repo-slug>-replenish-brief.md`, ~10–15 lines): what the project fundamentally IS, its core loop and user, 4–6 load-bearing assumptions, **ALL existing backlog / ideas / parked / deferred titles** (the self-censor list), and the bug lane's scope hint — the date of the latest `docs/bug-hunt/` report, so the hunt targets *everything since*.

**Every lane agent reads this file — lenses AND bug finders.** The brief is what teaches finders what "wrong" means for *this* product and what teaches lenses what already exists; a brief held only in-thread reaches neither.

## Steer — one combined round, then confirm (GATE 1 — compressible, never deletable)

One `AskUserQuestion` round covering: **lanes** (bug-hunt on/off + which brainstorm modes — offer presets: *Full* = bug-hunt + Moonshot + QuickWin + Premortem + Harden + Friction · *Standard* = bug-hunt + Moonshot + QuickWin + Harden · *Light* = bug-hunt + QuickWin · or custom from the full 9-mode catalog), the **Moonshot leash** if Moonshot is picked, and the **budget cap**.

From the answers, **pre-answer each engine's own interview** — bug-hunt's Aim (scope = repo-since-last-hunt, tier = ultracode fan-out unless steered down, disposition **locked to triage-only**; fixing routes through the end-of-run handoff) and each mode's Steer (catalog defaults; respect locked params — QuickWin/Harden/Friction lock Tethered, Premortem pins 12 months). Then **echo the assembled lane plan with the total agent count and ceiling, and confirm before ANY fan-out.**

"I'm in a hurry" / "you have standing permission" / "don't over-ask" compresses five engine interviews into this ONE round — it never deletes the round. Standing permission to *write docs* is not ratification of a 50-agent fan-out; brainstorm's own Steer requires confirm-before-fan-out, and merging the interviews **is** the time-respecting move.

## Run the lanes (parallel)

- **Lane A — bug-hunt fan-out, verbatim:** the engine derives the finder dimensions (subsystem × lens) from the real repo; if the repo vendors purpose-built reviewer agents (e.g. a contract-reviewer), add them as bonus finders. Then adversarial **verify-each** — batch verifiers, but keep **≥2 independent verifier calls**; never one agent ruling on the whole list. Then synthesize. The dated report is this lane's mandated durable output.
- **Lanes B+ — one per mode, verbatim:** Diverge (blind lenses reading the shared brief) → main-thread move-axis dedup → Validate (the mode's two opposing critics + Soul-Keeper, inadmissible line quoted verbatim) → Refine.
- **Scheduling:** all lens and finder agents are blind and read-only → launch them in parallel batches **across** lanes; each lane's critics run after that lane's dedup; refine after critics.
- **Budget:** ceiling ≈ 10 (bug-hunt) + ~12 × (number of brainstorm lanes). **State the total when you launch; hard-cap at 70.** Over the cap → batch lenses harder or drop a lane with the user; never trim the verify step, never add rounds.
- **Context discipline:** every lane's outputs land in scratch files; compact at the Validate → Refine and pre-review seams. The combined review must be assemblable **from files, not conversation memory**.

## Cross-lane dedup (main thread, before the review)

Dedup **across lanes on the move axis** — two entries that make the same move are ONE card; keep the stronger framing and credit both lanes on it. Known seams: **Harden ↔ bug-hunt** (a break+guard pair vs a verified bug for the same defect → one entry; the verified bug usually wins the framing, the guard becomes its suggested fix) and **Friction ↔ QuickWin**. Convergence across blind lanes is *signal* — note it on the surviving card; never present the same move twice.

## Combined review — ONE HARD STOP (GATE 2)

**Write the dated bug report now, at presentation time** — not after the user answers; it must survive the session regardless of picks. It and the scratch files are the only pre-gate writes.

Then present everything in one sitting: the ranked verified bug list with cross-cutting themes, and every brainstorm survivor as the engine's card format, grouped by lane, convergences flagged. **This single sitting IS each engine's mandated per-run gate — merged, never skipped.** Ask both picks together: which bugs are worth acting on, and which survivors to capture (one / several / all / none). No other file is written before the answer; "none" ends the run cleanly.

## Capture (only after the go-ahead)

Engine-verbatim: vision docs into the auto-discovered ideas dir; backlog stubs with each mode's capture type/size; plus a `[Bug]` stub per picked bug (severity + `file:line`, linking the dated report). **If the repo keeps a roadmap / kanban / master-plan doc, refill its Planned/Later columns per THAT doc's conventions in the same change.** Land it as **one docs-only change** under the house git rules.

**Worktree rule:** if the working copy is dirty or possibly shared with another live session, every write happens on a fresh worktree branch; re-verify the branch before each commit. **Verify before landing:** the diff touches only docs/backlog files; every stub link resolves; any touched kanban still renders. Close with a ranked "what I'd build next" recommendation.

## Wrap

Offer bug-hunt's handoff verbatim — "Want me to kick off `systematic-debugging` on these now?" — for the picked bugs (fresh sessions for big ones). Report every file written, SHAs, and the PR link.

## Red flags — every one observed in baseline runs

| Drift / rationalization | Reality |
|---|---|
| "User's in a hurry + standing permission → the review is the only stop" | Gate 1 compresses to one round; it never disappears. Confirm lane plan + agent count before any fan-out. |
| One verifier agent for all findings | The engine's contract is verify-EACH: ≥2 independent verifier calls, default-refuted, reading real code. |
| Soul brief held in-thread; finders get no brief | Brief goes to a scratch file; every agent in every lane reads it. |
| Bug report written only after the user picks | Written at presentation — it is the gate's durable record. |
| Same defect presented twice as "converging evidence" | One move = one card, both lanes credited on it. |
| Working copy flagged as shared, branch created in place anyway | Dirty-or-shared ⇒ worktree writes, branch re-verified per commit. |
| Big fan-out with no stated ceiling | State the total at launch; hard-cap 70; batch harder rather than trim verification. |
