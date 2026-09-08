---
name: todoist-triage
description: Use when Kyle's Todoist has overflowed and needs a bulk cleanup — an Inbox full of auto-captures, dozens of overdue tasks, hundreds of undated ones, a project tree to collapse — or for the periodic pass that keeps it clean: "/todoist-triage", "/todoist-triage inbox", "/todoist-triage weekly", "/todoist-triage map", "clean up my Todoist", "triage my Todoist", "my Inbox is a mess", "weekly review". Proposes dispositions bucket by bucket and writes only after each bucket is approved. NOT for one project's working day (day), ticket triage in a repo (triage), or generating new tasks.
---

# Todoist triage

Bulk cleanup and periodic hygiene for Kyle's whole Todoist. A run takes an **inventory**
snapshot, settles the **map** (the target project tree) once, then works through
**buckets**: one proposal table, one approval, one apply, one verified log entry per
bucket. Every task gets a **disposition**: done · dropped · re-date · move · Someday ·
Reference · rewrite. Nothing is written before its bucket is approved.

Ground rules:

- **There is no delete.** Done → complete. Dropped → append ` (dropped M/D)` to the
  content, then complete. Projects can't be archived, reparented, or given sections from
  here; the wrap lists what Kyle archives by hand.
- **Never write a task's description.** The API shows only its first 200 characters, so a
  write would destroy the rest. Notes go in a content suffix or the run log. The one
  exception is bucket 7, and only when the preview is empty.
- **State lives in `~/Projects/_todoist/`** (`map.md`, `inventory-YYYY-MM-DD.json`,
  `triage-YYYY-MM-DD.md`), never in a repo: task text carries rent, banking, and health
  details.
- Read `references/todoist-mcp.md` before the first query. It lists what the MCP can and
  cannot do and the filters that fail.

## Arguments

- none → the full cleanup, resumable: Phase 0, Gate 1 if the map isn't approved, then
  buckets 1–7 in order, skipping any the newest run log marks done.
- `inbox` → Phase 0 (Inbox only) + bucket 4.
- `weekly` → Phase 0 + the weekly review (below).
- `map` → Phase 0 + Gate 1, even if a map is approved.

## Phase 0 — Inventory

1. Load in one `ToolSearch`: `mcp__todoist__todoist_search_tasks`, `todoist_list_projects`,
   `todoist_list_sections`, `todoist_list_labels`, `todoist_complete_task`,
   `todoist_update_task`, `todoist_create_task`.
2. Read `~/Projects/_todoist/map.md` (its `status:` line) and the newest `triage-*.md`
   (which buckets are done, where a sitting stopped).
3. Pull every open task, partitioned so no query truncates (limit 200; `truncated: true`
   means split further): `overdue` · `today` · `!no date & !overdue & !today` ·
   `no date & created after: <A> & created before: <B>` in windows (start with quarters;
   halve any window that truncates). Partition by project **client-side** from
   `project_id`; project names containing `&` can't be filtered.
4. Pull projects, every project's sections, and labels.
5. Write `inventory-YYYY-MM-DD.json` and post the totals: open · overdue · Inbox · undated ·
   per top-level project with children rolled up · the finished-project and empty-duplicate
   candidates.

**Done when:** no partition is truncated, and the four date partitions sum to the count of
distinct ids in the snapshot.

## Gate 1 — The map

Skip when `map.md` says `status: approved` and the argument isn't `map`; still ask about any
project the inventory shows that the map doesn't name.

Build the table from the inventory: every project → **keep** / **absorb into <parent>** /
**finish and archive** / **archive (empty duplicate)**, with labels. The section rule for
absorbed tasks: dated → Active · undated and actionable → Someday · a note, list, or
checklist → Reference. Present the table and the label list. Kyle approves or edits rows;
write `map.md` with `status: approved YYYY-MM-DD`. **Nothing moves before that line
exists.**

## The bucket loop

Every bucket runs the same five steps:

1. **Propose.** From the snapshot, one table: `task · project · due · disposition · target ·
   confidence · why`. Target is the new project and section, label, or date. Confidence is
   `obvious` (a rule decided it) or `judgment` (Kyle decides). Cap a table near 40 rows;
   larger buckets split into sittings A, B, C.
