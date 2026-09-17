# A2C learning system — design spec

**Written:** 2026-09-16 · **Status:** approved by Kyle 2026-09-16 (brainstorm → design → this spec); build not started
**Deliverable:** a `/teach` learning workspace for the A2C Auctions business at `~/Learning/a2c-auctions/`, seeded with a mission and internal-source digests; a new global skill `skills/mock-call/` (SKILL.md + PERSONA-FORMAT.md) plus its reference-doc row and usage-playbook card; five persona files in the workspace; one optional brief slot added to the A2C project's `day` skill and a `## Bite` section in its hook. The `teach` and `teach-research` skills are **not edited**.

---

## 1. The problem

Kyle runs the finder side of A2C Auctions (cannabis-equipment consignment auctions, Chicago) and dials receivers, lenders, landlords, and operators every weekday morning. The vocabulary of that world (receivership, CRO, monitor, Article 9, sale-leaseback, reserve, hammer price, settlement) shows up all over the project files, but nothing in the folder explains it, and the "why clients choose A2C" material exists only as pitch copy. The result is a caller who can read a script but can't yet hold a conversation when the other side goes off it.

Kyle's stated purpose, in priority order: **sound credible on calls** (the main focus), find and pitch better on his own, and go deeper into asset disposition and restructuring as a field over the long term. All four conversation types feel shaky today: receivers and trustees, lenders and landlords, operators and their equipment, and A2C's own mechanics after the intro.

## 2. Settled decisions (from the brainstorm)

| Decision | Choice | Why |
|---|---|---|
| Spine | Matt Pocock's `/teach` workspace, stocked by Kyle's `/teach-research` | Kyle asked for it by name; it already owns lessons, quizzes, glossary, and learning records, and the retention model (spacing, retrieval) is the right one |
| Workspace location | `~/Learning/a2c-auctions/` | Matches `gearhead-products` and `party-line`; teach-research's guard refuses a folder with a `CLAUDE.md`, so the A2C project folder is out |
| Delivery, all four picked | Daily bite in the `/day` brief · recall quizzes and a glossary · role-play calls · audio for walks | Time budget is both: 10–15 min on weekday mornings plus one Sunday hour |
| Role-play medium | Voice through voicemode when possible, text otherwise | The real test is verbal; text is the quiet fallback |
| Zack as a source | Specific gaps only | Public sources cover receiverships and auctions; only Zack can answer past consignors and how a sale runs on his side |
| Daily bite placement | The `/day` brief, not the calendar block | Blocks already run near the 7,900-character size where `sync-check` refuses to write; adding text there risks the scripts |
| Audio | Phase 3, after the reference docs exist | `notebook-init` needs sources worth listening to; not part of the first build |
| Persona names | Fictional archetypes, real case facts as scenario only | A drill must never put invented words in a real receiver's mouth |

## 3. Workspace contract

```
~/Learning/a2c-auctions/
  MISSION.md            teach format · written by this build from the brainstorm
  RESOURCES.md          teach format · seeded with internal entries + a ## Gaps section naming the public lanes; /teach-research tops up
  research/             digests (teach-research's RESEARCH-FORMAT) · a2c-internal-* from this build, public ones from /teach-research
  NOTES.md              teach's scratchpad · pre-seeded with Kyle's teaching preferences and pointers to personas/ and recall-log.md
  GLOSSARY.md           teach owns · created by teach, only once Kyle can use a term correctly
  lessons/ reference/ learning-records/ assets/    teach owns · created lazily by teach
  personas/             this design · five files in PERSONA-FORMAT, read by /mock-call
  recall-log.md         this design · append-only, one line per recall event
  zack-questions.md     this design · drafted after the public research shows the gaps
```

Ownership rules: this build writes only MISSION.md, RESOURCES.md, NOTES.md, `research/a2c-internal-*.md`, `personas/`, `recall-log.md`. It never creates `lessons/`, `reference/`, `learning-records/`, `assets/`, or `GLOSSARY.md`; those are teach's to create when it first teaches.

