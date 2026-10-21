---
name: compass
description: Run the confusion-compass learning loop on any topic, concept or tool, with one durable markdown file per topic in ~/Learning/compass/. `/compass <topic>` resumes the topic it fuzzy-matches (asking when several match, offering a new topic when none do) or starts one by capturing why Kyle is learning it, turns his loose confusion into numbered questions he confirms, and answers the next open question tight and with cited sources (web search, local files, the repo at hand). A bare `/compass` lists every topic with its counts, status and last-touched date. The topic file is rewritten and validated by `scripts/compass.py check` after every change. Use when Kyle types /compass, or says "compass this", "start a compass topic", "I'm confused about X, help me learn it", "turn my confusion into questions" — even without naming the skill. NOT for building a teach workspace (teach-research), breaking down a video (youtube-breakdown), or a reference page of what a session covered (session-reference).
---

# Compass

Confusion is the signal. The loop: notice it, convert it into written questions, answer those
specific questions, repeat with the follow-ups. Everything lives in one topic file so a return to
the topic never starts from zero.

- Topic files: `~/Learning/compass/<slug>.md` — one flat folder, one file per topic.
- File format (the contract): `references/file-format.md`. Read it before the first write of a
  session.
- Helper: `python3 ~/.claude/skills/compass/scripts/compass.py check <file>` — read-only, JSON out,
  exit 0 only when the file is valid. The helper never writes; you do all writing. Its `match` and
  `list` subcommands read the folder (see *Resolve the topic* and *List topics*).

## Prime directives

1. **The why comes first.** No question is logged on a topic without a why in its frontmatter.
2. **Kyle's questions, not yours.** Converted questions are shown to Kyle and logged only after he
   confirms or edits them.
3. **Every answer cites its sources.** No sources, no `answered` status.
4. **Write, then check, after every change.** Every new question, answer and status change is
   written to the file immediately, with `updated` bumped to today, then `check` runs. If `check`
   reports anything, fix the file and re-run until it exits 0 before saying anything else to Kyle.
   Never continue the loop on a file that fails `check`.
5. **Write only topic files.** Never write into a teach workspace, a file a topic was seeded from,
   or anywhere outside `~/Learning/compass/`.

## Resolve the topic

`/compass <topic>`:

1. Run `python3 ~/.claude/skills/compass/scripts/compass.py match "<topic>"`. It matches the
   query case-insensitively against every topic's slug and display name and prints
   `{"result": "single" | "several" | "none", "matches": [{"slug", "topic", "status"}]}`.
2. Act on `result`:
   - **`single`** → *Resume* `~/Learning/compass/<slug>.md`.
   - **`several`** → show the candidates (display name and slug) and ask which one Kyle meant.
     Resume the one he picks; never guess.
   - **`none`** → say nothing matched and offer to start "<topic>" as a new topic. Create
     nothing until he says yes; if he says no or corrects a typo, run `match` again on what he
     gives you.
3. Starting a new topic: create `~/Learning/compass/` if it doesn't exist, and derive the slug:
   lowercase; letters and digits kept; every run of anything else becomes one `-`; no leading or
   trailing `-`; cut to about 60 characters at a hyphen. `Rust lifetimes & borrows` →
   `rust-lifetimes-borrows`. Then *Start a new topic*.

A bare `/compass` with no topic is *List topics*.

## Resume

1. Read the topic file. Open with one orienting glance: the topic, its why, the counts per
   status (`3 open · 4 answered · 1 parked · 0 prereq`), and the next open question by *Ordering*
   — its number and text. If nothing is open or prereq, say so and ask what confuses him now.
2. Continue the loop from that question (*Answer*), or take new confusion through *Form
   questions*.
3. This is a new session: its first write appends a new dated entry to the session log, even
   when an entry for today already exists from an earlier session (see *Session log*).

## List topics

Bare `/compass`: run `python3 ~/.claude/skills/compass/scripts/compass.py list` and print one row
per topic from its `topics` records, in the order given:

| Topic | Why | Open | Answered | Parked | Prereq | Status | Last touched |
|---|---|---|---|---|---|---|---|

Topic is the display name with the slug after it in backticks; Why is the record's shortened
`why` as given; Last touched is `last_touched`. With no topics, say there are none yet and that
`/compass <topic>` starts one. Then ask which topic to pick up; his answer goes through *Resolve
the topic*.

## Start a new topic

1. **Ask the why, and nothing else yet.** "Why are you learning <topic> — what will you do with
   it?" Wait for the answer. Reduce it to one plain line in Kyle's words.
2. **Write the file** with frontmatter (`topic` as Kyle named it, `why`, `status: open`, empty
   `workspace:`, `created` and `updated` today), a `# <topic>` title, an empty `## Questions`
   and a `## Session log` with today's entry (`- YYYY-MM-DD — Started.`). Run `check`.
3. Ask what confuses him.

## Form questions

1. Kyle describes his confusion loosely. Convert it into specific, answerable questions — one
   idea each, phrased so an answer could settle it. Number them as they'd be logged (next free
   top-level numbers, per the format's numbering rule).
2. Show the list and ask him to confirm or edit. Apply his edits; drop what he drops.
3. Log only the confirmed questions, each `status: open` with an empty `last recalled:`.
   Write, `check`.

## Answer

Answer the next open question by default — don't ask which one.

1. **Ground it.** Use what the question needs: web search and fetch for current or external
   facts, local files Kyle points at, and the repo you're in (read and grep) when the question is
   about code. Memory alone is not a source.
2. **Keep it tight and aimed at the question asked** — the smallest answer that settles it, a few
   short paragraphs at most. Don't survey the topic or answer neighbouring questions.
3. **Cite.** Give the answer in chat with its sources, then log it: `#### Answer` with the answer,
   `#### Sources` as a bullet per source (title + URL; local path; repo `path:line`),
   `status: answered`, `answered by: claude`. Write, `check`.
4. Ask whether it landed, then move to the next open question or take new confusion back
   through *Form questions*.

## Ordering

The next question is the first `prereq` question, else the open question that most directly
serves the why. Say which one you picked when it isn't simply the lowest-numbered open one.

## Session log

One dated entry per session. The first write of a session appends `- YYYY-MM-DD — <what moved>`;
later writes in the same session revise that same entry (`Logged Q3–Q5; answered Q3.`) rather
than adding more.
