# onboard — design spec

**Date:** 2026-08-03
**Status:** proposed design, pre-implementation
**Deliverable:** one new skill at `skills/onboard/SKILL.md` (auto-invocable as `/onboard` via the `~/.claude/skills` symlink), plus the same-commit row in `docs/command-skill-reference.md` and card in `docs/usage-playbook.md`. Nothing else changes.
**Lineage:** original idea from Kyle (2026-08-02): simulate a research team onboarding a new hire, with reverse-direction Q&A — Claude suggests the questions Kyle asks.

## Purpose

Kyle builds a growing lineup of reproduce-and-measure research projects. This skill
runs an **interactive, role-played onboarding session**: Claude plays a senior
member of "the research team," Kyle plays a new hire being brought up to speed so he
can start contributing. The session briefs him in detail on the current project and
(optionally) the whole lineup, with a **Q&A stop after every segment** in which
Claude supplies thought-provoking suggested questions *for Kyle to ask* — inverting
the usual quiz direction and pulling him deeper into his own work.

Success criterion (per interview, evenly weighted): by close-out Kyle has **both**
(a) deep fluency — he could explain the project's purpose, methods, and significance
from scratch, interview-grade — and (b) contribution-readiness — he knows exactly
where the project stands and what to pick up next.

## Relationship to sibling skills (the NOT-fors)

| Skill | It does | `/onboard` differs |
|---|---|---|
| `/reorient` | After-a-gap brief, then routes to the next executor | onboard is a *learning ritual*, role-played, Q&A-driven; it routes nowhere |
| `/project-guide` | Standalone written reference doc with interview lens | onboard is interactive and conversational; its packet records a *session*, not a reference |
| `/wrap` | End-of-session recap + active-recall quiz (Claude asks Kyle) | onboard reverses the quiz direction (Kyle asks Claude) and covers the project, not a session |
| `/begin` / `/catchup` | Session-start delta brief / mid-session audio recap | different jobs entirely |

**Disambiguation risk:** plain "catch me back up to speed" is `/reorient`'s trigger.
The discriminator is the **new-hire / team framing**: "onboard me", "like a new team
member", "pretend I just joined". The frontmatter description must carry this NOT-for
explicitly.

## Triggering

Frontmatter description triggers on: `/onboard`, "onboard me", "new hire mode",
"pretend I just joined the team", "bring me up to speed like a new team member /
new hire", "onboarding session". NOT-fors carried in the description: returning
after a gap with routing wanted (`/reorient`), a standalone written project guide
(`/project-guide`), session recaps (`/wrap`, `/catchup`).

## Input (`$ARGUMENTS`)

- **Nothing** → full agenda; whether to take the lineup tour is asked during the
  welcome (segment 1).
- **`--lineup`** → include the lineup tour without asking.
- **`--skip-lineup`** → skip it without asking.

## Voice & grounding rules (hard rules)

1. **Senior-teammate voice.** A longtime team member on their colleague's first day:
   "we / our lab / the team," warm, direct, genuinely welcoming. Sustained through
   the whole session, including Q&A answers.
2. **The fiction is only the frame.** No invented people, names, org chart, offices,
   or team history. "We" is the voice; everything behind it is real.
3. **Every factual claim traceable** to the repos/docs actually read. Numbers,
   results, and status claims come from the current repo or the portfolio cards —
   never from memory of what a project "probably" does.
4. **Unknowns admitted in character.** "Honestly, we haven't measured that yet" /
   "that's an open question on our board" — never a confident guess. (The team's
   stated values are Kyle's actual Methodology & Honesty Charter; the role-play
   obeys the same honesty rules as the research.)

## The agenda — five segments, a Q&A stop after each

Fixed sequence; each segment = briefing in teammate voice → Q&A session → Kyle
advances with "next" / "move on" / similar.

1. **Welcome & the mission** (short). Who we are, what the team does, the method
   that makes the projects one body of work (pre-registration, judge-free oracles,
   Wilson/Newcombe intervals, hard budget guards), the two lanes. If lineup flag
   absent, close by asking: full lineup tour, or straight to the current project?
2. **The lineup tour** (optional). Lane by lane from the portfolio cards: each
   project's claim-in-one-line, headline result, and status; how the projects chain
   (the J-lens build→map→audit arc; the agent-reliability reproductions); ending
   with where the current project sits in the picture.
3. **The current project, in depth.** The question it asks, its anchor (paper /
   own-result / original), methods and architecture, what's distinctive, and why it
   matters. The "understanding" half.
4. **State of play.** Milestones and gates — decided vs. pending; recent activity
   (git history, wrap logs); open decisions; known gaps. The "current state" half.
5. **Where you come in.** Concrete first contributions pulled from PROJECT.md next
   actions / GAPS / backlog, each with a one-line why-it's-next. Then close-out:
   final Q&A, takeaways, packet finalized.