`recall-log.md` line format: `YYYY-MM-DD · <term> · hit|miss · bite|mock-call`. Both the bite and the mock-call debrief append to it. It is retention evidence, not a learning record; a `/teach` session reads it (the NOTES.md pointer says so) and may promote a run of hits into a learning record.

## 4. The mission (draft for MISSION.md)

```md
# Mission: The A2C Auctions business

## Why
Hold a credible conversation with a receiver, a lender or landlord, or an operator about
surplus cannabis equipment without a script, and judge a lead on my own. I'm the finder
for A2C Auctions and the calls are where this gets tested every weekday morning.

## Success looks like
- Define the 30 core terms of this world cold, in one or two sentences each
- Explain in one sentence why a cannabis-specific auction recovers more than a generalist one
- Follow a lender's or landlord's collateral talk without stalling
- Finish five mock calls in a row with no misses in the debrief
- Read a receivership filing or a WARN notice and say what's likely left to sell

## Constraints
- 10 to 15 minutes on weekday mornings before the 8:00 call block; one hour on Sunday
- Lessons must tie to a contact type I actually call: receiver, lender/landlord, operator
- Calls are the test; anything that can't be said out loud on a phone is lower priority
- Sources first; no lesson built on parametric knowledge

## Out of scope
- Appraising equipment values myself (Zack prices; I never quote numbers on a call)
- Cultivation agronomy and anything plant-touching
- Statute-level legal detail; I need the shape of a receivership, not the code sections
- Texas hemp regulation (that lane was retired 9/12)
```

`/teach-research` finds this file present, summarizes it back, and asks for a one-line confirm instead of re-running the interview.

## 5. Sources, three layers

### 5.1 Internal digests (this build)

Seven digests in `research/`, each in teach-research's RESEARCH-FORMAT (`Type: docs`, `URL:` a `file://` path into `~/Desktop/A2CAuctions/`, `Fetched:` the build date), each with a matching `## Knowledge` entry in RESOURCES.md carrying its `Cached:` line:

| Slug | Drawn from | What it holds |
|---|---|---|
| `a2c-internal-pitch-mechanics` | outreach-drafts.md ground rules + templates, CLAUDE.md | The claims A2C makes (no listing fees, seller-set reserves, 15% commission / 85% wired after settlement, no exclusivity except the final 48 hours or once bidding beats reserve, buyers remove, appraisals, monthly national sales); soft pitch vs direct pitch and who gets which; the one-ask rule; the money-direction rule and the 9/11 "not a buyer" lesson |
| `a2c-internal-case-4front` | prospects.md, september-plan.md | A running receivership as a case: the receiver's role, what "still being marketed" means, why a relationship yes isn't a consignment |
| `a2c-internal-case-pharmacann` | prospects.md, outreach-drafts.md, september-plan.md | Five production-site exits, WARN dates, a settled REIT dispute (and the stale claim never to repeat), a retail-only acquisition that left the plant behind, a site with no receiver, buyer, or auctioneer on it |
| `a2c-internal-case-terrascend-gage` | prospects.md, outreach-drafts.md | A court order appointing a receiver over state entities; what a receiver email looks like and why it's the direct pitch |
| `a2c-internal-case-cannabist-and-ayr` | prospects.md, outreach-drafts.md | CRO and Monitor as roles, an RSA and Article 9 restructuring, a strategic buyer taking "certain assets" and leaving the gear, and a competitor auction closing the lane |
| `a2c-internal-distress-signals` | prospects.md sourcing notes | Where leads come from and what each signal means: WARN notices, licence surrenders, registry diffs, court dockets, REIT filings; the T1/T2/T3 tiering logic |
| `a2c-internal-competitors` | prospects.md, outreach-drafts.md | Heritage Global, Joiner Sales Corp, generalist industrial auctioneers, business brokers; what the files say about each and how A2C positions against them |

Digest rules on top of RESEARCH-FORMAT: concepts and case shape, never name lists. No phone numbers, no email addresses. Real people appear only where the fact is public record (a receiver named in a court order); no personal contacts. Where the project files flag a fact as stale or corrected, the digest carries the corrected fact and marks the superseded claim, so a lesson can't resurrect it.

