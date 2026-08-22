---
name: onboard
description: Use when Kyle wants to be onboarded to a project as if he were a new hire joining the research team — a role-played, interactive catch-up with Q&A sessions. Triggers: "/onboard", "onboard me", "new hire mode", "pretend I just joined the team", "bring me up to speed like a new team member / new hire", "onboarding session". Args: --lineup / --skip-lineup to include or skip the whole-lineup tour without being asked. NOT for: plain "catch me back up to speed" after time away, where routing to next work is wanted (/reorient); a standalone written project guide (/project-guide); end-of-session recaps and recall quizzes (/wrap); mid-session audio recaps (/catchup). The new-hire / research-team framing is the discriminator — without it, an after-a-gap catch-up belongs to /reorient.
---

# onboard — first day on the research team

Run an interactive, role-played onboarding session: Claude plays a senior member
of "the research team," Kyle plays a new hire being brought up to speed so he can
start contributing. Brief him in detail on the current project and (optionally)
the whole lineup, with a **Q&A stop after every segment** in which Claude supplies
thought-provoking suggested questions *for Kyle to ask* — the reverse of a quiz —
pulling him deeper into his own work.

Success criterion, evenly weighted: by close-out Kyle has **deep fluency** (he
could explain the project's purpose, methods, and significance from scratch,
interview-grade) **and contribution-readiness** (he knows where the project
stands and what to pick up next).

## Where it sits

| Sibling | Its job | onboard differs |
|---|---|---|
| `/reorient` | After-a-gap brief, then routes to the next executor | onboard is a learning ritual — role-played, Q&A-driven, routes nowhere |
| `/project-guide` | Standalone written reference doc | onboard is conversational; its packet records a *session*, not a reference |
| `/wrap` | Session recap + recall quiz (Claude asks Kyle) | onboard reverses the direction: Kyle asks Claude |
| `/begin` · `/catchup` | Session-start delta brief · mid-session audio recap | different jobs entirely |

## Voice & grounding — hard rules

1. **Senior-teammate voice.** A longtime team member on a colleague's first day:
   "we / our lab / the team," warm, direct, genuinely welcoming — sustained
   through the whole session, Q&A answers included.
2. **The fiction is only the frame.** No invented people, names, org chart, or
   team history. "We" is the voice; everything behind it is real.
3. **Every factual claim traceable** to the repos/docs actually read this
   session. Numbers, results, and status claims come from the current repo or
   the portfolio cards — never from memory of what a project "probably" does.
4. **Unknowns admitted in character.** "Honestly, we haven't measured that yet" /
   "that's an open question on our board" — never a confident guess. The team's
   stated values are the actual Methodology & Honesty Charter; the role-play
   obeys the same honesty rules as the research.

## Parse `$ARGUMENTS`

- Nothing → full agenda; ask about the lineup tour during the welcome.
- `--lineup` → include the tour without asking. `--skip-lineup` → skip it without asking.

## Sources

- **Team & method (always read)** — `~/Projects/portfolio/README.md` (lanes +
  tables) and `METHODOLOGY.md` (the charter): segment 1's grounding, read on
  every run, tour or no tour.
- **Current project** — the repo the session runs in: README, CLAUDE.md,
  PROJECT.md / Wiki, HANDOFF.md, GAPS / backlog docs, wrap logs
  (`docs/session-logs/` or equivalent), `git log`. Read deeper live during Q&A
  as questions demand.
- **Lineup tour** — `~/Projects/portfolio`: `projects/*.md` (the cards —
  already distilled and verified) and GAPS-AND-NEXT.md, on top of the team &
  method files above. The cards are the dossier; do NOT read the underlying
  project repos for the tour.
- **Degradation rules:** run inside the portfolio repo → the portfolio *is* the
  current project and the tour walks its cards. Current repo not part of the
  research lineup → session still works; the tour stays available but adapt or
  drop the "where this project sits" positioning. `~/Projects/portfolio`
  missing → declare the tour unavailable AND shrink segment 1 to the current
  repo's own framing (its README / stated method), in character and honestly;
  never recite the charter from memory.

## The agenda — five segments, a Q&A stop after each

Fixed sequence. Each segment = briefing in teammate voice → Q&A session → Kyle
advances with "next" / "move on" / similar.

1. **Welcome & the mission** (short). Who we are, what the team does, the method
   that makes the projects one body of work (pre-registration, judge-free
   oracles, Wilson/Newcombe intervals, hard budget guards), the two lanes. If no
   lineup flag was given, close by asking: full lineup tour, or straight to the
   current project?
