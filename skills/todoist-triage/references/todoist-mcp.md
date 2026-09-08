# Todoist MCP: what it can and cannot do

Verified 2026-09-08 against Kyle's account through the `mcp__todoist__*` server. Re-verify
any line that a run contradicts, then fix it here.

## Tools

`todoist_search_tasks(filter, limit≤200)` · `todoist_list_projects()` ·
`todoist_list_sections(project_id)` · `todoist_list_labels()` ·
`todoist_complete_task(task_id)` · `todoist_update_task(task_id, content?, description?,
due_string?, labels?, priority?, project_id?, section_id?, parent_id?)` ·
`todoist_create_task(content, …same fields…)` · `todoist_create_project(name, parent_id?,
color?)`.

**Missing:** delete a task · read one task by id · the full description (previews truncate
at 200 characters) · completed-task history · archive, delete, rename, or reparent a
project · create a section · create or delete a label.

## Filters

- Native Todoist syntax. `limit` caps at 200; `truncated: true` means split the query.
- `overdue`, `today`, `7 days`, `no date`, `p1`–`p4`, `@label`, `search: <text>` work.
- `#Project` and `##Parent` (with children) work when the name has no `&`. `##Work /
  Career & no date` is fine. `#Admin & Finances & no date` returns "invalid filter" because
  `&` is the AND operator. Ten of Kyle's projects contain `&`, so partition by
  `project_id` client-side instead of filtering by those names.
- `created after: YYYY-MM-DD & created before: YYYY-MM-DD` partitions correctly (130
  undated tasks before 2026-01-20 verified). `created before:` on its own is ignored and
  returns everything. `created after:` alone works.
- Project names with spaces need no quotes.

## Writes

- `due_string` takes natural language: `tomorrow 9am`, `every sunday 5pm`, `Oct 1`.
- `update_task` moves via `project_id` / `section_id` / `parent_id` in the same call as
  other fields.
- `labels` on update replaces the whole list; pass the existing labels plus the new one.
  Whether an unknown label name auto-creates a personal label is **unverified**: test on
  the first labelled move and stop if the label doesn't appear.
- `description` on update replaces the whole description. Combined with the 200-character
  read cap, that makes any description write lossy; the skill forbids it except on an empty
  preview.
- `complete_task` returns `{completed, task_id}`; there is no uncomplete.