### 5.2 Public lanes (Kyle runs `/teach-research`)

RESOURCES.md ships with a `## Gaps` section naming six lanes, because teach-research's top-up mode hunts exactly what `## Gaps` lists:

1. Why plant-touching cannabis companies can't use federal bankruptcy and land in state-court receiverships and assignments for the benefit of creditors instead; who the receiver, CRO, monitor, trustee, and assignee are
2. The receiver's playbook: appointment order, asset schedule, commercially reasonable disposition, court approval of sales, reporting and appraisal needs
3. UCC Article 9 and secured-lender remedies: liens, foreclosure sales, strict foreclosure; REIT sale-leasebacks and what a landlord owns when the tenant walks
4. Auction mechanics and vocabulary: consignment, reserve vs absolute, hammer price, buyer's premium, settlement, removal; the National Auctioneers Association glossary as the anchor
5. Cannabis equipment classes and what buyers pay for: extraction (CO2, ethanol, hydrocarbon), post-processing, packaging automation, cultivation lighting and HVAC; condition and spec language
6. Distress signals in the industry: WARN notices, licence surrenders, sale-leaseback defaults, restructuring support agreements, going-concern sales vs asset sales

Communities lane (teach's "wisdom"): Turnaround Management Association Chicago chapter, American Bankruptcy Institute, National Auctioneers Association. These double as prospecting rooms; the spec notes it, the workspace doesn't pitch it.

A2C's own site (a2cauctions.com) is pre-seeded as a `## Knowledge` entry so the finders don't have to rediscover it.

### 5.3 Zack, specific gaps only

After the public research lands, `zack-questions.md` is drafted from what's still missing. Candidate list, to be trimmed to 5 to 8:

1. Which consignors has A2C run sales for in the last two years, and which came through a receiver or lender versus an operator directly?
2. From signed consignment to wire, what does a sale look like on your side, and where do deals stall?
3. Who's bidding: how many registered bidders in a typical sale, and what share are operators versus general industrial buyers?
4. Which equipment categories clear at the best recovery, and which don't sell at all?
5. Have you worked inside a receivership or court process before, and what did they need from you (appraisal format, reporting)?
6. Who do you lose deals to, and why?
7. What's the biggest misconception prospects have about A2C?
8. Is there anything I should never say on a call?

Kyle asks Zack (a call or one email; Claude never sends). The answers become `research/zack-answers-<date>.md` with a RESOURCES.md entry.

## 6. The lesson arc (default path, not a rail)

Teach picks what's next from learning records; this is the order it should find sensible, and the order the personas assume. One concept per lesson, 5 to 10 minutes each:

1. **The A2C deal itself.** Consignment, reserve, hammer price, 15/85 after settlement, the 48-hour rule, buyers remove, why a cannabis-specific buyer pool recovers more. First because every call ends here.
2. **Why receivership, not bankruptcy.** Federal illegality closes Chapter 7 and 11; state receiverships, ABCs, and lender-driven Article 9 sales fill the gap. The cast: receiver, CRO, monitor, trustee, assignee.
3. **Anatomy of a receivership.** Appointment, duties, the asset schedule, court approval, "commercially reasonable," why a receiver cares about recovery and reporting.
4. **The money side.** Secured lenders and liens, Article 9 foreclosure, REIT sale-leasebacks, what a landlord owns when gear is left behind, consent orders.
5. **Equipment classes and what buyers actually pay for.** Extraction types, post-processing, packaging, cultivation; what condition and specs matter; what's worth little.
6. **Distress signals as a language.** WARN notices, licence surrenders, RSAs, going-concern sale vs asset sale, a strategic buyer leaving gear behind.
7. **Reading a real case.** 4Front, PharmaCann, TerrAscend from the internal digests: what happened, what's left, who to call.
8. **The competitive landscape.** Heritage Global, Joiner, generalists, brokers; how A2C positions and when to say "we run alongside."

## 7. `/mock-call` (new global skill)

### 7.1 Identity

- `skills/mock-call/SKILL.md` + `skills/mock-call/PERSONA-FORMAT.md`. Typed-only (`disable-model-invocation: true`), same posture as `/teach`.
- Invoked from a teach workspace: `/mock-call [persona-slug] [--voice|--text] [--turns N]`. Default turns: 8 (range 6 to 10).
- Guard: the CWD must hold `MISSION.md` and a `personas/` directory. Otherwise stop, report the resolved directory and what's missing, and suggest the workspace path. Never writes outside the CWD.
- Reference-doc row under Global Skills plus a usage-playbook card, in the same commit as the skill (house rule; `scripts/check-doc-sync.py` enforces it at push).

### 7.2 Flow

1. **Medium.** `--voice` or `--text` if given; otherwise one question. Voice runs each turn through `mcp__plugin_voicemode_voicemode__converse` (persona line as `message`, `wait_for_response: true`, `listen_duration_max: 90`). Text prints the persona line and waits for Kyle's typed reply. Two consecutive voice failures fall back to text, said out loud in one line.
2. **Persona.** The argument names one. With no argument, pick the weakest area: read `learning-records/` and `recall-log.md`, count misses and absent records per persona's "terms this persona tests," choose the persona with the most uncovered ground, and say why in one line before starting.
3. **Ground.** Read the persona file, `GLOSSARY.md` if it exists, `reference/` if it exists, and the internal digests the persona's scenario cites. The persona's vocabulary comes from those files, not from memory.
4. **Turns.** Stay in character for the whole call. Open with the persona's opening line (Kyle has dialed them, or they've picked up a chaser). Use at least two of the persona's curveballs. Never break character to teach mid-call; never invent facts about a real person or firm; scenario facts come only from the digests and are framed as the fictional persona's situation. The call ends when the persona's ask resolves (agrees to the Zack call, agrees to photos, or says no and why) or the turn cap lands.
5. **Debrief**, out of character, in this order: *Handled* (up to three things, each naming the move); *Missed* (each names the term or concept, and links the reference doc or lesson that covers it, or says "not yet taught" if none exists); *Say it differently next time* (one line, the single highest-leverage rewrite). Then the writes:
   - one line per term the persona tested appended to `recall-log.md` (`· hit ·` or `· miss ·`, source `mock-call`);
   - one learning record, only if teach's criteria are met: Kyle demonstrated understanding of something non-trivial, or a misconception was corrected. Coverage alone writes nothing. Numbering follows teach's LEARNING-RECORD-FORMAT (scan for the highest, increment).
