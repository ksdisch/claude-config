---
name: compass
description: Run the confusion-compass learning loop on any topic, concept or tool, with one durable markdown file per topic in ~/Learning/compass/. `/compass <topic>` starts a topic by capturing why Kyle is learning it, turns his loose confusion into numbered questions he confirms, and answers the next open question tight and with cited sources (web search, local files, the repo at hand). The topic file is rewritten and validated by `scripts/compass.py check` after every change. Use when Kyle types /compass, or says "compass this", "start a compass topic", "I'm confused about X, help me learn it", "turn my confusion into questions" — even without naming the skill. NOT for building a teach workspace (teach-research), breaking down a video (youtube-breakdown), or a reference page of what a session covered (session-reference).
---

# Compass

Confusion is the signal. The loop: notice it, convert it into written questions, answer those
specific questions, repeat with the follow-ups. Everything lives in one topic file so a return to
the topic never starts from zero.

- Topic files: `~/Learning/compass/<slug>.md` — one flat folder, one file per topic.
- File format (the contract): `references/file-format.md`. Read it before the first write of a
  session.
- Helper: `python3 ~/.claude/skills/compass/scripts/compass.py check <file>` — read-only, JSON out,
  exit 0 only when the file is valid. The helper never writes; you do all writing.

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

1. Derive the slug: lowercase; letters and digits kept; every run of anything else becomes one
   `-`; no leading or trailing `-`; cut to about 60 characters at a hyphen. `Rust lifetimes &
   borrows` → `rust-lifetimes-borrows`.
2. Create `~/Learning/compass/` if it doesn't exist.
3. If `<slug>.md` exists, read it and continue the loop from its next open question (see
   *Ordering*). Otherwise start a new topic.

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
