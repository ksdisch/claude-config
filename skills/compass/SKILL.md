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

## Seed from a file (`--from`)

`/compass <topic> --from <path>` starts a topic from context Kyle already wrote down: a teach
workspace's `MISSION.md`, a youtube-breakdown note, any notes file. The seed file is read-only.

1. **Only when starting.** If the topic resolves to an existing file, refuse with one line and
   carry on as a normal resume: "`--from` only seeds a new topic; <topic> already exists, so I'm
   resuming it." Never fold the seed into an existing topic.
2. **Read the seed.** If the path can't be read, say so and fall back to *Start a new topic*.
3. **Find the workspace.** The seed belongs to a teach workspace when its own folder, or a parent
   folder up to and including `~/Learning`, holds a `MISSION.md` (`research/` digests sit one
   level below it). That folder is the workspace; record its path, with `~` for the home folder.
   Otherwise `workspace:` stays empty.
4. **Propose, don't decide.** From the seed, draft a one-line why in Kyle's terms and three to
   five starter questions (one idea each, numbered `Q1`… as they'd be logged). Show both, along
   with the workspace link if there is one, and ask him to accept or edit. Nothing is written
   until he answers. If he rejects the drafted why, ask the why as in *Start a new topic*.
5. **Write.** Once he's settled, write the file as in *Start a new topic* step 2, with the
   accepted why, `workspace:` set as found, the accepted questions logged `status: open` with an
   empty `last recalled:`, and a session-log entry `- YYYY-MM-DD — Started from <seed path>;
   logged Q1–Qn.` Then run `check`.
6. **Continue** with *Answer* on the first open question, or take new confusion through *Form
   questions*.

Never write into the seed file, the workspace, or anything inside it (prime directive 5). The
topic file links to the workspace; the workspace never learns about the topic.

## Form questions

1. Kyle describes his confusion loosely. Convert it into specific, answerable questions — one
   idea each, phrased so an answer could settle it. Number them as they'd be logged (next free
   top-level numbers, per the format's numbering rule). No questions, confusion that amounts to
   "what is any of this?", or a question that drifts from the why: see *Loop defenses*.
2. Show the list and ask him to confirm or edit. Apply his edits; drop what he drops.
3. Log only the confirmed questions, each `status: open` with an empty `last recalled:`.
   Write, `check`.

## Answer

Answer the next open question by default — don't ask which one.

1. **Ground it.** Use what the question needs: web search and fetch for current or external
   facts, local files Kyle points at, and the repo you're in (read and grep) when the question is
   about code. Memory alone is not a source. If it can't be answered usefully — a missing
   prerequisite, or a source that's the problem — go to *Loop defenses* first.
2. **Keep it tight and aimed at the question asked** — the smallest answer that settles it, a few
   short paragraphs at most. Don't survey the topic or answer neighbouring questions.
3. **Cite.** Give the answer in chat with its sources, then log it: `#### Answer` with the answer,
   `#### Sources` as a bullet per source (title + URL; local path; repo `path:line`),
   `status: answered`, `answered by: claude`. Write, `check`.
4. Ask whether it landed, then move to the next open question or take new confusion back
   through *Form questions*.

## Let me try

On any question, Kyle can say "let me try" (or "let me answer that", "I'll take this one") and
answer it himself first. The question is the one on the table, or the one he names by number.

1. **Hand it over.** Name the question and wait. Give no answer, hint or outline before his
   attempt. If he gives up partway ("just tell me"), go to *Answer* and log `answered by: claude`.
2. **Check it against sources.** Ground the check exactly as you would ground an answer — his
   attempt is a claim to verify, not a source. Split it into what holds up and what doesn't.
3. **Reply: affirm, then correct.** Say specifically what he got right. Correct each wrong or
   missing piece in a sentence or two, each with its source. Don't rewrite a right answer into
   your own words.
4. **Log it.** `#### Answer` is his answer as checked: what held up, then a `Correction:` line
   per fix (none when it all held up). `#### Sources` lists what the check rested on — at least
   one, even when he was entirely right. `status: answered`, `answered by: kyle`. Write, `check`.
5. **Never log a wrong attempt uncorrected.** Every error in his attempt is either fixed in the
   logged Answer or the question isn't logged as answered. If he disputes a correction, look
   again; if the sources still don't settle it, leave the question `open`, write no Answer, and
   say what would settle it.

## Follow-ups

Follow-ups come out of an answer — Claude's or Kyle's checked one — or out of Kyle's reaction to
it ("wait, then why…").

1. **Convert and confirm.** Turn them into questions the way *Form questions* does: one idea
   each, shown to Kyle, logged only once he confirms or edits them.
2. **Number them under their parent.** The parent is the question whose answer produced the
   follow-up — a follow-up of Q3's answer is Q3.n, one of Q3.1's is Q3.1.n — using the parent's
   next free child number (one above its highest existing child). A question that isn't about
   any logged question is a new top-level one.
3. **Numbers are stable for life.** Never renumber, never reuse a number, never move a question
   to another parent. If one turns out to belong elsewhere, leave it and log the right question
   fresh under the right parent.
4. **Log** each as `status: open` with an empty `last recalled:`, placed after the parent's last
   descendant so the file reads in tree order. Write, `check`.

## Loop defenses

Four ways the loop stalls, each with its defense. All of them happen inside the session, in
your own words; never hand any of this off to another skill.

### No questions

When Kyle says he has no questions ("makes sense", "nothing yet", "I think I get it"), don't
move on or summarize. Ask the trigger prompt, framed against the stored why: "What does this
change about why you're learning <topic> — <why, in his words>?" Push once more if he still has
nothing ("what would you do differently now when you <why>?"). Whatever confusion it surfaces
goes through *Form questions*. Nothing is written unless it produces questions.

### Too new: the overview

When Kyle's confusion amounts to "what is any of this?" — he can't name a specific question, or
every question he offers is the whole topic — offer an overview first: "You're new enough that a
short map would help before questions. Want one?" Write nothing unless he says yes.

1. **Ground it** as you would an answer (*Answer* step 1) and keep it short: five to eight key
   ideas, each a numbered line with the term in bold and one sentence; a `How they connect:`
   paragraph of a few sentences; a `Sources:` line followed by one bullet per source.
2. **Write it** into `## Overview`, above `## Questions`. If the file already has an overview,
   revise that one in place; never add a second. Write, `check`.
3. **Ask again, straight away:** "With that map, what's confusing?" His answer goes through
   *Form questions*. The overview is a map for forming questions, not reading to finish.

### Drift: park and unpark

The why is the filter. When a question doesn't serve the why — while converting confusion in
*Form questions*, choosing the next question, or logging a follow-up — propose parking it with
a one-line reason that names the gap against the why: "Park Q4? Variance matters for library
authors; your why is reading errors."

1. **Park only on confirmation.** If he says no, it stays as it is (or is logged `open`). If the
   question has open follow-ups under it, propose parking them in the same breath; each needs
   its own yes.
2. **Log it.** `status: parked` and `- park reason: <the one line>`, kept in the file. A question
   that drifted before it was ever logged is logged straight as parked. Write, `check`.
3. **Unpark on request.** When he asks ("unpark Q4", "let's do the variance one"), set it back to
   `status: open`, remove its `park reason` line, and note it in the session log (`Unparked Q4:
   <why it matters now>`). Write, `check`. It joins the queue under *Ordering*.

### Unproductive confusion: prereqs and bad sources

1. **Missing prerequisite.** When a question can't be answered usefully because Kyle is missing
   something it depends on, say so plainly before answering anything: "Q3 won't land until you
   know what a NetworkPolicy is." Log the missing piece as a new question numbered under the one
   it blocks (the next free child, per *Follow-ups* step 2), `status: prereq`, with an empty
   `last recalled:`, and note it in the session log (`Q3 blocked; logged Q3.1 (prereq)`). Write,
   `check`. It is now at the top of the queue (*Ordering*): answer it next. Once it's answered,
   go back to the question it blocked.
2. **Bad source.** When the source Kyle is learning from is the problem — wrong, out of date,
   skips the step he's stuck on — say so and name what's wrong with it, with evidence. Suggest
   a better source (title + URL or path) for that specific gap, and note the swap in the
   session log. Don't relabel his confusion as his fault when the material is at fault.

## Ordering

When choosing the next question, consider only `prereq` and `open` questions; answered and
parked questions are never offered.

1. **Prereq first.** Any `prereq` question comes before every open one — the one blocking the
   question Kyle was on, else the lowest-numbered.
2. **Then by the why.** Rank open questions by how directly answering them serves the stored
   `why`. Break ties by tree order (Q1.2 before Q2).
3. **Say why when it isn't obvious.** When the pick isn't simply the lowest-numbered open
   question, name it and give the reason in one clause ("Q4 next — it's the one your why turns
   on"). Kyle naming a question by number overrides the order.

## Session log

One dated entry per session. The first write of a session appends `- YYYY-MM-DD — <what moved>`;
later writes in the same session revise that same entry (`Logged Q3–Q5; answered Q3.`) rather
than adding more.