6. **Close.** Print the debrief path summary (which files were appended or created) and the run time. Target: 10 minutes end to end.

### 7.3 PERSONA-FORMAT.md

```md
# Persona: {fictional name}, {role}

## Who they are
{2–3 sentences: role, the situation they're in, what's on their desk this week. Fictional person; scenario facts cited from ./research/ digests.}

## What they care about
- {the two or three things that decide whether they keep talking}

## How they talk
{The vocabulary they will actually use, as a short list. Every term here is one the debrief may score.}

## Opening line
{What they say when they pick up or call back.}

## Curveballs
1. {an objection or question that tests a specific term}
2. {…}
3. {…}

## What credible sounds like
{2–3 sentences: the answers that would make this person keep talking. Not a script; a bar.}

## Terms this persona tests
- {term} · {reference doc or lesson slug, or "not yet taught"}
```

### 7.4 The five personas (workspace files)

| File | Archetype | Tests |
|---|---|---|
| `personas/receiver.md` | Court-appointed receiver over a multi-state operator's Michigan entities, four months in, long tail of gear unsold | appointment order, asset schedule, secured-creditor consent, court approval, commercially reasonable, appraisal for the court, buyer's premium and who pays it, "I already have a national auctioneer" |
| `personas/reit-asset-manager.md` | Asset manager at a cannabis REIT holding a recovered building full of tenant gear | sale-leaseback, tenant default, landlord's lien vs abandoned property, fixtures vs equipment, re-lease timeline, removal at buyer's cost |
| `personas/operator-facilities-lead.md` | Facilities head at an MSO consolidating sites; soft-pitch territory | decommissioning, idle lines, C1D1, extraction skid, "we're redeploying it," "corporate approves dispositions," "what's it worth" (never quote) |
| `personas/skeptical-executive.md` | CFO who reads every pitch as a sale; the 9/11 lesson | money direction, "I'm not a buyer," "send me a deck," "how do you get paid," the one ask |
| `personas/zack.md` | Zack asking Kyle to explain the process back to him and to answer "what would you say if a receiver asked…" | the whole chain: consignment agreement, reserve, settlement, wire, intro on email as the attribution record |