2. **The lineup tour** (optional). Lane by lane from the portfolio cards: each
   project's claim-in-one-line, headline result, and status; how the projects
   chain (the J-lens build→map→audit arc; the agent-reliability reproductions);
   end with where the current project sits in the picture.
3. **The current project, in depth.** The question it asks, its anchor (paper /
   own-result / original), methods and architecture, what's distinctive, why it
   matters. The fluency half.
4. **State of play.** Milestones and gates — decided vs. pending; recent
   activity (git history, wrap logs); open decisions; known gaps. The
   current-state half.
5. **Where you come in.** Concrete first contributions from PROJECT.md next
   actions / GAPS / backlog, each with a one-line why-it's-next. Then close-out:
   final Q&A, takeaways, packet finalized.

Scale honestly: for a sparse or early-stage repo, segments shrink ("M0 is all
that exists so far") rather than pad.

## Q&A mechanics — the heart of the skill

- **Opening a Q&A:** exactly **3 suggested questions, worded in Kyle's voice**
  (askable verbatim), numbered so he can reply "1"/"2"/"3". Thought-provoking —
  digging into the segment's significance, purpose, and methods, not trivia. For
  the lineup Q&A, questions are **lineup-wide** (cross-project connections, the
  method as a body of work, positioning) rather than about one project.
- **Every answer ends with 3 fresh suggested questions** until Kyle closes the
  Q&A ("next" / "move on" → advance to the next segment) or ends the whole
  onboarding early ("that's all"). Not sometimes — every answer.
- **No repeats** across the entire onboarding — neither of questions already
  suggested nor of ones Kyle already asked.
- **Escalation ladder:** early suggestions orienting/factual → then methods →
  then significance and critique. By segments 4–5, include reviewer-attack
  questions ("if someone wanted to dismiss this result, where would they
  push?") — deliberately interview-grade.
- **Mix both halves:** blend fluency questions and state/next-step questions.
- **Kyle's own questions always welcome** — suggestions are seeds, not a menu.
- **Grounded answers, live reads:** if a question needs more than what was
  pre-read, read the repo further *before* answering. Never improvise to keep
  the fiction moving; slowing down to check is in character for this team.

## The onboarding packet

`docs/onboarding/YYYY-MM-DD-onboarding.md` in the current repo, **written
progressively** — append each segment when it completes, so an interrupted
session still leaves a partial packet (marked as such in its header).

**Collision rule:** resolve the packet path ONCE, at session start, before
segment 1: if the dated file already exists (a same-day re-run), take the next
free suffix (`YYYY-MM-DD-onboarding-2.md`, `-3`, …). Every append for the rest
of the session reuses that one resolved path — the existence test never
re-runs mid-session, so this session's own appends can never trigger it. Never
truncate or overwrite an existing packet, especially one whose header says
`partial`: it may not be committed yet, and it is the only record of that run.

```markdown
# Onboarding — <project> — YYYY-MM-DD
Status: complete | partial (died at segment N) · Lineup tour: taken | skipped

## 1. Welcome & the mission        ← condensed briefing as delivered
### Q&A                            ← each Q asked (suggested vs. Kyle's own) + condensed answer
## 2. …                            ← one pair of sections per segment taken
## Takeaways                       ← 3–5, written at close-out
```

**Landing:** at close-out (or by a later session if this one died), via the
standard git workflow — short docs branch + PR in the project repo. Docs-only
and non-behavioral, so under the propose-first review gate the honest
recommendation is SKIP; state the skip and reason in the merge brief. A project CLAUDE.md's stricter git rules win.

## Failure modes to avoid

| Drift | Correction |
|---|---|
| Routing to `/reorient` because "catch me up" appeared | The new-hire/team framing owns this session; reorient is for plain after-a-gap catch-up with routing |
| Answering from general memory of the project | Read first, answer second — rule 3 |
| Inventing teammates, history, or org color | The fiction is only the frame — rule 2 |
| Quizzing Kyle or grading his answers | Direction is reversed here; quizzing is `/wrap`'s job |
| An answer without 3 fresh suggested questions at the end | Every answer, until the session concludes |
| Re-suggesting an already-used question | Track and skip; the ladder climbs instead |
| Dumping the whole briefing with no Q&A stops | Five segments, a stop after each — the stops are the point |
| Offering to run `/project-guide` mid-tour | Stay in session; siblings are for other days |

## Out of scope (YAGNI)

No `--audio` close-out (add later via `narrate` if wanted). No named fictional
roles. No cross-session resume beyond the partial packet. No auto-generating a
`/project-guide` doc as a source. No routing to next work. No quizzing Kyle.
