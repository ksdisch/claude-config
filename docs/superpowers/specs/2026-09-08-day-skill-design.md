# day — design spec

**Date:** 2026-09-08
**Status:** approved design (interview 2026-09-08; Kyle: "thats great, build it"), built in the same session per the Planner/Builder protocol (plan-heavy, build-light).
**Deliverable:** one new skill at `skills/day/SKILL.md` (reachable as `/day` via the `~/.claude/skills` symlink) with `skills/day/references/hook-template.md`; the same-commit row in `docs/command-skill-reference.md` (Session & Context Management) and card in `docs/usage-playbook.md`; the first project hook at `~/Desktop/A2CAuctions/.claude/day.md` (outside this repo — A2C is not a git repo).
**Lineage:** Kyle asked for "a skill that I invoke at the beginning of each day that familiarizes itself with all of my tasks for a particular Todoist project for the day and then assists me / logs progress as I work through the day … keep me on task … not lose focus, start working on trivial things, keep me from over optimizing something instead of just making real progress." The A2C September plan already names this loop (Kyle reports one line per name after each call block; Claude logs, re-dates Todoist, rebuilds tomorrow's block). This generalizes it to any Todoist project.

## Purpose

`/day` is the daily bookend for a Todoist-driven working day. In the morning it reads one
Todoist project's tasks due today plus overdue, folds in whatever the project's hook adds,
briefs Kyle, and pins the day's must-do set. Then the session is in **day mode** until
`/day wrap`: Kyle reports outcomes in plain language and the skill logs them (Todoist
action + a timestamped line in the day log), challenges off-list and polish requests
with one line, and posts a short pace check-in on a session cron. Wrap re-dates what
slipped, writes the day's record, and runs the project's wrap step.

Success criterion: the first live run on the A2C project (Tue 9/8, 11 dated tasks)
produces a brief matching Todoist, logs a reported outcome to the right task, gates one
off-list request, fires at least one check-in, and wraps with every plan task either done
or re-dated.

## Decisions from the interview

| Question | Kyle's pick |
|---|---|
| Scope | One Todoist project per run (A2C first); project-specific rules live in a hook file in the project folder, so the same skill serves any project. |
| Focus mechanism | Gate on off-list / polish requests **plus** timed check-ins on a session cron. |
| Reporting | Plain talk in the session; `/day` re-invoked later resumes from the log file. |
| Record | One dated markdown file per day in the project folder (`daily/YYYY-MM-DD.md`). Todoist stays the operational record. |

## Grounding facts (verified 2026-09-08)

- **Todoist MCP** (`mcp__todoist__*`): `todoist_search_tasks` takes Todoist's native filter
  syntax; `#A2C Auctions & (today | overdue)` returned today's 11 dated tasks with due
  times (project names with spaces work unquoted). Writes: `todoist_complete_task`,
  `todoist_update_task` (`due_string`, `content`, `description`, `project_id`, …),
  `todoist_create_task`. `todoist_list_projects` for resolution. There is **no
  completed-tasks lookup**, so the day log is the only record of what got done.
- **CronCreate**: 5-field cron in local time, session-only (gone when the session exits),
  recurring jobs auto-expire after 7 days, fire only while the REPL is idle, and the prompt
  is enqueued as a user turn — so the check-in prompt must be self-contained. `CronList` /
  `CronDelete` manage them. Off-minutes preferred.
- **Google Calendar** `list_events` / `get_event` / `update_event` (update replaces the
  whole description) and **Gmail** `search_threads` are hook-level sources. The base skill
  needs only Todoist.
- `~/.claude/skills` is a symlink to `~/Projects/claude-config/skills`, so `skills/day/`
  is `/day` in every folder once the branch lands on the checkout.

## Design

### Entry points and project resolution

- `/day` — start the day (or resume it if today's log already exists).
- `/day <project>` — same, naming the Todoist project.
- `/day wrap` — close the day.

Project resolution, first hit wins: the argument → `.claude/day.md` in the CWD (its
`project:` line) → the CWD's `CLAUDE.md` naming a Todoist project → `todoist_list_projects`
and one question. The day-log directory is `daily/` in the folder that resolved the project;
a project with no folder falls back to `~/Projects/_daily/<project-slug>/`.

### Morning brief

Reads: Todoist `#<project> & (today | overdue)`; the newest prior day log (carry-overs, the
parking lot, whether the last day wrapped); the hook's extra sources (A2C: today's calendar
blocks for the scripts and window; a light Gmail check — `newer_than:1d in:inbox` scanned
for names on today's list). If the newest prior log is more than one day old, the brief's
first line says so and names the hook's re-entry skill (A2C: `/rebrief-a2c`) instead of
pretending the light check was a sweep.

Output: window · overnight items · carry-overs · the time-ordered task list (overdue
flagged) · yesterday's unworked parking lot · one question: **which one to three tasks
make today a win**. The answer is the must-do set. Then the log file is created with Goal,
Must-do, and the Plan table, and the check-in cron is armed. Completion criterion: every
task Todoist returned is in the Plan table, the must-do set is written, and a cron is
listed.

### Day mode

**Logging.** A message that reports what happened to a task ("Santucci voicemail, Hometown
Hero wants photos") is matched to plan tasks by name. Each outcome maps to a Todoist action:
generic vocabulary is done → complete, later → re-date (ask the date unless the hook's
vocabulary supplies one), new → create in the project, note → log only. The hook's
vocabulary overrides (A2C: voicemail → complete the call, chaser-send task due within the
hour, second call per cadence; bite → complete, Template E task due within the hour, day-3
and day-7 photo chasers; hard no → complete and move the lead to "Checked / ruled out" with
the reason; referral → a task for the new name). Every action gets a timestamped line under
`## Log` and a one-line confirmation naming the task. Two candidate tasks → ask. No outcome
stated → ask what came of it before touching Todoist. Nothing is completed without a stated
outcome.

**The gate.** On-list = a task in today's Plan, a direct dependency of one (its script,
draft, or number), a consequence of a logged outcome (Template E after a bite), or an item
on the hook's always-on-list duties. Anything else Kyle asks for gets one line: *Not on
today's list. Park it, or swap it for <next due task>?* Polish (the hook's polish list plus
the generic set: rebuilding an artifact that works, rewording, re-tiering, reformatting,
improving tooling or this skill during the window) gets the sharper line: *That's polish.
Next up is <task>. Park it for the wrap?* Park → one line in `## Parking lot`. Swap → name
the displaced task, re-date it, do the thing, log it. "Do it anyway" → do it, log it as a
detour with the time. The gate fires once per item; an overridden item is on-list for the
rest of the day. One line, no lecture.

**Check-ins.** One recurring `CronCreate` at an off-minute (`:52`) for every hour inside
the hook's working window (default 9–17 when no hook). The prompt is self-contained: read
today's log and Todoist, post three lines — done since the last check-in, next up, pace
(tasks due by now vs. logged) — and, if two consecutive check-ins found nothing logged, one
direct question about the tasks due since the last log line. Session-only: closing the
terminal kills it; `/day` re-arms it on resume. The last firing inside the window doubles as
the wrap nudge.

### Wrap (`/day wrap`)

1. `CronList` → `CronDelete` the day's job(s).
2. Re-read Todoist `#<project> & (today | overdue)`; list plan tasks still open with no log
   line and ask, in one message, what happened with them.
3. Propose one re-date table (task · proposed date from the hook's cadence or "tomorrow" ·
   reason); apply on Kyle's approval, one `todoist_update_task` per row.
4. Write `## Wrap (HH:MM)`: must-do result · done · slipped → new date · parking lot carried
   forward · tomorrow's first task.
5. Run the hook's wrap step (A2C: rebuild tomorrow's morning-block calendar description
   from tomorrow's Todoist tasks; on Sundays, point at the weekly ritual in
   `september-plan.md`).