Zack is the one persona modeled on a real person, and only in the role of asking questions; the persona never asserts facts about A2C beyond what the digests hold.

## 8. The daily bite

### 8.1 `day` skill (project skill at `~/Desktop/A2CAuctions/.claude/skills/day/`, not in git)

One optional brief item. Phase 1's "post the brief, in this order and nothing more" gains item 7, and the must-do question becomes item 8:

> 7. **Bite** — only when the hook has a `## Bite` section: follow it. One term, one recall question, nothing more.

Phase 2 gains one sentence under Log: a reply to the bite's recall question is confirmed in one line and recorded per the hook; it is never a log line and never touches Todoist. `references/hook-template.md` gains the optional section with a one-line description. The prime directive is untouched: the bite is thirty seconds of the brief.

### 8.2 `## Bite` in `~/Desktop/A2CAuctions/.claude/day.md`

```md
## Bite
workspace: ~/Learning/a2c-auctions/
- Sources, in order: `GLOSSARY.md` terms; then the cheat sheets in `reference/`. If neither exists yet, skip the bite silently.
- Match the contact types on today's list: receiver or fiduciary → receivership and court terms; lender, landlord, banker → collateral terms; operator or corporate → equipment and deal terms; no match → the A2C deal terms.
- Within the match, pick the least-recently-recalled term per `recall-log.md`; never the same term two days running.
- Print: **Bite** · the term · two sentences at most · then `Recall:` one question about the previous bite's term, no options, no hints in the formatting.
- Kyle answers alongside his must-do pick. Confirm in one line (right, or the correct answer in one sentence). Append `YYYY-MM-DD · <term> · hit|miss · bite` to `recall-log.md`. Nothing else changes.
```

## 9. Sundays

One hour: from `~/Learning/a2c-auctions/`, `/teach` for one lesson, then `/mock-call`. A recurring Sunday calendar event ("A2C — Learning hour", 60 minutes) with those two commands in the description is part of the build so the hour exists where Kyle actually reads his day. It is a standing event, not a task, so the Todoist sync rule doesn't apply; Kyle can veto it at build time.

## 10. Audio (phase 3, not in the first build)

Once `reference/` holds four or more cheat sheets: `/notebook-init` with the `learning-topic` template, sources = the reference docs (converted from HTML to text or PDF if NotebookLM rejects HTML) plus the research digests; then `/audio-series` for a building season that follows the lesson arc. `curriculum-sync` can own the notebook→workspace staleness later if the workspace keeps changing; not required.

## 11. Build order and who does what

`/teach` and `/teach-research` are typed-only, so Kyle runs those. Everything else is Claude's.