2. **Ask once:** apply all · apply obvious only · edit rows (Kyle names the row and the
   change) · skip. "Apply obvious" leaves the judgment rows for the next sitting.
3. **Apply.** Re-read the bucket's filter first; a task that changed since the snapshot is
   skipped and noted. One write per task. Suffixes: ` (dropped 9/8)` · ` (dup of <kept
   task's first words>)`.
4. **Verify.** Re-run the bucket's filter; the residue must equal the rows Kyle skipped or
   edited out. A mismatch is reported, never absorbed.
5. **Log.** Append to `triage-YYYY-MM-DD.md`: bucket, sitting, counts, one line per task
   (`id · content · disposition · target`), then `bucket N: done` or `paused at row K`.

## The buckets

1. **Finished projects.** A project whose open tasks all belong to a dated event that has
   passed, with nothing recurring and nothing due ahead (an interview-prep project after the
   interview). Default: complete every task; Kyle pulls any row to Someday. The project
   joins the archive list.
2. **Duplicates.** Same content after normalising case and punctuation, or the same subject
   plus the same amount, case number, or deadline. Keep the newer or richer one; the other
   gets ` (dup of …)` and completes.
3. **The collapse.** Every task in an absorbed project → the parent, section by the map's
   rule, labels per the map. Obvious for dated tasks; judgment only on undated ones the rule
   can't place. **The first labelled move is a test:** if the label isn't on the task
   afterward, stop, print the label list for Kyle to create in the app, and resume when he
   says so. Emptied projects join the archive list.
4. **Inbox.** Every Inbox task → project (plus label) and one of: date · Someday · Reference ·
   done · dropped. Auto-captures whose stated deadline has passed default to `done`, obvious
   when the content names the date. A bare quick-add gets a one-line question in the `why`
   column rather than a guess. Inbox ends empty.
5. **Overdue honesty pass** outside Inbox. Each → done · re-date (the next weekday morning,
   or the cadence the content states) · Someday · dropped. Recurring overdue → the next
   occurrence.
6. **Undated per project.** Each → date (proposed) · Someday · Reference · dropped. Goal
   bullets, checklists, and outlines → Reference. Placeholder rows (`task 1`, `Chase`,
   `Fico`) → dropped unless Kyle claims them.
7. **Pasted-text titles.** Content longer than about 120 characters or more than one
   sentence → a verb phrase under 80 characters. The original text moves to the description
   only when the preview is empty; otherwise the content stays and the row is logged for
   Kyle.

## Weekly review (`weekly`)

Kyle's own four steps, each run through the bucket loop:

1. Inbox to near-zero → bucket 4.
2. Active honesty pass → bucket 5 over `overdue | today | 7 days`.
3. Waiting-for sweep → `@waiting-on`: anything older than 14 days proposes a nudge task or
   a drop.
4. Date cleanup → tasks due in the next 7 days with no time, or several stacked on one day:
   propose the spread.

Sundays. **Done when** all four tables are applied or skipped and the log says
`weekly: done`.

## Wrap

- Post the counts per bucket, the **archive list** (projects now empty, plus the empty
  duplicate tree), any labels to delete by hand, and the buckets still open.
- First full run only: create one recurring task in Routines & Planning,
  `Weekly review: run /todoist-triage weekly`, due `every sunday 5pm`. Never a batch task.
- Hand off: `/day` runs the day-to-day on a clean project.

## Red flags

| Drift | Reality |
|---|---|
| Writing before the bucket is approved | Propose, ask, then apply. The map gate and each bucket's approval are the only writes. |
| Writing a description | It truncates at 200 characters on read; a write erases the rest. Content suffix or run log. |
| Completing a stale task because it's old | Stale means Someday or a question, unless the deadline itself has passed. |
| Guessing a project for a bare quick-add | One line in the `why` column asks; the row waits. |
| A 120-row table | Split into sittings. Forty rows is a sitting. |
| `#Admin & Finances` in a filter | Invalid query. Partition client-side by `project_id`. |
| `created before:` alone | Ignored by the API; pair it with `created after:`. |
| Reporting a bucket done without the re-query | Verify is step 4, every bucket. |
| A batch task listing several items | One task per item. |
| Personal task text in the repo | State goes to `~/Projects/_todoist/`. |
