---
name: day
description: Use when Kyle is starting, resuming, or wrapping a working day driven by one Todoist project — "/day", "/day <project>", "/day wrap", "start my day", "what's on today", "log that", "wrap the day". Briefs today's tasks, then keeps the session in day mode: logs outcomes he reports in plain language, gates off-list and polish requests, posts hourly pace check-ins, and wraps by re-dating what slipped. NOT for multi-day re-entry after a gap (reorient, rebrief-a2c), coding-session bookends (/begin, /wrap), bulk Todoist cleanup or triage (separate skill), or sending anything.
---

# Day

The daily bookend for a Todoist-driven day. One Todoist project per run. The morning
brief pins a **must-do** set; the session then runs in **day mode** until `/day wrap`:
Kyle reports outcomes in plain language and the skill logs them, keeps a **parking lot**
for tangents, and posts pace **check-ins** on a session cron. A project can add a
**hook** (`.claude/day.md`) that supplies extra sources, outcome vocabulary, the polish
list, and a wrap step; without one the skill runs on Todoist alone.

**Prime directive:** progress on the list beats improvement of the system. The skill
never sends anything; Kyle sends.

## Arguments

- `/day` — start today, or resume it if `daily/<today>.md` already exists.
- `/day <project>` — same, naming the Todoist project.
- `/day wrap` — close the day (`/day <project> wrap` also works).

## Phase 0 — Resolve the project, the hook, the log

1. Load the tools in one `ToolSearch` call: `mcp__todoist__todoist_search_tasks`,
   `todoist_complete_task`, `todoist_update_task`, `todoist_create_task`,
   `todoist_list_projects`, `CronCreate`, `CronList`, `CronDelete`, plus whatever the hook's
   sources need (Calendar, Gmail).
2. Project, first hit wins: the argument → `.claude/day.md` in the CWD (`project:` line) →
   the CWD's `CLAUDE.md` naming a Todoist project → `todoist_list_projects` and one question.
3. Hook: read `.claude/day.md` if present (format in `references/hook-template.md`). No hook
   → generic vocabulary, window 09:00–17:00, no extra sources.
4. Log directory: `daily/` in the folder that resolved the project (create it); a project
   with no folder uses `~/Projects/_daily/<project-slug>/`. Today's file is
   `daily/YYYY-MM-DD.md`. If the argument is `wrap` → **Wrap**. Else if the file exists →
   **Resume**. Else → **Start**.

## Phase 1 — Start: the brief

Read, in parallel where possible:

- Todoist: `todoist_search_tasks`, filter `#<project> & (today | overdue)`, limit 200.
  Project names with spaces work unquoted.
- The newest prior day log in the directory: its `## Wrap` (carry-overs, tomorrow's first
  task), its `## Parking lot`, and whether it wrapped at all. More than one day old → the
  brief opens with that fact and names the hook's `reentry` skill; the light sources below
  are not a sweep.
- The hook's extra morning sources (today's calendar blocks for the window; a light
  overnight mail check for names on today's list).

Post the brief, in this order and nothing more:

1. `<Weekday date> · <project> · window <from the hook or calendar>`, then the gap line if any.
2. **Overnight** — replies, bounces, anything the hook's sources surfaced that names a task
   on today's list. Bites first. "Nothing new" is a valid line.
3. **Carried over** — from the prior wrap.
4. **Today** — every returned task in due-time order, overdue ones flagged with their
   original date. Task names only; ids go in the log file.
5. **Parking lot** — the prior day's unworked items, one line each.
6. One question: **which one to three of these make today a win?**

Kyle's answer is the must-do set. Then write the log file (format below) with Goal (from
the hook), Must-do, and the Plan table, and arm the check-in cron (see Day mode).

**Done when:** every task Todoist returned is in the Plan table, the Must-do line is
filled, and `CronList` shows the day's job. Answering a question Kyle asks about a task is
part of the brief; doing work on one is day mode.

## Phase 2 — Day mode

Day mode holds from the brief until `/day wrap`. Three behaviors run at once.

### Log

A message that reports what happened to a task is a log entry: "Santucci voicemail,
Hometown Hero wants photos, Zach email sent." For each outcome in the message:

1. Match it to a Plan task by name. Two candidates → ask which. No candidate → ask whether
   it is a new task (create it in the project) or a note (log only).
2. Apply the Todoist action. The hook's outcome vocabulary decides; the generic vocabulary
   is **done** → complete · **later / call back / no answer** → re-date (ask the date unless
   the vocabulary supplies one) · **new** → create in the project, one task per item ·
   **note** → log only. An outcome with no result stated ("talked to Santucci") gets one
   question before Todoist changes.
3. Apply the hook's file updates for that outcome.
4. Append `- HH:MM <task>: <outcome>. <action taken>.` under `## Log`; tick the Must-do
   box if it was one.
5. Confirm in one line per outcome, naming the task and the action.

Questions get answers, not log lines. **Done when:** every outcome in the message has a
log line and an applied action, or a question back.

### Gate

**On-list** is: a Plan task; a direct dependency of one (its script, draft, number, or a
question about the lead); a consequence of a logged outcome (the photo request after a
bite); or an item in the hook's always-on-list duties. On-list work Kyle asks for gets done
and logged.

