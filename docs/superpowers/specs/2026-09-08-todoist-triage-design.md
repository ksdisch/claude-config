# todoist-triage — design spec

**Date:** 2026-09-08
**Status:** approved design (interview 2026-09-08; Kyle: "go ahead and build the skill as you designed it"), built in the same session per the Planner/Builder protocol.
**Deliverable:** `skills/todoist-triage/SKILL.md` with `skills/todoist-triage/references/todoist-mcp.md`; a new "Personal Productivity" category in `docs/command-skill-reference.md` and `docs/usage-playbook.md` holding this skill's row and card plus `day`'s (moved from Session & Context Management); the seeded map at `~/Projects/_todoist/map.md` (outside the repo).
**Lineage:** Kyle: "I need a dedicated skill for comprehensive triaging / cleaning up of my todoist because its really overflowed and unorganized right now overall. and then [`/day`] can/will handle the day to day organization once the bulk cleanup is done."

## Purpose

One skill for the bulk cleanup of Kyle's whole Todoist and for the periodic passes that keep
it clean afterward. It inventories everything, settles a target project tree once (the
map), then works through buckets of proposed dispositions that Kyle approves a bucket at a
time. Writes happen only after approval; there is no delete in the API, so every
disposition is a complete, a re-date, or a move.

Success criterion: after the first full run, Inbox is empty, every open task has a project
and either a date or a Someday/Reference section, the finished-event project is completed,
every absorbed sub-project is empty and listed for archiving, and the run log names every
write.

## Decisions from the interview

| Question | Kyle's pick |
|---|---|
| Target state | **Collapse the tree**: fewer, flatter projects with labels carrying the sub-area. |
| Decision loop | **Bucketed proposals**, approved a bucket at a time, in ~20-minute sittings, resumable. |
| Stale-but-unsure tasks | **Someday**, refined in the design to the existing Someday *section* of the task's project, since every top-level project already has Active / Someday / Reference sections and the API can't add sections to a new project. |
| The old Todoist Gemini Pipeline repo | Stale, not used; moved to `~/Projects/_archive/`. Its weekly-review role passes to `/todoist-triage weekly`. |

## Grounding facts (verified 2026-09-08)

State of the account: 51 projects, of which 8 are an empty duplicate top-level tree and 3
are one-offs (one a finished interview-prep project with 35 overdue tasks); 73 overdue; 52
in Inbox, mostly evening-reflection auto-captures; 241 undated (130 created before
2026-01-20, 82 from late January through March, 29 since April); 54 future-dated, almost all A2C. Every top-level project runs
Peter Akkies' Active / Someday / Reference sections. Labels in use: the job-search pipeline
set, `quick`, `deep work`, `waiting-on`, plus ad-hoc ones on auto-captures (`finance`,
`health`, `critical`, `systems`, `security`, `pets`, `job-search`, `vault`, `logistics`).

API facts are in `skills/todoist-triage/references/todoist-mcp.md`: no delete, no single-task
read, 200-character description previews, 200-row query cap, `&` in project names breaks
filters, `created before:` only works paired with `created after:`, no project archive /
rename / reparent, no section or label creation.

## Design

### The target tree (the seeded map)

Twelve existing projects keep their sections; sub-project tasks move up.

| Keeps | Absorbs | Labels added |
|---|---|---|
| Inbox | nothing; triage empties it | — |
| Work / Career | BBall Coaching, Portfolio → John referral | coaching, portfolio |
| A2C Auctions | unchanged (`/day`'s project) | — |
| Job Search | Part Time Applications, Full Time Applications | part-time, full-time |
| Admin & Finances | Vehicle (Jeep), Retirement, Insurance & Benefits, Bills & Subscriptions | vehicle, insurance |
| Home | Cleaning & Organization, Louis, Shopping & Orders, Errands & Returns, Chores / Recurring, Tech & Setup, Cooking, Handywork | errand, tech |
| Health | Mental Health, Medical | — |
| Relationships | Marlee, Family, Friends | family, friends |
| Learning | Books, Leisure Books, Learning Books, Courses, AI Agents Intensive Course, DevLaunch Vault | book, course |
| Fun & Trips | nothing | — |
| 2026 Goals & Resolutions | Wishes, Goals, Ongoing Goals (Life); goal bullets → Reference | — |
| Routines & Planning | ADHD Sprint System | — |

Strata Panel Prep: finish and archive. The 8 duplicate empties: archive by hand. A2C
Auctions and Job Search stay children of Work / Career because the API can't reparent;
"flat" means no third level. The map is a default: Kyle edits it at Gate 1.

### Modes

`/todoist-triage` full and resumable · `inbox` · `weekly` (Kyle's existing four-step
Weekly Review: Inbox to near-zero, active honesty pass, waiting-for sweep, date cleanup) ·
`map`.

### Flow

Phase 0 inventory (partitioned reads, client-side project partition, JSON snapshot, totals
with a checkable sum) → Gate 1 map (first run or `map`; nothing moves before
`status: approved`) → buckets 1–7, each through the same loop: propose a ≤40-row table with
a disposition, target, and `obvious`/`judgment` confidence per task → one question (apply
all / obvious only / edit / skip) → apply with a re-read → verify by re-query → log. Order:
finished projects, duplicates, the collapse, Inbox, overdue honesty pass, undated per
project, pasted-text titles. Wrap posts counts and the archive list and, on the first full
run, creates the recurring Sunday `weekly` task in Routines & Planning.

### Dispositions without a delete

Done → complete. Dropped → ` (dropped M/D)` suffix, then complete. Someday and Reference →
section moves. Re-date → `due_string`. Descriptions are never written (read cap makes it
lossy) except in bucket 7 on an empty preview. Labels may not auto-create; the first
labelled move is a test with a stop-and-ask fallback.

### State

`~/Projects/_todoist/`: `map.md`, `inventory-YYYY-MM-DD.json`, `triage-YYYY-MM-DD.md`.
Never in the repo: task text includes rent, banking, and health details.

### Relationship to siblings

`/day` runs one project's day on the clean structure and does no bulk work. `triage` (the
repo ticket state machine) and `backlog-hygiene` (a coding backlog) are the software
analogs and never touch Todoist. The archived Gemini pipeline is superseded.

## Out of scope

- Fixing the evening-reflection capture so it lands in projects instead of Inbox (that's
  home-base's sweep code; a follow-up there).
- Archiving projects, creating sections or labels: not possible from the MCP; listed for
  Kyle each run.
- Completed-task history and analytics.

## Acceptance — first live run

- [ ] Inventory totals match Todoist and the partition sum checks.
- [ ] Gate 1 map approved and written with `status: approved`.
- [ ] Bucket 1 completes the finished interview-prep project's tasks.
- [ ] Bucket 3 leaves every absorbed sub-project empty and on the archive list; the label test passes or stops cleanly.
- [ ] Bucket 4 leaves Inbox empty.
- [ ] The run log names every write with the task id.

## Follow-ups

- Route auto-captures to projects at the source (home-base sweeps).
- If sittings run long, lower the row cap from 40.
