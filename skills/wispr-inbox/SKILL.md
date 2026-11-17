---
name: wispr-inbox
description: Sweep Kyle's Wispr Flow scratchpad notes added since the last run and route each item — todos into Todoist on his yes, life data into one paste block for the Life Nodes logging chat, learning questions into suggested /compass starts, the rest listed. Use when Kyle types /wispr-inbox, or says "process my Wispr notes", "inbox my notes", "what did I dictate" — even without naming the skill. NOT for meeting recordings or transcripts (ask the Wispr connector directly), or logging a message he types here (that's Life Nodes' log).
---

# wispr-inbox

Kyle dictates loose notes into Wispr Flow's scratchpad during the day. This skill is the
**inbox sweep**: read what's new, sort every item into a **lane**, show the sort, write only
after his yes. The Wispr connector is read-only, so "new" is tracked by a local
**watermark**, never by changing the notes.

## Arguments

- `/wispr-inbox` — sweep everything since the watermark.
- `/wispr-inbox <window>` — sweep a window instead ("today", "since Monday", "last 3 days");
  the watermark still advances only to the newest note swept.

## The lanes

| Lane | Prefix that forces it | What lands here | What happens on yes |
|---|---|---|---|
| **todo** | `todo:` | Something Kyle has to do: call, email, buy, fix, follow up | One Todoist task each |
| **log** | `log:` | Something he did, took, drank, slept, earned or worked | One line in the Life Nodes paste block |
| **learn** | `learn:` | A question or confusion he wants to understand | A suggested `/compass` start |
| **keep** | `keep:` | An idea, reference or thought worth seeing again | Listed in the report only |
| **skip** | — | Chatter, test dictation, talk to the dog, fragments with no content | Counted, not listed |

A prefix at the start of an item (case-insensitive, colon optional: "todo call mom") forces
its lane and is stripped from the text. Without one, infer the lane from the content. When an
item could sit in two lanes, pick the one with an action (todo over keep, log over keep) and
mark it `?` in the sort.

## Steps

### 1. Load and read the watermark

1. One `ToolSearch`: `mcp__claude_ai_Wispr_Flow__search_scratchpad_notes`,
   `mcp__claude_ai_Wispr_Flow__get_scratchpad_note`, `mcp__todoist__todoist_create_task`,
   `mcp__todoist__todoist_list_projects`.
2. Read `~/.claude/state/wispr-inbox.json`:
   `{"watermark": "<ISO UTC>", "processed": {"<note_id>": "<modified_at>"}}`.
   Missing file → first run: the window is the last 7 days, and the report's first line says so.
3. Read the clock: `TZ=America/Chicago date +%Y-%m-%dT%H:%M:%S%z`. All times shown to Kyle are
   America/Chicago; the connector returns UTC.

**Done when:** the window's start is fixed (watermark, argument, or the 7-day default).

### 2. Fetch every note in the window

1. `search_scratchpad_notes` with `since` = the window start and `limit` 200. Page with
   `next_cursor` until `has_more` is false.
2. Drop a note whose id is in `processed` with the same `modified_at` (already swept). A note
   in `processed` with a newer `modified_at` was edited since: keep it, and tag its items
   `edited` so Kyle can tell them from fresh ones.
3. `get_scratchpad_note` for each remaining note; follow the truncation marker until the whole
   text is read. An excerpt is never enough to sort from.

**Done when:** every note in the window is fully read or dropped as already swept. Zero notes
→ reply "Nothing new in Wispr since <local time>" and stop without touching the state file.

### 3. Split and sort

1. Split each note into **items**: one per distinct thing said. A note holding "ran 4 miles,
   call the dentist about Thursday, and why does my knee click" is three items.
2. Give each item a lane (table above).
3. **Anchor relative dates** to the note's own local date, because Kyle reads and pastes this
   later: "yesterday" in a note from Tue Nov 17 becomes "Mon Nov 16"; "tonight" becomes
   "Tue Nov 17 evening". Clock times stay exactly as he said them.
4. Per lane, build the payload:
   - **todo**: a short imperative task title, plus a due string only if he said one
     ("Thursday", "by Friday 5pm", anchored per step 3). No project unless he named one that
     `todoist_list_projects` returns; otherwise it goes to Inbox.
   - **log**: the item as a first-person sentence in his words, date-anchored, e.g.
     "Mon Nov 16: ran 4 miles in the morning". Never add amounts, units or times he didn't say;
     the logging chat asks for what's missing.
   - **learn**: the question as he'd ask it, plus the topic name for `/compass`.
   - **keep**: one line.

**Done when:** every item in every note is in exactly one lane.

### 4. Show the sort and wait

One numbered list grouped by lane, items in note order inside each lane:

```
Wispr inbox · 6 items from 3 notes · since Mon Nov 16 9:40 PM

todo
 1. Call the dentist about Thursday's appointment · due Thu Nov 19
 2. Email Chamberlain recruiter back ?  (could be keep)
log
 3. Mon Nov 16: ran 4 miles in the morning
learn
 4. Why does my knee click when I squat? → /compass knee mechanics
keep
 5. Idea: a Wispr lane for gift ideas
skip: 2 items (dictation tests)

Create the 2 Todoist tasks? Fix any line first ("2 is keep", "drop 5", "1 due Friday").
```

Kyle's reply can move, edit or drop any line; rebuild and show only the changed lines, then
ask again. Nothing is written before a yes. No todo items → skip the question and go to step 6.

### 5. Write the todos

On yes, create each todo with `todoist_create_task`: `content`, `due_string` if any, and
`project_id` from `todoist_list_projects` if he named a project. Report each one's result. A failed create is named with its error, and the other
tasks still go; that item stays listed under **Not done** in step 6.

### 6. Hand off, then advance the watermark

1. **log** items → one fenced block, ready to paste into the Life Nodes logging chat, one item
   per line, nothing else in the block. Above it: "Paste into the Life Nodes logging chat."
   This skill never writes the vault: `log` runs only inside that project.
2. **learn** items → each as its `/compass <topic>` line with the question, for Kyle to start
   when he wants. Don't start one.
3. **keep** items stay in the report as shown.
4. Write `~/.claude/state/wispr-inbox.json` (create the folder if missing): `watermark` = the
   newest `modified_at` swept, `processed` gains every swept note's id and `modified_at`. Drop
   `processed` entries older than 30 days. Write it **only after** step 5 finished or there
   were no todos, so a crash mid-run sweeps the same notes again rather than losing them.

**Done when:** every todo is created or listed under Not done, the paste block and compass
lines are shown, and the state file holds the new watermark.

## Hard limits

- Wispr is read-only here: this skill only searches and reads notes.
- Todoist gets `create_task` only, and only after Kyle's yes to the exact lines shown. It
  completes, edits and deletes nothing.
- The Life Nodes vault is reached only through Kyle's paste into its logging chat.