Anything else gets exactly one line and a choice:

- Off-list: *Not on today's list. Park it, or swap it for <the next due task>?*
- **Polish** (the hook's polish list, plus: rebuilding an artifact that already works,
  rewording, restyling, re-tiering, reformatting, improving tooling or this skill inside
  the window): *That's polish. Next up is <task>. Park it for the wrap?*

Kyle's reply resolves it. **Park** → one line under `## Parking lot`, back to the next
task. **Swap** → name the displaced task, re-date it, do the thing, log it. **Do it
anyway** → do it, log it as `Detour (override)` with the minutes spent. The gate fires once
per item; an overridden item is on-list for the rest of the day. Questions never trigger
the gate.

### Check-ins

At the brief, create one recurring cron for every hour of the working window: minute `52`,
hours from the window's first start hour through its last end hour inclusive, so the final
firing lands just after the window closes and doubles as the wrap nudge. Example for
08:00–11:00 plus 11:30–13:30: `52 8-13 * * *`. Crons are session-only and expire after
seven days, so each morning arms a fresh one and wrap deletes it. Closing the terminal
kills it; Resume re-arms it.

The cron prompt is self-contained, because the session may have compacted by the time it
fires:

```
Day-mode check-in for <project>. Read <absolute log path> and run todoist_search_tasks
with filter "#<project> & (today | overdue)". Reply in three lines: (1) done since the
last check-in, from the log; (2) next up: the earliest due task with no log line; (3)
pace: tasks due by now vs. tasks with a log line. If this is the second consecutive
check-in with no new log line, add one question asking what happened with the tasks due
since the last log line. If the log already has a "## Wrap" section, delete this cron
job (CronList, then CronDelete) and reply with one line saying the day is wrapped.
Nothing else.
```

### Resume

`/day` when today's log exists: read it and Todoist, post three lines (done · next up ·
pace), re-arm the cron if `CronList` is empty, and the session is back in day mode. If
`## Wrap` exists already, say the day is wrapped and continue only if Kyle asks, appending
`## Reopened (HH:MM)`.

## Phase 3 — Wrap

1. `CronList` → `CronDelete` every day-mode job.
2. Re-run the Todoist filter. Plan tasks still open with no log line → one message asking
   what happened with them; log the answers.
3. Propose one re-date table for what is still open: task · proposed date (from the hook's
   cadence, else tomorrow at the same time) · reason. Apply on Kyle's approval, one
   `todoist_update_task` per row. Tasks he calls done → complete.
4. Append `## Wrap (HH:MM)`: must-do result in one line · done · slipped → new date ·
   parking lot carried forward · tomorrow's first task.
5. Run the hook's wrap step.
6. Print the log path.

**Done when:** no Plan task is open without a date, `## Wrap` exists, and `CronList` is
empty. Nothing was sent.

## The day log

```markdown
# 2026-09-08 · A2C Auctions
Goal: one consignor with photos in Zach's inbox by 9/30
Must-do: [ ] Drew text + call · [ ] Native Roots plant · [ ] Groundwork / Bret Peace

## Plan (08:02) · window 08:00–11:00, 11:30–13:30
| Due | Task | Todoist id | Status |
|---|---|---|---|
| 08:00 | Send the staged Zach email (Drafts) | 6h7GG2w7rChgMqcr | |

## Log
- 08:41 Santucci call: voicemail. Completed; chaser-send task due 09:41; second-angle task 10/8.
- 09:20 Detour (override): rebuilt the Bayou City opener. 12 min.

## Parking lot
- 09:05 Recolor the Call Sheet headers (polish)

## Wrap (13:40)
Must-do: 2 of 3. Drew reached, photos promised; Native Roots name obtained; Groundwork slipped → Wed 9/9 13:00.
```

Ids live in the file so the log is exact; in chat, tasks are named.

## The hook

`.claude/day.md` in the project folder, read only by this skill. Write a new one from
`references/hook-template.md`: project and id, window, goal, re-entry skill, extra morning
sources, outcome vocabulary, always-on-list duties, polish list, wrap step. The hook
restates a project's cadence rules for speed; the project's own files stay the source of
truth, and a disagreement is fixed in the hook.

## Red flags

| Drift | Reality |
|---|---|
| Completing a task because Kyle mentioned its name | A log entry needs a stated outcome. "Talked to Santucci" gets a question first. |
| Guessing a re-date | The vocabulary supplies it or Kyle does. One question beats a wrong date. |
| Doing a polish request because it's quick | Quick is how the morning goes. One line, park or swap, then the next task. |
| Re-challenging an overridden item | The gate fires once per item per day. |
| A paragraph of pushback | The gate is one line and a choice. |
| A check-in prompt that assumes the skill is loaded | The session may have compacted; the prompt carries its own instructions. |
| Treating the light mail check as a sweep | Gap of more than a day → say so and name the re-entry skill. |
| Sending a draft, text, or DM | Kyle sends. Always. |
| One Todoist task listing several contacts | One task per item, in the project. |
| Running a sibling skill mid-window because it would help | It's off-list. Park it for the wrap or the next planning slot. |
| A wrap that leaves open tasks undated | Every open Plan task gets a date or a completion before the file closes. |