Scaling: for a sparse or early-stage repo, segments shrink honestly ("M0 is all
that exists so far") rather than pad.

## Q&A mechanics (the heart of the skill)

- **Opening a session:** exactly **3 suggested questions, worded in Kyle's voice**
  (askable verbatim), numbered so he can reply "1"/"2"/"3". Thought-provoking —
  digging into the segment's significance, purpose, and methods, not trivia. For
  the lineup Q&A, questions are **lineup-wide** (cross-project connections, the
  method as a body of work, portfolio positioning) rather than about one project.
- **Every answer ends with 3 fresh suggested questions** until Kyle concludes the
  session ("next", "move on", "that's all").
- **No repeats** across the entire onboarding — neither of questions already
  suggested nor of ones Kyle already asked.
- **Escalation ladder:** early suggestions are orienting/factual; then methods;
  then significance and critique. By segments 4–5 they include reviewer-attack
  questions ("if someone wanted to dismiss this result, where would they push?") —
  deliberately interview-grade.
- **Mix both halves:** suggestions blend fluency questions and state/next-step
  questions, matching the evenly-weighted success criterion.
- **Kyle's own questions always welcome** — the suggestions are seeds, not a menu.
- **Grounded answers, live reads:** if a question needs more than what was
  pre-read, read the repo further *before* answering. Never improvise an answer to
  keep the fiction moving; slowing down to check is in character for this team.

## Sources

**Current project** — the repo the session runs in: README, CLAUDE.md, PROJECT.md /
Wiki, HANDOFF.md, GAPS / backlog docs, wrap logs (`docs/session-logs/` or
equivalent), `git log`. Deeper file reads happen live during Q&A as needed.

**Lineup tour** — `~/Projects/portfolio`: README.md (lanes + tables),
METHODOLOGY.md (the charter), `projects/*.md` (the cards — already distilled and
verified), GAPS-AND-NEXT.md. The cards are the dossier; the eight underlying repos
are **not** read for the tour.

**Degradation rules:**
- Run inside the portfolio repo itself → the portfolio *is* the current project;
  the tour walks its cards; segments 3–4 cover the portfolio artifact.
- Current repo not part of the research lineup (e.g. an app project) → session
  still works; the tour remains available but the "where this project sits"
  positioning is adapted or dropped.
- `~/Projects/portfolio` missing → tour declared unavailable, in character and
  honestly; never faked from memory.

## The onboarding packet

`docs/onboarding/YYYY-MM-DD-onboarding.md` in the current repo, **written
progressively** — each segment appended when it completes, so an interrupted
session still leaves a partial packet (marked as such in its header).

Structure:
1. Header — project, date, lineup tour taken or not, completion status.
2. Per segment: the briefing content as delivered (condensed, not transcript-length).
3. Per segment: the Q&A record — each question actually asked (marked suggested vs.
   Kyle's own) + a condensed answer.
4. Closing takeaways — 3–5, written at close-out.

The Q&A record is what makes this a different artifact from a `/project-guide`
document; the packet is a session record, not a reference doc.

**Landing:** at close-out (or by a later session, if this one died), via the
standard git workflow — short docs branch + PR in the project repo. Docs-only and
non-behavioral, so it qualifies for the adversarial-review escape hatch; the skip
and reason are stated in the merge brief. A project CLAUDE.md's
stricter git rules win where present.

## Out of scope (YAGNI)

- No `--audio` close-out (natural later addition via `narrate`; not now).
- No named fictional roles / multi-character team simulation.
- No cross-session resume beyond the partial packet a broken session leaves.
- No auto-generation of a `/project-guide` doc as a fallback source, and no
  routing to next work (`/reorient`'s job).
- No quizzing Kyle (that's `/wrap`'s recall round; the direction here is reversed).

## Testing note

Per `superpowers:writing-skills`, the highest-risk behaviors are (a) **trigger
disambiguation** — fires on "pretend I just joined the team" without the word
"onboard"; does NOT fire on plain "catch me back up to speed" (that's
`/reorient`); and (b) **Q&A discipline under drift** — the
3-fresh-suggestions-per-answer rule and the no-repeat rule surviving a long
session. A short subagent pressure-test on (a) before merge is recommended but
optional.

## Definition of done (for the skill itself)

`skills/onboard/SKILL.md` exists with house-style frontmatter (name + rich trigger
description carrying the NOT-fors) and a body encoding: the voice-and-grounding
hard rules, the five-segment agenda with Q&A stops, the Q&A mechanics (3 openers /
3 per answer / no repeats / escalation / both halves mixed / live reads), the
source lists with all three degradation rules, the progressive packet spec, and
the out-of-scope list — all consistent with this spec. Same commit: reference-doc
row + usage-playbook card (Run config · Reach for it when · Pairs well with).
Landed via branch + PR + the full adversarial-review loop (skill edits never use
the escape hatch).
