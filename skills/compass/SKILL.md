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
