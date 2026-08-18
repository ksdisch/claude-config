---
name: mock-panel
description: Mock interview panel for a real upcoming job interview — Claude plays the interviewers in character, grounded in the prep dossier, application file, and JD from the vault, asks one question at a time with realistic follow-ups, then delivers a scorecard debrief and writes a session log so later mocks re-test the weak answers. Use when Kyle wants live practice for a scheduled interview — "mock interview", "mock panel", "practice interview", "interview me for [company]", "rehearse for my interview", "run me through interview questions", "pretend to be the interviewer", "grill me for my [company] interview" — ideally after a prep dossier exists (offer to run interview-prep first if not). NOT for: pressure-testing a plan or design (use grilling), producing the prep dossier itself (use interview-prep / generate-interview-prep-dossier), or career-direction questions (use career-coach). Blocks on Kyle's answers by design — do not auto-invoke in unattended runs (cron/Routine, cloud one-shot, autonomous flows); if reached there anyway, follow the body's unattended note.
---

Run a live mock interview for a real, named, upcoming interview. You are the panel; the user
is the candidate. Everything you ask should be a question this specific panel could plausibly
ask for this specific role — generic question-bank filler is the failure mode this skill
exists to avoid.

## 1. Grounding

Before the first question, gather what exists — never quiz from parametric knowledge alone:

- **Prep dossier**: look in the vault's `30-job-search/dossiers/` for a file matching the
  company (the argument, or ask which interview this is for). This is the primary source —
  its role decoding, technical checklist, and STAR stories define what to probe.
- **Application file** (`30-job-search/applications/`) and **JD**
  (`30-job-search/jd-archive/`) for the same company, when present.
- **Prior mock logs** (`30-job-search/mock-sessions/`, same company): read them, do not
  repeat their questions verbatim, and deliberately re-test every answer a prior debrief
  graded weak — an improved retake is the point of a second session.

No dossier found → say so and offer two paths: run `interview-prep` /
`generate-interview-prep-dossier` first (better), or proceed from a short setup interview
(role, company, who's on the panel, technical vs. behavioral weighting) — one question at a
time.

## 2. Frame the session

Confirm three things in one message, with defaults so a bare "go" starts the session:

- **Panel**: the interviewer roles you'll play, derived from what Kyle knows about the real
  panel (e.g. "two Data Integration team members"). Give them roles, not fictional bios.
- **Length**: default ~10 questions / 30–40 minutes; Kyle can size it.
- **Mode**: **realistic** (default) — stay in character throughout, all feedback held for the
  debrief; or **graded** — 1–2 lines of feedback after each answer, then back in character.

## 3. Run the panel

- **One question at a time. Wait for the answer.** Never stack questions or move on unanswered.
- **Mix the question types** across the session, weighted by what the grounding says this
  panel cares about: behavioral/STAR ("tell me about a time…"), technical
  explain-your-approach (no live coding unless Kyle asks for it), scenario/troubleshooting
  ("a client reports X — walk me through what you check"), and role-specific probes pulled
  from the JD and dossier.
- **Follow up like a real interviewer.** A vague, rambling, or evasive answer gets a pointed
  follow-up ("what did *you* do, specifically?", "what would you check first?") before the
  panel moves on. One follow-up per weak answer is realistic; three is an interrogation.
- **Stay in character** in realistic mode. Kyle can say **"coach me"** at any point to step
  out of character for guidance on the current question, then resume.
- **End with the closer**: "what questions do you have for us?" — and evaluate his questions
  in the debrief too; asking weak questions is a findable, fixable flaw.

## 4. Debrief

After the last question (or whenever Kyle calls it), deliver the scorecard:

- **Per-question table**: the question, a verdict (strong / adequate / weak), and one line on
  what would move it up a grade.
- **Reworks**: for the 2–3 weakest answers, a model answer written in Kyle's voice from his
  real experience (the dossier's STAR stories are the raw material) — never an invented
  accomplishment.
- **Cross-cutting habits**: patterns across answers — burying the result, missing
  quantification, rambling past the answer, underselling the differentiator the dossier says
  to lead with.
- **Drill list**: the 2–3 things to practice before the real interview, concrete enough to do
  tonight.

## 5. Session log

Write the session to the vault at `30-job-search/mock-sessions/{company-slug}-{YYYY-MM-DD}.md`
(create the directory if missing): date, role, mode, each question with its verdict, the
debrief's reworks and drill list. A second run on the same date appends a numbered suffix
rather than overwriting. If the vault isn't reachable from this session, produce the same file
and tell Kyle where to save it — the log is what makes the next mock smarter, so it is never
silently skipped.

## Unattended runs

This skill blocks on the user's answers. In an unattended run (subagent, cron/Routine, cloud
one-shot), do not park on a question: do the grounding, then write a **prep sheet** instead —
the full question set you would have asked, each with a sketch of what a strong answer covers,
saved next to the session logs as `{company-slug}-{YYYY-MM-DD}-prep-sheet.md` — and stop. The
live panel runs when Kyle is present.
