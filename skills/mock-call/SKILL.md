---
name: mock-call
description: Use when Kyle wants to drill a live call against a persona from a teach workspace — "/mock-call", "/mock-call receiver", "run a practice call", "drill me on a lender call". Runs from the workspace (needs MISSION.md and personas/): picks a persona, plays it for 6 to 10 turns by voice (voicemode) or text, then debriefs out of character — handled, missed with each miss named to a term and the doc that covers it, one rewrite — and writes recall-log lines plus a learning record only when teach's criteria are met. Typed-only. NOT for teaching a concept (teach), stocking sources (teach-research), or briefing a real dial (the A2C folder's call-brief).
disable-model-invocation: true
argument-hint: "[persona-slug] [--voice|--text] [--turns N]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, ToolSearch, mcp__plugin_voicemode_voicemode__converse, mcp__plugin_voicemode_voicemode__service
---

# mock-call — drill a call against a persona

One persona, one call, one debrief. The persona is the other end of the phone: it talks the
way its file says, pushes back, and never teaches. The debrief is where the teaching happens,
and it writes only what the workspace's retention files can use.

## Guard

The current directory must hold `MISSION.md` and a `personas/` directory with at least one
`.md` file. Otherwise stop: print the resolved directory, name what is missing, suggest the
learning workspace (`~/Learning/<topic>/`), and write nothing. Never write outside the
current directory.

The workspace must also have something taught to test: `GLOSSARY.md`, or a `lessons/`
directory holding at least one file, or a `reference/` directory holding at least one file.
Lessons count on their own — they are teach's primary unit, and `reference/` is compressed
from them afterward. If none of the three exists, print exactly
`nothing to test yet, run /teach` and stop — before picking a persona, before reading one.
Write nothing.

## Arguments

`/mock-call [persona-slug] [--voice|--text] [--turns N]`

- `persona-slug` matches `personas/<NN>-<slug>.md` or `personas/<slug>.md`. No match → list
  the slugs that exist and stop.
- `--voice` / `--text` pick the medium. Neither → one `AskUserQuestion`: voice or text.
- `--turns N` caps the call at N turns, 6 to 10; default 8. A turn is one persona line and
  one reply from Kyle; the opening line is turn 1.

## Ground (read before the first line)

1. The persona file, whole.
2. `GLOSSARY.md` if it exists; its definitions are the workspace's canonical language.
3. `reference/` if it exists: the cheat sheets. The persona's vocabulary comes from here and
   from its own file, never from memory.
4. Each `./research/` digest the persona's "Who they are" cites, for scenario facts.
5. `recall-log.md` if it exists, for the choice below and the debrief; `learning-records/`
   if it exists, for the debrief only.

## Choosing a persona (no slug given)

For each persona, take its "Terms this persona tests" list and count the **uncovered** terms:
a term with no `hit` line in `recall-log.md`, or whose most recent line is a `miss`. Rank by
the **fraction** uncovered — uncovered ÷ total terms on that persona's list — and pick the
highest fraction, so a long term list never out-ranks a short one on length alone. Ties go to
the lowest file prefix (`01-` before `02-`). Absent files count as zero coverage everywhere,
which puts every persona at 1.0 — a real tie, broken by the prefix. Say the pick, the
fraction, and the count in one line before the call starts.

## The call

**Voice.** Load the tools once: `ToolSearch` with
`select:mcp__plugin_voicemode_voicemode__converse,mcp__plugin_voicemode_voicemode__service`.
Before turn 1, check both services — `service(kokoro, status)` and `service(whisper, status)`;
if either is stopped, say so in one line and run the whole call in text. Each persona line is
one call: `message` is the line, `wait_for_response: true`, `listen_duration_max: 90`. The
transcript that comes back is Kyle's turn.

On a tool error or an empty transcript, retry the same persona line once, unchanged. A second
failure in a row → say "Switching to text" once, re-print that same undelivered persona line
as a text blockquote so Kyle answers the line he never heard, and continue in text from there.
Failed attempts never consume a turn: the turn count advances only when Kyle's reply arrives.

**Text.** Print the persona line as a blockquote and end your turn. Kyle's next message is his
turn. Nothing else in the message: no coaching, no hints, no stage directions.

**In character, both media:**
- Open with the persona's "Opening line". The file says whether Kyle dialed them or they are
  returning his voicemail.
- Talk only the way "How they talk" says. Use at least two of the "Curveballs" before the
  call ends, at the moments they would land on a real call.
- Never break character to teach, correct, or encourage. Never answer a question the persona
  would not answer.
- Never invent a fact about a real person or firm. Scenario facts come from the cited digests
  and belong to the fictional persona's situation.
- End the call when the persona's ask resolves (agrees to the Zack call, agrees to send
  photos, or says no and why) or when the turn cap lands. The persona says goodbye the way a
  person would; then the debrief starts.

## Debrief (out of character)

Print exactly this shape:

```
**Debrief · <persona> · <n> turns · <voice|text>**

Handled
- <the move Kyle made, in one line> (<term it showed>)

Missed
- <what happened, in one line> → <term> · <reference/<file>.html | lessons/<file>.html | not yet taught>

Say it differently next time
- "<what Kyle said>" → "<the rewrite>"

Wrote: recall-log.md (+<k> lines) · <learning-records/<NNNN>-<slug>.md | no learning record: coverage only>
```

Rules: at most three items under Handled; every Missed item names a term from the persona's
list or the glossary; one line only under "Say it differently". No paragraph anywhere in the
debrief.

## Writes

1. **`recall-log.md`**: one line per term the persona actually tested on this call, in the
   form `YYYY-MM-DD · <term> · hit|miss · mock-call`. A term the call never reached gets no
   line. Create the file with its header line if it is missing.
2. **A learning record**, at most one per run, only when teach's LEARNING-RECORD-FORMAT
   criteria are met: Kyle demonstrated genuine understanding of something non-trivial, or a
   misconception was corrected. Coverage alone writes nothing. Follow
   `~/.claude/skills/teach/LEARNING-RECORD-FORMAT.md`: scan `learning-records/` for the
   highest number and increment; create the directory if this is the first record.
3. Nothing else. Not `GLOSSARY.md` (teach promotes terms), not `NOTES.md`, not `MISSION.md`,
   not the persona file.

## Close

One line: the Wrote line again, plus elapsed minutes. Target: ten minutes from the opening
line to the close. Then stop.

## Never

- Never run from a directory that fails the guard, and never write outside it.
- Never quote a number for what equipment is worth, in character or out. Zack prices.
- Never send anything, dial anything, or touch a calendar, Todoist, or Gmail.
- Never let the persona teach mid-call; the debrief is the only teaching surface.
