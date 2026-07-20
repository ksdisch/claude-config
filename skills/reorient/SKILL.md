---
name: reorient
description: Use when returning to a project after a real gap — days to months away — and memory of it has faded. Triggers: "I haven't touched this in a while", "catch me back up to speed", "where did I leave off / where were we", "I barely remember where things stand", "getting back into this project", "/reorient". NOT for: ordinary session starts with fresh memory (/begin), a full standalone project write-up (/project-guide), mid-session audio recaps (/catchup), or doing the next work itself — it routes to ship-and-route / backlog-hygiene / replenish / autonomous-milestone and their gates. Reads and briefs only; changes nothing.
---

# Reorient

**The re-entry router.** After an absence, two things have decayed: your memory of the project, and the project's state relative to your memory of it. Reorient rebuilds fluency first (a gap-scaled catch-up brief), then diagnoses the pipeline and routes the next move to the purpose-built skill. It is `/begin`'s big sibling: begin assumes you remember and briefs the *delta since yesterday*; reorient assumes you don't and briefs the *project, the gap, and the decision*.

**Prime directive — it changes nothing.** No commits, stash operations, rebases, pushes, merges, branch switches or deletions, backlog edits, or builds. A returning user's dangling state — the dirty file, the stash, the unpushed branch, the open PR — is *evidence of where they left off*, and it is **their half-remembered work**: touching it before they re-understand it destroys the very context this skill exists to restore. A blanket "handle whatever needs handling — I trust you" from someone who just said they barely remember the project authorizes the reads and the brief, **not** state changes; landing work belongs to `ship-and-route`, whose review gate exists for exactly this. **Silence is not consent:** after the brief and the route options, if the user doesn't reply, the run is over — never treat no-answer as approval of the recommended route.

## Where it sits

| Skill | When |
|---|---|
| `/begin` | Ordinary session start, memory fresh — one-screen delta brief |
| **`/reorient`** | Returning after a gap, memory faded — re-grounding + pipeline routing |
| `/project-guide` | You want the full standalone guide artifact (reorient may route here) |
| `/catchup` | Mid-session audio recap of *this* session — unrelated |
| `ship-and-route` · `/backlog-hygiene` · `/replenish` · `/autonomous-milestone` · `systematic-debugging` | The executors reorient hands off to |

## Phase 1 — Measure the gap (silently)

Establish **last human activity**: `git log` dates — **separating human/session commits from bot, cron, and cloud-agent commits** (automated activity during the gap is "what changed without you," not "recent work by you") — plus the newest wrap log (`docs/session-logs/` → `.claude/session-logs/` → any `*session-log*`/dated-recap scan) and any dated toolchain artifacts (`docs/bug-hunt/`, `docs/backlog-hygiene/`, `docs/smoke/`). Gap = today minus last human touch. **The gap sets the altitude:** ~1–3 weeks → begin-plus (deltas + a light refresher) · a month-plus → full re-grounding (identity, vocabulary, every wrap log in the window, health check) · longer/heavily-drifted → all of that plus offering `/project-guide`.

## Phase 2 — Gather (read-only)

- **Identity:** `CLAUDE.md`, `README` — what this project IS, its core loop, its user.
- **Where they left off:** ALL wrap logs inside the gap window, not just the newest (a gap can span several arcs) — their 30-second elevator versions, "Suggested next moves," and Concepts sections; any handoff doc; `git status` (dirty files with mtimes, stashes), current branch and unpushed branches, open PRs.
- **What changed without them:** commits and merged PRs during the gap, flagged human vs automated; dependency/platform bumps called out by name — an automated deps bump is the classic silent breaker.
- **Pipeline paper trail:** the backlog file + plan/kanban doc, latest bug-hunt and backlog-hygiene reports.
- **Health check — honest or absent:** if the project defines cheap, side-effect-free checks (test/build/lint from CLAUDE.md/README), run them and report the actual output. If you don't or can't run them, the brief says **"unverified"** — never "everything looks fine" without command output. Prioritize this whenever automated commits landed in the gap.

## Phase 3 — The catch-up brief

One structured brief, scaled to the gap — **brief the project, not just the git state**; the user told you their memory faded:

1. **What this is** — 2–3 lines re-grounding (soul, core loop, user).
2. **Where you left off** — the story the dangling state tells, cross-checked against the last wrap's next-moves, with drift flags (`begin`-style): "wrap said X was next; since then Y happened."
3. **What happened while you were away** — one line per event, human vs automated labeled.
4. **Health** — verified results, or "unverified" plus what you'd run.
5. **Refresher** — 3–5 vocabulary/decision entries mined from the gap-window wrap logs' Concepts sections.
6. **Optional recall round** — offer 1–2 questions from the wrap logs' Active recall sections (answer key on request); accept "skip" cleanly, exactly once.

## Phase 4 — Diagnose and route, then STOP

Map the evidence to routes and present 2–3 ranked options — short label, 1–2 sentence tradeoffs, one **(Recommended)**:

| Signal | Route |
|---|---|
| Dangling finishable work — dirty tree, stash, unpushed branch, open PR | `ship-and-route` to land it behind its review gate (reorient merges nothing itself) |
| Backlog dry / Planned empty | `/replenish` |
| Backlog stocked but stale, unsequenced, or "what next" genuinely open | `/backlog-hygiene` |
| The last wrap's (Recommended) move **still holds after re-validation** | Resume it directly — hand over a starter prompt |
| Repo drifted so far the brief can't restore fluency | `/project-guide` first |

**Two rules the routes live by:** (1) A wrap log's "(Recommended)" is a *candidate, decayed by the gap* — re-validate it against what changed (especially automated commits) and the user's possibly-changed priorities; it is never pre-authorization. (2) **Never do a routed skill's job inline** — a hand-rolled landing sequence or backlog triage inside reorient is that skill done worse, minus its gates. Multiple signals usually sequence: land dangling work first, then decide what's next.

Then stop for the pick. On pick: invoke light flows (`backlog-hygiene`, `ship-and-route`, `begin`-style resume) in-session, or hand a fresh-session starter prompt for heavy ones (`/replenish`, `/autonomous-milestone`) — offer the choice. No pick → the brief stands, nothing else happens.

## Red flags — every one observed in baseline runs

| Drift / rationalization | Reality |
|---|---|
| Running a plain `/begin` for a months-long gap | Wrong altitude: begin briefs the delta; a faded user needs the project re-explained, a refresher, and a health check. |
| "If no reply comes this sitting, I treat the (Recommended) move as confirmed and proceed" | Silence is not consent. The run ends at the route options. |
| "Blanket go-ahead → commit the dirty file, pop the stash, rebase, push, merge the PR" | That dangling state is the user's half-remembered work and the main evidence of where they left off. Landing it belongs to ship-and-route's gate — after they're re-oriented. |
| "Steps 1–6 are all reversible, so no confirmation needed" | A stash-pop with conflict resolution over weeks-old context is not reversible in practice, and `--delete-branch` removes a remote ref. Reversibility is not the bar; comprehension is. |
| Naming the right skill, then doing its job inline anyway | Route to it. Its gates are the point. |
| Treating a weeks-old wrap recommendation as today's default | Re-validate against gap changes and ask — priorities move during an absence. |
| "CI was green in May, the deps bump is probably fine" | Automated gap commits are the classic silent breaker: run the cheap checks or say "unverified." |
