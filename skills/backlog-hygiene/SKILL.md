---
name: backlog-hygiene
description: Use when the backlog is already stocked and the question is what to do next, in what order — grooming/pruning/sequencing/decomposing the existing backlog corpus, phase planning, choosing the next arc, or weighing improvements and solidification work against new build. Triggers: "what should I work on next", "groom / sequence / prioritize / clean up the backlog", "what's the next phase", "help me pick", "/backlog-hygiene". NOT for: generating new backlog items (/brainstorm, /replenish), building the pick (autonomous-milestone — this skill hands off to it), landing finished work (ship-and-route), or fixing a known bug (systematic-debugging). Decision-first — builds nothing, invents nothing.
---

# Backlog Hygiene

Operates on the **backlog corpus + project state** to answer one question: *what should be worked on next, and in what order?* It grooms, prunes, sequences, decomposes, and coverage-checks what already exists, then presents a decision brief and — after the pick — hands off with a routed starter prompt. This is the reserved seam `/brainstorm` names for backlog-operations: a dedup/sort/decide task is the wrong shape for a Diverge→critic-gate engine, and the wrong shape for an ultracode rig. **This skill is LIGHT** — main-thread analysis, a few cheap read-only agents at most.

**Two prime directives, because both fail under "just make the call" pressure:**
1. **It builds nothing, ever.** Producing the decision *is* the deliverable. "If it's obvious, just get started" means *include the starter prompt so the next session starts instantly* — it never means start implementing here. In `autonomous-milestone`, picking a candidate IS build authorization; that is exactly why hygiene ends at the pick and routes to it instead of continuing.
2. **It invents nothing.** No new ideas, no gap-filler items. A hole in the pipeline is a *finding*, reported with a pointer at `/replenish` or `/brainstorm <mode>` — adding items is the generators' job.

## Where it sits

| Skill | Job |
|---|---|
| `/brainstorm`, `/replenish` | **Add** to the backlog |
| **`/backlog-hygiene`** | **Order and decide** — groom the corpus, pick the next arc |
| `/autonomous-milestone` | **Build** the pick (its no-target triage is a fast subset of this; use hygiene when the corpus needs grooming or the decision needs sequencing across items) |
| `ship-and-route` | **Land** finished work, then route from right here |

## Phase 1 — Inventory (main thread, read-only)

Auto-discover and read the whole corpus: the backlog file (`BACKLOG.md` → `TODO.md` / `ROADMAP.md` / `docs/backlog.md`), any roadmap/kanban/master-plan doc, `docs/ideas/`, the latest `docs/bug-hunt/` report, open GitHub issues (`gh issue list` if a remote exists), plus `README`/`CLAUDE.md` (identity, success criteria) and recent `git log` (what actually shipped). Build an item ledger: id · type · size · age · what it claims · where it points.

## Phase 2 — Steer (ONE round, GATE 1 — compressible, never deletable)

One `AskUserQuestion` round: **scope preset** (*Full* = groom + sequence + decide · *Decide* = sequence + decide only, corpus assumed clean · *Groom* = hygiene only, no decision), **appetite** — what does "next" mean right now (one sitting · an arc of a few items · a phase), including any solidify-vs-build-new lean — and **anything off-limits**. Echo the plan in one line and proceed. "Just make the call" compresses this to one quick round with stated defaults; it never deletes the round — appetite is the one input that cannot be inferred from the repo.

## Phase 3 — Groom: verify before you rank

