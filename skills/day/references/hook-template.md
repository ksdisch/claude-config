# Day hook template

Copy to `<project folder>/.claude/day.md` and fill in. `/day` reads it in Phase 0. Every
section is optional except the header lines; leave out what the project doesn't need. Keep
it a restatement of the project's own rules, short enough to read every morning; the
project's files stay the source of truth.

```markdown
# Day hook: <Project name as it appears in Todoist>

project: <Todoist project name>
project_id: <Todoist project id>
window: <working hours, e.g. Mon–Fri 08:00–11:00; where to read today's actual window if it varies>
goal: <the standing goal every day serves, one line>
reentry: </skill to run after a gap of more than a day, e.g. /rebrief-a2c or /reorient>
log_dir: daily/

## Extra morning sources
- <source, what to read, what counts as an overnight item>

## Outcome vocabulary (Kyle says → what to do)
| Outcome | Todoist | Files / follow-through |
|---|---|---|
| <what Kyle says> | <complete / re-date to … / create "…" due …> | <file + section to update, or the next step Claude owes> |

Dates the vocabulary doesn't cover: ask one question, never guess.

## Always on-list (Claude's standing duties)
- <work Claude does unasked or on request that never trips the gate>

## Polish (park it for the wrap)
- <the project's specific tempting tangents>

## Wrap step
1. <what Claude rebuilds or updates when the day closes>
```