1. Claude: create the workspace; write MISSION.md, NOTES.md, `recall-log.md` (empty with a header comment), RESOURCES.md (a2cauctions.com entry, the seven internal entries, the `## Gaps` lanes).
2. Claude: write the seven internal digests (fan out to subagents, one or two digests each, each reading only the named project files). Verify teach-research's own contract by hand: every `Cached:` path exists, every digest is linked, counts match.
3. Claude: write `skills/mock-call/` in claude-config, the reference row, the playbook card. Write the five personas in the workspace.
4. Claude: edit the `day` skill (item 7, Phase 2 sentence, hook template) and add `## Bite` to `day.md`.
5. Claude: create the Sunday calendar event (Kyle's veto).
6. Kyle: `cd ~/Learning/a2c-auctions && claude`, then `/teach-research` (top-up; confirm the mission; curate the table). Then `/teach` for lesson one.
7. Claude (next session): draft `zack-questions.md` from RESOURCES.md's remaining `## Gaps`.

## 12. Verification

- **Workspace contract.** `ls` shows exactly the files in §3 that this build owns and none of teach's. Every RESOURCES.md `Cached:` path exists; every file in `research/` is linked; the two counts match.
- **Top-up safety.** Before Kyle's `/teach-research` run, snapshot RESOURCES.md; after, diff: every internal entry survives verbatim, `## Gaps` shrank only where a lane was hunted.
- **mock-call, text.** From the workspace: `/mock-call receiver --text --turns 6` ends with a three-part debrief, one or more `recall-log.md` lines, and a learning record only if the criteria were met (a plain run with no demonstrated skill writes none). From `~/Desktop/A2CAuctions/`: the guard stops with the path and the missing files named.
- **mock-call, voice.** A two-turn voice smoke run completes; unplugging the headset mid-run produces the text fallback line.
- **Bite.** `/day` on a weekday with a receiver on the list shows item 7 with a receivership term; on a day with no matching contact type it shows an A2C deal term; before any reference docs exist it shows nothing and the brief is unchanged. A recall answer appends one line and creates no Todoist change.
- **Doc sync.** `python3 scripts/check-doc-sync.py` passes in claude-config with the mock-call row and card.
- **Nothing sent, nothing dialed.** No Gmail, Todoist, or calendar-block writes anywhere in the build except the optional Sunday event.

## 13. Edge cases

- Voicemode services down: mock-call says so once and runs in text.
- `GLOSSARY.md` absent for weeks (teach adds terms only once understood): the bite and the debrief draw from `reference/` until then. If `reference/` is also empty, the bite skips silently (the brief is unchanged) and mock-call says "nothing to test yet, run /teach" and stops before picking a persona.
- Persona argument doesn't match a file: list the available slugs and stop.
- `learning-records/` or `recall-log.md` absent when choosing a persona: treat as zero coverage everywhere, which makes the choice a tie; break ties in the order the personas are listed in §7.4 (receiver first).
- `recall-log.md` missing: recreate it with the header line; it's append-only data, not state anyone else owns.
- Project files change (they do, daily): the internal digests are point-in-time and dated in `Fetched:`; a lesson cites the digest, not the live file. A re-digest is a manual top-up, not automatic.
- The bite's contact-type match depends on task names in Todoist; a task with no recognizable type falls through to the A2C deal terms rather than guessing.

## 14. Landing it

- claude-config branch `feat/a2c-learning-system` carries this spec, `skills/mock-call/`, the reference row, and the playbook card. PR to `main` per the git workflow; `skills/**` is a behavioral file, so the review-gate proposal applies (single round is the likely recommendation: one new skill, no existing behavior changed, no data or auth surface).
- The workspace (`~/Learning/a2c-auctions/`) and the A2C-folder edits (`day` skill, `day.md`) are not under version control. The `day` edit is small and reversible; the previous text is quoted in the plan so it can be restored by hand.

## 15. Out of scope

- Editing `teach` or `teach-research` in any way.
- NotebookLM, audio, or `curriculum-sync` in the first build (§10 is phase 3).
- Rewording any script, template, or calendar block; the bite never touches the block.
- A generic "learning" framework in the `day` skill beyond the one optional hook-driven slot.
- Teaching Kyle to appraise equipment or quote numbers; Zack prices.
- Prospecting through the communities listed in §5.2; the workspace is for learning.

---

**Run-config note (for the build session, once the implementation plan exists):** Opus 5 · `high`. The judgment calls are made here; what's left is a well-specified build with several independent pieces (seven digests to fan out, one skill, five personas, two small edits), and `high` covers the digest-writing judgment about what's stale. Launch from the A2C folder so its `CLAUDE.md` (name spellings, voice rules, the no-stale-claims warnings) loads, and give the other two locations by absolute path:

```
cd ~/Desktop/A2CAuctions && claude --model claude-opus-5 --effort high
```