**No item may appear in a ranking until it has a reality verdict.** Check each against the repo, not against its own text: already shipped (git log / the code itself — cite the commit/PR), stale (references files, flags, or plans that no longer exist), duplicate (same **move** as another item — same fix wearing two descriptions), too-big-to-start (no single credible first step), blocked (names a dependency that hasn't happened). Verdicts: `fresh · done-already · stale · duplicate · too-big · blocked`, **each with evidence** (commit, file, report line). Small corpus (≤ ~10 items): main thread. Larger: up to 3 cheap read-only agents, split by subsystem. **No numeric scoring** — qualitative, evidence-backed, same rule as everywhere else in this toolchain.

Verdicts at this stage are **proposals, not actions.** Present-tense confidence ("this is dead — remove it") is fine in the brief; touching the file is not. Standing permission to write docs is permission for the *approved* edits after Gate 2 — not for applying your own verdicts before anyone has reviewed them.

## Phase 4 — Decompose, sequence, coverage

- **Decompose:** every `too-big` item that survives gets a proposed first slice — a credible first wedge pinned to a real file/area — recorded as a *proposed child*, appended later, never replacing the parent.
- **Sequence:** assemble **2–3 candidate next arcs** — each a coherent run of 1–3 items with a theme ("solidify the import path", "ship the next visible thing") sized to the stated appetite, ordered by dependency and risk-burn-down (data-integrity before performance before polish, unless the user's lean says otherwise). Present each in `autonomous-milestone`'s case format: one-line what-it-is · pros/cons · heuristic blast radius (likely areas/files, rough risk — no deep code reads) · the logic. Mark one **(Recommended)**.
- **Coverage:** after grooming, look at the *mix* of what remains (solidify vs build-new vs UX vs de-risk). An empty axis is a finding — e.g. "after hygiene your active pipeline is entirely solidification; if that's not deliberate, run `/replenish` (Moonshot/QuickWin lanes)". Say it; **do not invent items to fill it.**

## Phase 5 — Decision brief (GATE 2 — HARD STOP)

Present in one sitting: the hygiene findings table (verdict + evidence + proposed disposition per item), the candidate arcs with the recommended pick, and the coverage note. Then ask two things together: **which arc/items to work next**, and **which hygiene edits to apply**. **This skill writes NO files before this go-ahead — none.** There is no pre-gate durable output (unlike bug-hunt's report, hygiene analysis is cheap to regenerate); "none" to both ends the run with the brief in chat.

## Phase 6 — Apply & hand off (only after the go-ahead)

- **Apply approved edits, preserving history — retire, never delete.** Follow the backlog's own conventions; where none exist: done-already/stale/retired items **move** to a `## Parked / Retired` section (created if absent) with a dated one-line reason citing the evidence ("shipped in #31", "target deleted in #27"); duplicates collapse to the stronger item with a subsumed-note; decompositions append the child linked to its parent. Never rewrite an existing item's substance.
- **Mirror the plan/kanban doc** if the repo keeps one, per that doc's conventions.
- **Save the decision brief** to `docs/backlog-hygiene/<YYYY-MM-DD>.md` (findings, arcs, the pick, the coverage note).
- Land it all as **one docs-only change** under the house git rules (worktree if the working copy is dirty or shared). Verify: diff touches only backlog/plan/docs files; nothing deleted, only moved with reasons.
- **Close with the handoff, not with work:** a copy-paste starter prompt for the picked arc, routed to the right executor — `[Bug]` → a `systematic-debugging` session · build/feature item → `/autonomous-milestone <target>` · needs-design-first → `/explore-plan` · test-shaped improvement → `/tdd`. State why that route fits, and attach the Run-config note required by `CLAUDE.md`'s Planner/Builder Protocol (recommended model + effort, one-clause why, literal launch command). When that pick is Opus 5, apply the builder notes (`.claude/opus5-builder-notes.md` if vendored in the repo, else `~/.claude/opus5-builder-notes.md`) to the starter prompt; if neither copy exists, write it normally. Then stop.

## Red flags — every one observed in baseline runs

| Drift / rationalization | Reality |
|---|---|
| "Standing permission on docs → apply the hygiene edits right now, before a reply" | Verdicts are proposals until Gate 2. Permission to write docs ≠ permission to skip the review of your own inferences. |
| "The answer's obvious → just get started on it" / opening a fix branch after presenting | This skill builds nothing. "Get started" = hand over the routed starter prompt; implementation belongs to the next session's executor. |
| "Remove items 1 and 5" — deleting done/stale items | Retire with a dated reason to Parked/Retired; history is part of the backlog. |
| Zero user stops end-to-end under "just make the call" | Two gates, always: one steering round (appetite can't be inferred) and the decision-brief hard stop. |
| Ranking items straight from their own text | Verify against the repo first — done-already and stale items poison every ranking they appear in. |
| Deferring all the big items and moving on | That's a coverage finding: if nothing build-shaped remains, say so and point at `/replenish` — don't silently ship a pipeline of pure chores. |
| A weighted scoring matrix to justify the ranking | Qualitative cases with evidence, per the house rule. If the ranking needs a spreadsheet to defend, the arcs aren't coherent yet. |