6. Print the log path.

Completion criterion: no plan task is left open-and-undated, `## Wrap` exists, no cron
remains.

### Resume

`/day` when today's log exists: read it and Todoist, post three lines (done · next · pace),
re-arm the cron if `CronList` is empty, back in day mode. If `## Wrap` already exists, say
so and append `## Reopened (HH:MM)` only if Kyle wants to continue.

### The day log

```markdown
# 2026-09-08 · A2C Auctions
Goal: one consignor with photos in Zach's inbox by 9/30
Must-do: [ ] Drew text + call · [ ] Native Roots plant · [ ] Groundwork / Bret Peace

## Plan (08:02) · window 08:00–11:00, 11:30–13:30
| Due | Task | Todoist id | Status |
|---|---|---|---|
| 08:00 | Send the staged Zach email (Drafts) | 6h7GG2w7rChgMqcr | |
| 08:05 | 🔥 Drew Mathews (Green Life) text, call 12:00 if quiet | 6hCX2WWqcPGRFF5r | |
…

## Log
- 08:41 Santucci: voicemail. Call task completed; chaser-send task due 09:41; 30-day park task 10/8.
- 09:20 Detour (override): rebuilt the Bayou City opener. 12 min.

## Parking lot
- 09:05 Recolor the Call Sheet headers (polish, parked)

## Wrap (13:40)
…
```

### The hook file (`.claude/day.md`)

Optional, read only by `/day`, formatted per `references/hook-template.md`: `project` /
`project_id`, working window, the standing goal, the re-entry skill, extra morning sources,
the outcome vocabulary table, always-on-list duties, the polish list, the wrap step. Without
a hook the skill runs on Todoist alone with the generic vocabulary and a 9–17 window.

### Relationship to siblings

`/begin` and `/wrap` bookend coding sessions (git state, recap quiz); `/day` bookends a
Todoist-driven day and never runs `/wrap`'s quiz. `reorient` and `rebrief-a2c` are multi-day
re-entry; `/day` points at them when the gap is more than a day. `stage-a2c` and
`replenish-a2c` are routed to, never run inline — prospecting during a call block is the
canonical off-list request. A bulk Todoist triage/cleanup skill is a separate, upcoming
deliverable; `/day` keeps the project tidy day to day once that has run.

## Out of scope

- Bulk Todoist cleanup or triage across projects (separate skill, requested 2026-09-08).
- Multi-day re-entry sweeps.
- Sending anything: email, texts, DMs. Kyle sends.
- Persisting check-ins across sessions (CronCreate is session-only).
- A visual dashboard.

## Acceptance — first live run (Tue 9/8, A2C)

- [ ] Brief lists all 11 Todoist tasks in due-time order with today's calendar window.
- [ ] Must-do set written to `daily/2026-09-08.md`.
- [ ] A reported voicemail completes the right call task and creates the chaser-send task.
- [ ] An off-list request gets the one-line gate; "park" lands in the parking lot.
- [ ] A cron fires at least once and posts the three-line check-in.
- [ ] `/day wrap` leaves no plan task open-and-undated, writes `## Wrap`, deletes the cron, and rebuilds Wed 9/9's morning-block description.

## Follow-ups

- Todoist triage skill (bulk cleanup) — brainstorm next.
- If hourly check-ins land mid-call too often, switch to block-end-only firings.
- Create the `~/Projects/_daily/` fallback only when a folder-less project first uses it.
