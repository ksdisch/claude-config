# A2C Learning System Implementation Plan

> **For the orchestrator session:** this plan is executed by a Fable 5 session that coordinates, not builds. Phase B runs through `/orchestrate a2c-learning-system --seats 3` (worker sessions, one per ticket, in worktrees of the learning workspace). Phase A runs as one background `Agent` subagent in claude-config. Phase C runs as one small `Agent` subagent plus the orchestrator's own git and calendar calls. The `superpowers:subagent-driven-development` and `executing-plans` skills are **not** used; Kyle chose `/orchestrate` for this build. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a `/teach` learning workspace for the A2C Auctions business at `~/Learning/a2c-auctions/`, seeded with a mission, seven internal-source digests, and five call personas; ship a global `mock-call` drill skill in claude-config; and add a one-line daily bite to the A2C `/day` brief.

**Architecture:** Three locations. The workspace (`~/Learning/a2c-auctions/`) becomes a local git repo with no remote so `/orchestrate` can cut worktrees in it; its scaffolding and seed files are materialized verbatim from this plan before orchestration, and the judgment-bearing content (digests, personas) is built by worker sessions from tickets. The `mock-call` skill lands in `~/Projects/claude-config` on the existing branch `feat/a2c-learning-system` via a subagent and a reviewed PR. The A2C folder (`~/Desktop/A2CAuctions/`, not under git) gets three small verbatim edits at the end.

**Tech Stack:** Markdown workspaces (Matt Pocock `teach` format, Kyle's `teach-research` RESEARCH-FORMAT), bash contract check, `/orchestrate` + `/launch` worker sessions, voicemode `converse` for the drill, Google Calendar MCP for one recurring event.

**Spec:** `docs/superpowers/specs/2026-09-16-a2c-learning-system-design.md` (same branch). Where this plan and the spec differ on a detail (persona file prefixes, `/day` item numbers, the workspace being a git repo), the spec was amended in the same commit as this plan and they agree.

---

## File structure

**`~/Learning/a2c-auctions/` (new local git repo, branch `main`, feature branch `feat/a2c-learning-system`)**

| Path | Owner | Written by |
|---|---|---|
| `.gitignore` | this build | Phase 0 (orchestrator, verbatim) |
| `Makefile` | this build | Phase 0 (verbatim) |
| `scripts/check-workspace.sh` | this build | Phase 0 (verbatim) |
| `MISSION.md` | teach format | Phase 0 (verbatim from spec §4) |
| `NOTES.md` | teach's scratchpad | Phase 0 (verbatim) |
| `recall-log.md` | this build | Phase 0 (verbatim) |
| `RESOURCES.md` | teach format | Phase 0 (verbatim); `/teach-research` tops up later |
| `.scratch/a2c-learning-system/issues/01..04-*.md`, `tickets.md` | orchestrate's tracker | Phase 0 (verbatim) |
| `research/a2c-internal-pitch-mechanics.md`, `-distress-signals.md`, `-competitors.md` | RESEARCH-FORMAT | ticket 01 |
| `research/a2c-internal-case-4front.md`, `-case-terrascend-gage.md` | RESEARCH-FORMAT | ticket 02 |
| `research/a2c-internal-case-pharmacann.md`, `-case-cannabist-and-ayr.md` | RESEARCH-FORMAT | ticket 03 |
| `personas/01-receiver.md` … `05-zack.md` | PERSONA-FORMAT | ticket 04 |
| `lessons/ reference/ learning-records/ assets/ GLOSSARY.md` | teach | **never created by this build** |

**`~/Projects/claude-config/` (branch `feat/a2c-learning-system`, already holds the spec and this plan)**

| Path | Written by |
|---|---|
| `skills/mock-call/SKILL.md` | Phase A subagent |
| `skills/mock-call/PERSONA-FORMAT.md` | Phase A subagent |
| `docs/command-skill-reference.md` (one row, Personal Coaching table) | Phase A subagent |
| `docs/usage-playbook.md` (one card after `teach-research`) | Phase A subagent |

**`~/Desktop/A2CAuctions/` (not under git)**

| Path | Written by |
|---|---|
| `.claude/skills/day/SKILL.md` (two insertions) | Phase C subagent |
| `.claude/skills/day/references/hook-template.md` (one insertion) | Phase C subagent |
| `.claude/day.md` (one new section) | Phase C subagent |

---

## Phase 0: the orchestrator materializes the workspace (no judgment, verbatim)

Everything in this phase is copied from this plan. Run from `~/Learning/a2c-auctions/` (the session's launch directory). The shell's working directory resets between Bash calls in this harness, so every command below uses absolute paths or a leading `cd`.

### Task 0.1: Create the repo and scaffolding

**Files:** create `.gitignore`, `Makefile`, `scripts/check-workspace.sh`

- [ ] **Step 1: Confirm the directory is empty or absent, then init**

Run:
```bash
cd ~/Learning/a2c-auctions && ls -A
```
Expected: nothing (or only files this plan wrote in an earlier attempt). Anything else → stop and ask Kyle.

```bash
cd ~/Learning/a2c-auctions && git init -q -b main && git status --short | wc -l
```
Expected: `0`.

- [ ] **Step 2: Write `.gitignore`**

```bash
cd ~/Learning/a2c-auctions && cat > .gitignore <<'EOF'
.claude/worktrees/
.DS_Store
EOF
```

- [ ] **Step 3: Write `Makefile` (recipe lines need a literal tab, so use printf)**

```bash
cd ~/Learning/a2c-auctions && printf 'test:\n\tbash scripts/check-workspace.sh\n\nstrict:\n\tbash scripts/check-workspace.sh --strict\n' > Makefile && cat -A Makefile | head -2
```
Expected second line: `^Ibash scripts/check-workspace.sh$` (the `^I` is the tab).

- [ ] **Step 4: Write `scripts/check-workspace.sh`**

```bash
cd ~/Learning/a2c-auctions && mkdir -p scripts && cat > scripts/check-workspace.sh <<'EOF'
#!/usr/bin/env bash
# check-workspace.sh: contract check for this teach workspace.
# Usage: bash scripts/check-workspace.sh [--strict]
# Default: structural checks on what exists; a Cached: path not written yet is a note.
# --strict: every Cached: path in RESOURCES.md must exist (run after all digests land).
set -u
cd "$(dirname "$0")/.." || exit 2
strict=0; [ "${1:-}" = "--strict" ] && strict=1
fail=0; pending=0
bad()  { echo "FAIL: $*"; fail=1; }

for f in MISSION.md RESOURCES.md NOTES.md recall-log.md; do
  [ -f "$f" ] || bad "$f missing"
done
if [ -f MISSION.md ]; then
  for h in "## Why" "## Success looks like" "## Constraints" "## Out of scope"; do
    grep -qF "$h" MISSION.md || bad "MISSION.md lacks '$h'"
  done
fi
if [ -f RESOURCES.md ]; then
  for h in "## Knowledge" "## Wisdom (Communities)" "## Gaps"; do
    grep -qF "$h" RESOURCES.md || bad "RESOURCES.md lacks '$h'"
  done
  tmp=$(mktemp)
  grep -o 'Cached: \./research/[^ ]*\.md' RESOURCES.md | sed 's/^Cached: //' | sort -u | while read -r p; do
    if [ ! -f "$p" ]; then
      if [ "$strict" = 1 ]; then echo "FAIL: cached digest missing: $p"; else echo "note: not written yet: $p"; fi
    fi
  done > "$tmp"
  cat "$tmp"
  grep -q '^FAIL' "$tmp" && fail=1
  pending=$(grep -c '^note' "$tmp")
  rm -f "$tmp"
fi
for f in research/*.md; do
  [ -e "$f" ] || continue
  grep -qF "Cached: ./$f" RESOURCES.md 2>/dev/null || bad "orphan digest (no RESOURCES.md entry): $f"
  for k in "URL" "Type" "Author/steward" "Fetched" "Covers"; do
    grep -qF "**$k:**" "$f" || bad "$f lacks header field $k"
  done
done
if ls research/*.md >/dev/null 2>&1; then
  grep -nE '[0-9]{3}[-. )]{1,2}[0-9]{3}[-. ][0-9]{4}' research/*.md && bad "phone number in research/"
  grep -nE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' research/*.md && bad "email address in research/"
fi
if [ -d personas ]; then
  for f in personas/*.md; do
    [ -e "$f" ] || continue
    for h in "## Who they are" "## What they care about" "## How they talk" "## Opening line" "## Curveballs" "## What credible sounds like" "## Terms this persona tests"; do
      grep -qF "$h" "$f" || bad "$f lacks '$h'"
    done
  done
fi
X="--exclude-dir=.git --exclude-dir=.scratch --exclude-dir=.claude"
grep -rnw $X --include='*.md' 'Zach' . | grep -v 'zachary@' && bad "'Zach' found; the name is Zack (only the email keeps zachary@)"
grep -rniwE $X --include='*.md' 'Daryll|Daryl' . && bad "Darryl misspelled (two R's, one L)"
if [ "$fail" = 0 ]; then echo "OK (digests not yet written: $pending)"; exit 0; else echo "FAILED"; exit 1; fi
EOF
chmod +x scripts/check-workspace.sh
```

- [ ] **Step 5: Run the check before the seed files exist**

Run: `cd ~/Learning/a2c-auctions && make test; echo "exit=$?"`
Expected: four `FAIL: … missing` lines, then `FAILED`, `exit=1`. (The check works; the files come next.)

### Task 0.2: Write the four seed files

**Files:** create `MISSION.md`, `NOTES.md`, `recall-log.md`, `RESOURCES.md`

- [ ] **Step 1: `MISSION.md`**

```bash
cd ~/Learning/a2c-auctions && cat > MISSION.md <<'EOF'
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
EOF
```

- [ ] **Step 2: `NOTES.md`**

```bash
cd ~/Learning/a2c-auctions && cat > NOTES.md <<'EOF'
# Notes

Working notes and Kyle's teaching preferences for this workspace. Read before designing a lesson.

## How Kyle wants to be taught
- Short lessons, 5 to 10 minutes, one concept each. Every lesson names the contact type it serves: receiver, lender/landlord, or operator.
- Quizzes are the point, not decoration. Same-length answers, no formatting hints, and a "say it out loud" prompt where the concept is something he'd have to voice on a call.
- Plain language over polished. No em dashes in lesson prose; short sentences mixed with a longer one.
- Never quote a number for what equipment is worth. Zack prices. Lessons teach the shape of value (what clears, what doesn't), not figures.
- Kyle has not opted out of communities; the wisdom lane is open.

## Files this workspace adds beyond teach's own
- `personas/` — five call personas in the mock-call skill's PERSONA-FORMAT. `/mock-call` reads them; `/teach` may cite them when a lesson maps to a persona's "Terms this persona tests" list.
- `recall-log.md` — one line per recall event (`YYYY-MM-DD · <term> · hit|miss · bite|mock-call`), written by the A2C `/day` bite and by `/mock-call`. It is retention evidence, not a learning record. Read it before choosing the next lesson; a run of hits on a term is grounds to promote it into a learning record and, once Kyle can define it cold, into `GLOSSARY.md`.
- `zack-questions.md` — drafted after `/teach-research` shows what public sources can't answer (past consignors, how a sale runs on Zack's side). Kyle asks Zack; the answers become `research/zack-answers-<date>.md`.
- `research/a2c-internal-*.md` — digests of Kyle's own A2C project files (cases, pitch mechanics, competitors, distress signals). Point-in-time: the `Fetched` date says when the files were read.

## Spelling and naming rules (from the A2C project)
- Zack Stern, with a k. The email address is the one exception and keeps its own spelling. Never "Zach".
- Darryl Jacobs: two R's, one L. Verified against a contact card 9/11. A name is verified against an artifact, never a recollection.
- Real people appear in this workspace only where the fact is public record (a receiver named in a court order). Personas are fictional; Zack's persona only asks questions.
EOF
```

- [ ] **Step 3: `recall-log.md`**

```bash
cd ~/Learning/a2c-auctions && cat > recall-log.md <<'EOF'
# Recall log

One line per recall event, append-only: `YYYY-MM-DD · <term> · hit|miss · bite|mock-call`.
Written by the A2C `/day` bite and by `/mock-call`. Read by `/teach` (see NOTES.md). Never edited by hand.

EOF
```

- [ ] **Step 4: `RESOURCES.md`**

```bash
cd ~/Learning/a2c-auctions && cat > RESOURCES.md <<'EOF'
# The A2C Auctions business: Resources

Entries marked "Cached:" have local digests in ./research/ — read the digest before searching the web.

## Knowledge

- [Docs: A2C Auctions site](https://www.a2cauctions.com/)
  A2C's own description of the consignment process, the sale calendar, and "sign up to bid". Use for: what A2C promises a consignor, in A2C's words.
- [Docs: A2C pitch mechanics (internal digest of outreach-drafts.md + CLAUDE.md)](file:///Users/kyledisch/Desktop/A2CAuctions/outreach-drafts.md)
  The claims A2C makes to a consignor, soft pitch vs direct pitch, the one-ask rule, the money-direction rule. Use for: lesson 1, the A2C deal itself.
  Cached: ./research/a2c-internal-pitch-mechanics.md
- [Docs: Distress signals and lead sourcing (internal digest of prospects.md)](file:///Users/kyledisch/Desktop/A2CAuctions/prospects.md)
  Where leads come from and what each signal means: WARN notices, licence surrenders, registry diffs, court dockets, REIT filings; the tiering logic. Use for: lesson 6, distress signals as a language.
  Cached: ./research/a2c-internal-distress-signals.md
- [Docs: Competitors (internal digest of prospects.md)](file:///Users/kyledisch/Desktop/A2CAuctions/prospects.md)
  Heritage Global, Joiner Sales Corp, the generalist industrial auctioneers, brokers; how A2C positions. Use for: lesson 8, the competitive landscape.
  Cached: ./research/a2c-internal-competitors.md
- [Docs: Case: the 4Front receivership (internal digest)](file:///Users/kyledisch/Desktop/A2CAuctions/prospects.md)
  A running multi-state receivership as a case: the receiver's role, what "still being marketed" means, why a relationship yes isn't a consignment. Use for: lessons 3 and 7.
  Cached: ./research/a2c-internal-case-4front.md
- [Docs: Case: the TerrAscend / Gage Michigan receivership (internal digest)](file:///Users/kyledisch/Desktop/A2CAuctions/prospects.md)
  A court order appointing a receiver over state entities; what the direct pitch to a receiver looks like. Use for: lessons 2, 3 and 7.
  Cached: ./research/a2c-internal-case-terrascend-gage.md
- [Docs: Case: PharmaCann's site exits (internal digest)](file:///Users/kyledisch/Desktop/A2CAuctions/prospects.md)
  Five production-site exits, WARN dates, a settled REIT dispute and the stale claim never to repeat, a retail-only acquisition that left the plant behind. Use for: lessons 4, 6 and 7.
  Cached: ./research/a2c-internal-case-pharmacann.md
- [Docs: Case: Cannabist and Ayr, CRO, Monitor, RSA, and a competitor's auction (internal digest)](file:///Users/kyledisch/Desktop/A2CAuctions/prospects.md)
  CRO and Monitor as roles, an RSA and Article 9 restructuring, a strategic buyer taking certain assets and leaving the gear, licence surrenders as separate events from sales. Use for: lessons 2, 4, 6 and 8.
  Cached: ./research/a2c-internal-case-cannabist-and-ayr.md

## Wisdom (Communities)

(none yet; `/teach-research` proposes candidates. No opt-out recorded.)

## Gaps

- Why plant-touching cannabis companies can't use federal bankruptcy and land in state-court receiverships and assignments for the benefit of creditors instead; who the receiver, CRO, monitor, trustee, and assignee are. No public primary source held yet.
- The receiver's playbook: appointment order, asset schedule, commercially reasonable disposition, court approval of sales, reporting and appraisal needs. No public source held yet.
- UCC Article 9 and secured-lender remedies: liens, foreclosure sales, strict foreclosure; REIT sale-leasebacks and what a landlord owns when the tenant walks. No public source held yet.
- Auction mechanics and vocabulary: consignment, reserve vs absolute, hammer price, buyer's premium, settlement, removal. The National Auctioneers Association glossary is the anchor to find. No public source held yet.
- Cannabis equipment classes and what buyers pay for: extraction (CO2, ethanol, hydrocarbon), post-processing, packaging automation, cultivation lighting and HVAC; condition and spec language. No public source held yet.
- Distress signals in the industry: WARN notices, licence surrenders, sale-leaseback defaults, restructuring support agreements, going-concern sales vs asset sales. Only the internal digest covers this; a public treatment is missing.
- Communities: Turnaround Management Association Chicago chapter, American Bankruptcy Institute, National Auctioneers Association. None verified yet.
- A2C's past consignors and how a sale runs on Zack's side: not answerable from public sources; goes to `zack-questions.md`.
EOF
```

- [ ] **Step 5: Verify the a2cauctions.com URL resolves; if not, move that entry under Gaps**

Run: `curl -sI -o /dev/null -w '%{http_code}\n' https://www.a2cauctions.com/`
Expected: `200` (or a 3xx). Any other code → edit RESOURCES.md: delete the site entry from Knowledge and add a Gaps line `A2C's site did not resolve on <date> (HTTP <code>); re-check.`

- [ ] **Step 6: Run the check**

Run: `cd ~/Learning/a2c-auctions && make test; echo "exit=$?"`
Expected: seven `note: not written yet: ./research/…` lines, then `OK (digests not yet written: 7)`, `exit=0`.

### Task 0.3: Write the tickets and commit

**Files:** create `.scratch/a2c-learning-system/issues/01-digests-pitch-and-signals.md`, `02-digests-receivership-cases.md`, `03-digests-restructuring-cases.md`, `04-personas.md`, `.scratch/a2c-learning-system/tickets.md`

Every ticket carries the same **Constraints** block. It is repeated in full in each file on purpose: workers read their own ticket and nothing else.

- [ ] **Step 1: Ticket 01**

```bash
cd ~/Learning/a2c-auctions && mkdir -p .scratch/a2c-learning-system/issues && cat > .scratch/a2c-learning-system/issues/01-digests-pitch-and-signals.md <<'EOF'
# 01: Internal digests: pitch mechanics, distress signals, competitors

**What to build:** Three research digests that let a `/teach` lesson cite what A2C promises a consignor, how leads are found and what each distress signal means, and who A2C competes with, without re-reading Kyle's 270 KB prospect file.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

## What to build

Create exactly these three files, each in teach-research's RESEARCH-FORMAT (read `~/.claude/skills/teach-research/RESEARCH-FORMAT.md` first; the template and rules there are the contract):

1. `research/a2c-internal-pitch-mechanics.md`
2. `research/a2c-internal-distress-signals.md`
3. `research/a2c-internal-competitors.md`

`RESOURCES.md` already carries the entry and `Cached:` line for each; do not edit `RESOURCES.md`. If a `Cached:` path there does not match one of the three names above, send a Blocked message.

## Sources (read-only, by heading)

All under `/Users/kyledisch/Desktop/A2CAuctions/`. These files are large; locate headings with `grep -n '^## \|^### ' <file>` and read ranges with `sed -n 'A,Bp'`. Never read a whole file, never modify anything in that folder.

- **pitch-mechanics:** `outreach-drafts.md`: the notes above the first `##` heading (proof point and phone-close changes), `## Ground rules (from Zack + his seller template)`, `## Reusable templates` (Templates A through E). `CLAUDE.md`: `## Drafting emails/messages for Kyle` and `### Voice: write like a person, not an AI` (the pitch rules and the money-direction rule; skip the contact details and the sign-off entirely). `september-plan.md`: `## Cadence rules` and `## Decisions from the interview (9/6)`.
- **distress-signals:** `prospects.md`: the intro above the first `##` heading ("How to use this list", the tier definitions), `## 📌 Campaign status & scouting update` including `### Earlier rebriefs` (how each lead was found and verified), `## Tier 3 — Multipliers` (its intro and the kinds of people it lists, not their contact details), `## Hunting grounds — renewable lead sources`, `## Working notes`. `september-plan.md`: `## What the 9/6 verification changed`, `## Replenish results (9/6, after the gate)`, `## Replenish results (9/12, after the gate)`.
- **competitors:** `prospects.md`: every "Competitor watch" and "Competitor note" bullet (grep `-n -i 'competitor'`), the Ayr entries (`### T1-5`, `### T2-20`, and the Ayr bullet under `### Checked / ruled out`), `### T1-6. The Cannabist Company` (the Heritage Global sale and the third Denver site), and the 9/6 and 9/12 replenish paragraphs naming Joiner Sales Corp. `outreach-drafts.md`: `## Ground rules` (A2C's stated edge).

## Digest contents

Each digest keeps the RESEARCH-FORMAT header block (`URL` is `file:///Users/kyledisch/Desktop/A2CAuctions/<primary file>.md`, `Type` is `docs`, `Fetched` is today's date, `Covers` names the mission line it serves) and the `## Structure`, `## Key concepts`, `## Notable quotes` sections. Add one section the format does not have: `## Retired claims (never repeat)`, listing every claim the source files mark stale, superseded, corrected, or wrong, each with the corrected version beside it. A lesson that resurrects a retired claim is the failure this section prevents.

- **pitch-mechanics** captures: the claims A2C makes to a consignor and where each comes from (listing fees, who sets reserves and how A2C suggests them, commission and the share wired after settlement, the exclusivity rule and its two exceptions, who handles removal and shipping, appraisals, sale cadence); the soft pitch versus the direct pitch and which contact types get which, with the reasoning the files give; the one-ask rule for a first touch and what the ask is for each contact type after the 9/7 change; the money-direction rule and the 9/11 lesson behind it; the proof point as of the files (what to point people to, and what not to cite); the intro-on-email attribution rule; what happens the moment a lead bites (Template E's shape, not its text); why the files say cannabis-specific buyers recover more than a generalist auction.
- **distress-signals** captures: the T1/T2/T3 tier logic in the file's own terms; each lead source the files actually used and what a hit means (WARN notices and the difference between notice date and effective date; state licence surrenders, expirations, suspensions and revocations; the Texas registry diff and why that lane was retired 9/12; court dockets and receivership orders; SEC filings such as a 10-Q calling a building dark; press; competitor-auction archives as a negative check); the verification rules the files learned the hard way (a shared switchboard is not a shared company; a name is verified against an artifact; a dead sale link; the Cannabist third-site correction); what a "multiplier" is and the kinds of people who control equipment dispositions repeatedly (receivers, CROs, lenders, REIT landlords, brokers, restructuring advisors), described as roles.
- **competitors** captures: each competitor the files name and what the files say about them (Heritage Global Partners as the incumbent on distressed cannabis gear and the sales it ran that closed lanes; Joiner Sales Corp; Maynards and Solid Assets Solutions; Paul E. Saperstein and the domain warning; Thomas Hirchak; Rabin Worldwide; Schneider Industries; PPL Group; Rick Levin and why he is never pitched; the generalists named around the Texas lane); how the files check whether a competitor already sold the gear (the archive checks and their stated bounds); A2C's edge in the files' own words; the "we run alongside" posture.

## Constraints (apply to every file you write)

- Concept-level, for a learner. No Todoist ids, draft numbers, block numbers, calendar dates for calls, or task language. Case shape and mechanics, not name lists.
- No phone numbers, no email addresses, no personal contact details of any kind. `make test` fails on a phone or email pattern in `research/`.
- Do not name any referral source, personal contact, or friend of Kyle's. Real people appear only where the fact is public record (a receiver named in a court order, an executive named in a press release). Facility addresses only where the case turns on them.
- Where a source marks a claim STALE, SUPERSEDED, CORRECTED, WRONG, or "never say", carry the corrected fact in the body and list the retired claim under `## Retired claims (never repeat)`.
- Spelling: Zack Stern (the email address is the only place "Zach" survives, and it never appears in a digest). Darryl Jacobs is not mentioned at all.
- Digest, not dump: compressed concepts and short attributed quotes with their heading as the location. 80 to 200 lines per file.
- Read the A2C folder read-only. Write only the files this ticket names, in your worktree. Do not touch `RESOURCES.md`, `MISSION.md`, `NOTES.md`, or anything under `.scratch/`.
- Leave no untracked files in the worktree. Commit with a message starting `research:`.

## Acceptance criteria

- [ ] The three files exist at the exact paths above, each with the five header fields, the three format sections, and `## Retired claims (never repeat)`.
- [ ] `make test` passes from the worktree root and prints `OK (digests not yet written: 4)`.
- [ ] Every `## Retired claims` entry pairs the retired claim with its corrected version.
- [ ] No line in the three files contains a phone number, an email address, a Todoist id, or a draft/block number.
- [ ] Each `Notable quotes` entry names the source file and heading it came from.

## Comments
EOF
```

- [ ] **Step 2: Ticket 02**

```bash
cd ~/Learning/a2c-auctions && cat > .scratch/a2c-learning-system/issues/02-digests-receivership-cases.md <<'EOF'
# 02: Internal digests: the 4Front and TerrAscend/Gage receivership cases

**What to build:** Two case-study digests of running court receiverships, written so a lesson on "anatomy of a receivership" can walk a learner through a real one and a mock-call persona can borrow its shape.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

## What to build

Create exactly these two files, each in teach-research's RESEARCH-FORMAT (read `~/.claude/skills/teach-research/RESEARCH-FORMAT.md` first; the template and rules there are the contract):

1. `research/a2c-internal-case-4front.md`
2. `research/a2c-internal-case-terrascend-gage.md`

`RESOURCES.md` already carries the entry and `Cached:` line for each; do not edit `RESOURCES.md`. If a `Cached:` path there does not match one of the two names above, send a Blocked message.

## Sources (read-only, by heading)

All under `/Users/kyledisch/Desktop/A2CAuctions/`. These files are large; locate headings with `grep -n '^## \|^### ' <file>` and read ranges with `sed -n 'A,Bp'`. Never read a whole file, never modify anything in that folder.

- **case-4front:** `prospects.md`: `### T1-3. 4Front Ventures receivership`, and the paragraph in `## 📌 Campaign status & scouting update` that begins "⏰ Two live clocks found" (the same receiver's separate PharmaCann Maryland sale process: a going-concern process with equipment in scope). `outreach-drafts.md`: `### 2. Jacques Santucci, 4Front receiver + multiplier`. `september-plan.md`: the 4Front line under `## What the 9/6 verification changed` and the 4Front row in `## The roster`.
- **case-terrascend-gage:** `prospects.md`: `### T1-1. TerrAscend (Gage Cannabis) Michigan receivership`. `outreach-drafts.md`: `### 1. Charles Bullock, TerrAscend/Gage Michigan receiver`, `### 43. John W. Polderman, Stevenson & Bullock` (the receiver's firm as a multiplier; describe the role, not the contact). `september-plan.md`: the TerrAscend row in `## The roster`.

## Digest contents

Each digest keeps the RESEARCH-FORMAT header block (`URL` is `file:///Users/kyledisch/Desktop/A2CAuctions/prospects.md`, `Type` is `docs`, `Fetched` is today's date, `Covers` names the mission line it serves) and the `## Structure`, `## Key concepts`, `## Notable quotes` sections. Add one section the format does not have: `## Retired claims (never repeat)`, listing every claim the source files mark stale, superseded, corrected, or wrong, each with the corrected version beside it.

Write each case as a timeline a learner can retell: what the company was, what went wrong, who was appointed and by what kind of order, what the receiver has been doing with the assets, what the files say is still unsold or unknown, how A2C approached it (direct pitch, what was asked for), and what came back. Then a short "what this case teaches" list: the receiver's incentives (recovery, court reporting, a defensible process), why a relationship yes is not a consignment, why a receiver who runs many cannabis estates is a multiplier, what "the long tail usually does" means, and what a going-concern sale process is versus an equipment disposition.

- **case-4front** also captures: that the same receiver runs a separate estate with an explicit equipment line and a going-concern bid deadline, and what that says about how receivers sequence a sale (going concern first, tail after).
- **case-terrascend-gage** also captures: what an order appointing a receiver over a company's state entities does and doesn't cover, why the files call this contact "photo-capable", and what the receiver's own firm being a repeat appointee means.

## Constraints (apply to every file you write)

- Concept-level, for a learner. No Todoist ids, draft numbers, block numbers, calendar dates for calls, or task language. Case shape and mechanics, not name lists.
- No phone numbers, no email addresses, no personal contact details of any kind. `make test` fails on a phone or email pattern in `research/`.
- Do not name any referral source, personal contact, or friend of Kyle's. Real people appear only where the fact is public record (a receiver named in a court order, an executive named in a press release). Facility addresses only where the case turns on them.
- Where a source marks a claim STALE, SUPERSEDED, CORRECTED, WRONG, or "never say", carry the corrected fact in the body and list the retired claim under `## Retired claims (never repeat)`.
- Spelling: Zack Stern (the email address is the only place "Zach" survives, and it never appears in a digest). Darryl Jacobs is not mentioned at all.
- Digest, not dump: compressed concepts and short attributed quotes with their heading as the location. 80 to 200 lines per file.
- Read the A2C folder read-only. Write only the files this ticket names, in your worktree. Do not touch `RESOURCES.md`, `MISSION.md`, `NOTES.md`, or anything under `.scratch/`.
- Leave no untracked files in the worktree. Commit with a message starting `research:`.

## Acceptance criteria

- [ ] The two files exist at the exact paths above, each with the five header fields, the three format sections, and `## Retired claims (never repeat)`.
- [ ] `make test` passes from the worktree root and prints `OK (digests not yet written: 5)`.
- [ ] Each case reads as a dated timeline followed by a "what this case teaches" list.
- [ ] No line in the two files contains a phone number, an email address, a Todoist id, or a draft/block number.
- [ ] Each `Notable quotes` entry names the source file and heading it came from.

## Comments
EOF
```

- [ ] **Step 3: Ticket 03**

```bash
cd ~/Learning/a2c-auctions && cat > .scratch/a2c-learning-system/issues/03-digests-restructuring-cases.md <<'EOF'
# 03: Internal digests: the PharmaCann and Cannabist/Ayr cases

**What to build:** Two case-study digests of operators winding down outside a single court receivership: one through site exits under a REIT landlord and a partial acquisition, one through a CRO, a Monitor, a restructuring agreement, and a competitor's auction. A lesson on the money side and one on distress signals both draw on these.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

## What to build

Create exactly these two files, each in teach-research's RESEARCH-FORMAT (read `~/.claude/skills/teach-research/RESEARCH-FORMAT.md` first; the template and rules there are the contract):

1. `research/a2c-internal-case-pharmacann.md`
2. `research/a2c-internal-case-cannabist-and-ayr.md`

`RESOURCES.md` already carries the entry and `Cached:` line for each; do not edit `RESOURCES.md`. If a `Cached:` path there does not match one of the two names above, send a Blocked message.

## Sources (read-only, by heading)

All under `/Users/kyledisch/Desktop/A2CAuctions/`. These files are large; locate headings with `grep -n '^## \|^### ' <file>` and read ranges with `sed -n 'A,Bp'`. Never read a whole file, never modify anything in that folder.

- **case-pharmacann:** `prospects.md`: `### T1-2. PharmaCann` (long; read all of it, it carries its own corrections). `outreach-drafts.md`: `### 3. PharmaCann, Chicago HQ` including the "SUPERSEDED 9/12" paragraph, and `### 7. IIP, landlord with repossessed facilities` (the REIT side). `september-plan.md`: the PharmaCann line under `## What the 9/6 verification changed`.
- **case-cannabist-and-ayr:** `prospects.md`: `### T1-6. The Cannabist Company`, `### T1-5. Ayr Wellness`, `### T2-20. Ayr Wellness / Sira Naturals`, the Ayr and Cannabist bullets under `### Checked / ruled out`, and the 9/5–9/6 rebrief paragraph in `## 📌 Campaign status & scouting update` that begins "Fact check killed the Cannabist play". `outreach-drafts.md`: `### 5. Ayr Wellness, wind-down`, `### 9. The Cannabist Company, Denver manufacturing wind-down`, `### 35. Curt Kroll, SierraConstellation Partners`.

## Digest contents

Each digest keeps the RESEARCH-FORMAT header block (`URL` is `file:///Users/kyledisch/Desktop/A2CAuctions/prospects.md`, `Type` is `docs`, `Fetched` is today's date, `Covers` names the mission line it serves) and the `## Structure`, `## Key concepts`, `## Notable quotes` sections. Add one section the format does not have: `## Retired claims (never repeat)`, listing every claim the source files mark stale, superseded, corrected, or wrong, each with the corrected version beside it. These two cases carry more corrections than any other part of the files; this section is the most important thing in the digest.

Write each case as a timeline a learner can retell, then a "what this case teaches" list.

- **case-pharmacann** captures: the production-site exits with their WARN notice dates versus effective dates and the difference between the two; what a REIT landlord (sale-leaseback) is in this story, what the dispute with the landlord was, and that it was settled (the retired claim about "a year in default, repossessing sites" goes under Retired claims with the corrected fact); what a retail-only acquisition by a competitor means for the plant that did not go with it; what it means that one site has no landlord, no buyer, no receiver, and no auctioneer on it; how the reachability problem was solved in principle (a warm introduction replacing a cold lane; do not name the introducer); and the lesson that the file's own earlier list double-counted one site and missed another.
- **case-cannabist-and-ayr** captures: the roles of a Chief Restructuring Officer and a court-appointed Monitor and which firms held them here; what a restructuring support agreement and an Article 9 process mean in the Ayr story; a strategic buyer taking "certain assets" and what that leaves behind; a competitor auction closing a lane (which sites it covered) and the 9/9 correction that a third site's gear was not in it; licence surrenders as an event separate from any sale, and why that reopened a lead the files had ruled out twice; the "liquidator check" as a method and its stated bounds.

## Constraints (apply to every file you write)

- Concept-level, for a learner. No Todoist ids, draft numbers, block numbers, calendar dates for calls, or task language. Case shape and mechanics, not name lists.
- No phone numbers, no email addresses, no personal contact details of any kind. `make test` fails on a phone or email pattern in `research/`.
- Do not name any referral source, personal contact, or friend of Kyle's. Real people appear only where the fact is public record (a receiver named in a court order, an executive named in a press release). Facility addresses only where the case turns on them (the third Denver site is such a case).
- Where a source marks a claim STALE, SUPERSEDED, CORRECTED, WRONG, or "never say", carry the corrected fact in the body and list the retired claim under `## Retired claims (never repeat)`.
- Spelling: Zack Stern (the email address is the only place "Zach" survives, and it never appears in a digest). Darryl Jacobs is not mentioned at all.
- Digest, not dump: compressed concepts and short attributed quotes with their heading as the location. 80 to 200 lines per file.
- Read the A2C folder read-only. Write only the files this ticket names, in your worktree. Do not touch `RESOURCES.md`, `MISSION.md`, `NOTES.md`, or anything under `.scratch/`.
- Leave no untracked files in the worktree. Commit with a message starting `research:`.

## Acceptance criteria

- [ ] The two files exist at the exact paths above, each with the five header fields, the three format sections, and `## Retired claims (never repeat)`.
- [ ] `make test` passes from the worktree root and prints `OK (digests not yet written: 5)`.
- [ ] The PharmaCann digest's Retired claims section includes the landlord-default claim with its corrected fact, and the digest names no introducer.
- [ ] The Cannabist/Ayr digest states which sites the competitor's auction covered and which Denver site it did not.
- [ ] No line in the two files contains a phone number, an email address, a Todoist id, or a draft/block number.

## Comments
EOF
```

- [ ] **Step 4: Ticket 04**

```bash
cd ~/Learning/a2c-auctions && cat > .scratch/a2c-learning-system/issues/04-personas.md <<'EOF'
# 04: Five call personas for /mock-call

**What to build:** Five persona files that let `/mock-call` play the other end of the phone: a receiver, a REIT asset manager, an operator's facilities lead, a skeptical executive, and Zack asking Kyle to explain the process back. Each persona talks in its world's vocabulary, carries three curveballs, and names the terms it tests.

**Blocked by:** 01 (pitch, signals, competitors digests), 02 (receivership cases), 03 (restructuring cases)

**Status:** ready-for-agent

## What to build

Create exactly these five files:

1. `personas/01-receiver.md`
2. `personas/02-reit-asset-manager.md`
3. `personas/03-operator-facilities-lead.md`
4. `personas/04-skeptical-executive.md`
5. `personas/05-zack.md`

Each file follows this format exactly (it is the `mock-call` skill's PERSONA-FORMAT; the section headings are checked by `make test`):

```md
# Persona: {fictional name}, {role}

## Who they are
{2–3 sentences: role, the situation they're in, what's on their desk this week. Fictional person; scenario facts cited from ./research/ digests by file name.}

## What they care about
- {the two or three things that decide whether they keep talking}

## How they talk
{The vocabulary they will actually use, as a short list. Every term here is one the debrief may score.}

## Opening line
{What they say when they pick up or call back. Say which: Kyle dialed them, or they are returning his voicemail.}

## Curveballs
1. {an objection or question that tests a specific term}
2. {…}
3. {…}

## What credible sounds like
{2–3 sentences: the answers that would make this person keep talking. Not a script; a bar.}

## Terms this persona tests
- {term} · not yet taught
```

Every persona in this ticket writes `not yet taught` after each term, because no lessons exist yet; `/teach` sessions update those pointers later.

## Ground each persona in the digests

Read all seven `research/a2c-internal-*.md` files first. Scenario facts come from them and from nowhere else; cite the digest by file name inside "Who they are". Names are fictional. Situations echo the cases (a multi-state operator's Michigan entities under a receiver; a REIT holding a recovered building; an MSO consolidating sites) without being those companies.

| File | Archetype | Tests, at minimum |
|---|---|---|
| `01-receiver.md` | Court-appointed receiver over a multi-state operator's Michigan entities, four months in, long tail of gear unsold; Kyle dialed them | appointment order, asset schedule, secured-creditor consent, court approval of a sale, commercially reasonable, appraisal for the court, buyer's premium and who pays it. Curveballs must include "the secured lender has a lien on all of it, why would I talk to you", "I already have a national auctioneer on the estate", "what's your buyer's premium and who pays it" |
| `02-reit-asset-manager.md` | Asset manager at a cannabis REIT holding a recovered building full of a former tenant's gear; returning Kyle's voicemail | sale-leaseback, tenant default, landlord's lien versus abandoned property, fixtures versus equipment, re-lease timeline, removal at the buyer's cost. Curveballs must include "is the equipment even ours to sell", "we need the building empty in thirty days", "our lawyers say the fixtures stay" |
| `03-operator-facilities-lead.md` | Facilities head at a multi-state operator consolidating sites; soft-pitch territory; Kyle dialed them | decommissioning, idle lines, C1D1, extraction skid, redeploying to another site, corporate approval of dispositions. Curveballs must include "we're moving it to our other facility", "corporate has to approve any disposition", "what's it worth" (the credible answer never quotes a number) |
| `04-skeptical-executive.md` | CFO who reads every pitch as a sale; the 9/11 lesson from the pitch-mechanics digest; returning Kyle's email with a call | money direction, the one ask, how A2C gets paid, consignment versus purchase. Curveballs must include "I'm not a buyer", "send me a deck", "how do you get paid" |
| `05-zack.md` | Zack Stern asking Kyle to explain the process back to him, then "what would you say if a receiver asked…"; only asks, never asserts a fact about A2C beyond the digests; Kyle dialed him | the whole chain: consignment agreement, reserve, hammer price, settlement, the wire, no exclusivity and its exceptions, the intro on email as the attribution record |

## Constraints (apply to every file you write)

- Fictional names for personas 01 through 04. Persona 05 is Zack, and its only moves are questions.
- No phone numbers, no email addresses, no personal contact details, no real receiver's or executive's name as the persona.
- Never quote a number for equipment value anywhere in a persona file, including in "What credible sounds like".
- Spelling: Zack Stern. Darryl Jacobs is not mentioned at all.
- Read the A2C folder only if a digest is unclear, and read-only; the digests are the intended source. Write only the five files this ticket names, in your worktree. Do not touch `RESOURCES.md`, `research/`, `NOTES.md`, or anything under `.scratch/`.
- Leave no untracked files in the worktree. Commit with a message starting `personas:`.

## Acceptance criteria

- [ ] The five files exist at the exact paths above, each with all seven section headings from the format.
- [ ] `make test` passes from the worktree root and prints `OK (digests not yet written: 0)`.
- [ ] Each persona's Curveballs include the three named in the table, in the persona's own words.
- [ ] Each "Who they are" cites at least one `research/a2c-internal-*.md` file by name.
- [ ] Every "Terms this persona tests" entry ends with `· not yet taught`.
- [ ] `05-zack.md` contains no statement of fact about A2C; every line Zack speaks is a question or an acknowledgement.

## Comments
EOF
```

- [ ] **Step 5: `tickets.md`**

```bash
cd ~/Learning/a2c-auctions && cat > .scratch/a2c-learning-system/tickets.md <<'EOF'
# Tickets: a2c-learning-system

Generated index — resolves to the issue files below. Source of truth is `issues/`; refresh on publish, on a /triage Status change, or once after each merge in /orchestrate.

| # | Title | Summary | Status | Blocked by |
|---|---|---|---|---|
| [01](issues/01-digests-pitch-and-signals.md) | Internal digests: pitch mechanics, distress signals, competitors | Three research digests: what A2C promises, how leads are found, who A2C competes with | ready-for-agent | None |
| [02](issues/02-digests-receivership-cases.md) | Internal digests: the 4Front and TerrAscend/Gage receivership cases | Two case-study digests of running court receiverships | ready-for-agent | None |
| [03](issues/03-digests-restructuring-cases.md) | Internal digests: the PharmaCann and Cannabist/Ayr cases | Two case-study digests: REIT landlord and partial acquisition; CRO, Monitor, RSA, competitor auction | ready-for-agent | None |
| [04](issues/04-personas.md) | Five call personas for /mock-call | Receiver, REIT asset manager, operator facilities lead, skeptical executive, Zack | ready-for-agent | 01, 02, 03 |
EOF
```

- [ ] **Step 6: Commit the workspace on `main`**

```bash
cd ~/Learning/a2c-auctions && git add -A && git commit -q -m "workspace: scaffolding, seed files, and tickets for the A2C learning system

Materialized verbatim from ~/Projects/claude-config/docs/superpowers/plans/2026-09-16-a2c-learning-system.md.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git log --oneline && make test
```
Expected: one commit; `OK (digests not yet written: 7)`.

---

## Phase A: the `mock-call` skill in claude-config (one background subagent)

### Task A.1: Dispatch the build

**Files (in `~/Projects/claude-config`, branch `feat/a2c-learning-system`):** create `skills/mock-call/SKILL.md`, `skills/mock-call/PERSONA-FORMAT.md`; modify `docs/command-skill-reference.md` (Personal Coaching table), `docs/usage-playbook.md` (card after `teach-research`)

- [ ] **Step 1: Confirm the branch is where the subagent will write**

Run: `git -C ~/Projects/claude-config status --short --branch | head -3`
Expected: `## feat/a2c-learning-system...origin/feat/a2c-learning-system` and a clean tree. Any other branch → `git -C ~/Projects/claude-config checkout feat/a2c-learning-system` first; a dirty tree → stop and ask Kyle.

- [ ] **Step 2: Dispatch one `general-purpose` subagent, model `opus`, in the background, with this brief verbatim**

````text
Build the `mock-call` skill in ~/Projects/claude-config on the branch feat/a2c-learning-system (already checked out; do not create or switch branches). Commit when done; do not push. Use absolute paths in every command (the shell cwd resets between calls).

Write these four things, then run `python3 ~/Projects/claude-config/scripts/check-doc-sync.py` from the repo root and make it pass.

### 1. ~/Projects/claude-config/skills/mock-call/SKILL.md (exact content)

---
name: mock-call
description: Use when Kyle wants to drill a live call against a persona from a teach workspace — "/mock-call", "/mock-call receiver", "run a practice call", "drill me on a lender call". Runs from the workspace (needs MISSION.md and personas/): picks a persona, plays it for 6 to 10 turns by voice (voicemode) or text, then debriefs out of character — handled, missed with each miss named to a term and the doc that covers it, one rewrite — and writes recall-log lines plus a learning record only when teach's criteria are met. Typed-only. NOT for teaching a concept (teach), stocking sources (teach-research), or briefing a real dial (the A2C folder's call-brief).
disable-model-invocation: true
argument-hint: "[persona-slug] [--voice|--text] [--turns N]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, ToolSearch, mcp__plugin_voicemode_voicemode__converse
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
5. `recall-log.md` and `learning-records/` if they exist, for the choice below and the debrief.

## Choosing a persona (no slug given)

For each persona, take its "Terms this persona tests" list and count the **uncovered** terms:
a term with no `hit` line in `recall-log.md`, or whose most recent line is a `miss`. Pick the
persona with the most uncovered terms; ties go to the lowest file prefix (`01-` before `02-`).
Absent files count as zero coverage everywhere. Say the pick and the count in one line before
the call starts.

## The call

**Voice.** Load the tool once: `ToolSearch` with `select:mcp__plugin_voicemode_voicemode__converse`.
Each persona line is one call: `message` is the line, `wait_for_response: true`,
`listen_duration_max: 90`. The transcript that comes back is Kyle's turn. A tool error or an
empty transcript twice in a row → say "Switching to text" once and continue in text from the
next turn; the turn count carries on.

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

### 2. ~/Projects/claude-config/skills/mock-call/PERSONA-FORMAT.md (exact content)

# Persona format

Persona files live in a teach workspace at `personas/<NN>-<slug>.md`. The two-digit prefix
orders them; `/mock-call <slug>` matches the part after the prefix. Every section below is
required; the workspace's contract check greps for the headings.

```md
# Persona: {fictional name}, {role}

## Who they are
{2–3 sentences: role, the situation they're in, what's on their desk this week. Fictional person; scenario facts cited from ./research/ digests by file name.}

## What they care about
- {the two or three things that decide whether they keep talking}

## How they talk
{The vocabulary they will actually use, as a short list. Every term here is one the debrief may score.}

## Opening line
{What they say when they pick up or call back. Say which: Kyle dialed them, or they are returning his voicemail.}

## Curveballs
1. {an objection or question that tests a specific term}
2. {…}
3. {…}

## What credible sounds like
{2–3 sentences: the answers that would make this person keep talking. Not a script; a bar.}

## Terms this persona tests
- {term} · {reference/<file>.html | lessons/<file>.html | not yet taught}
```

Rules:
- Fictional names, always. A persona modeled on a real person may only ask questions; it never asserts a fact about a real firm.
- No contact details of any kind.
- "Terms this persona tests" is what the debrief scores and what persona selection counts. Keep it to the terms the persona would actually make Kyle use.
- Update the pointer after `· ` when a lesson or reference doc covers the term; until then it reads `not yet taught`.

### 3. One row in ~/Projects/claude-config/docs/command-skill-reference.md

Under `### Personal Coaching`, add this row directly after the `teach-research` row (exact text, one line):

| [`mock-call`](../skills/mock-call/SKILL.md) | Drill a live call against a persona from a `teach` workspace — voice through voicemode or text, 6 to 10 turns in character, then an out-of-character debrief (handled, missed with the term named, one rewrite) that writes recall-log lines and, only when earned, a learning record. Typed-only (`/mock-call`); run from the learning directory. · [config →](usage-playbook.md#mock-call) |

### 4. One card in ~/Projects/claude-config/docs/usage-playbook.md

Insert directly after the `#### \`teach-research\`` card (before `#### \`match-the-mock\``), matching the surrounding cards' style exactly:

#### `mock-call`

- **Run config:** Opus 5 · `medium` — the persona has to stay in character and the debrief
  has to map each miss to the right term, which is judgment; voice turns want low latency,
  which argues against `high`.
- **Reach for it when:**
  - A teach workspace has personas and you want to test whether the vocabulary survives a
    live conversation, not a quiz.
  - Sunday learning hour, after the `/teach` lesson.
  - Before a real call of a type you have not made in a while.
- **Pairs well with:** [`teach`](#teach) (builds the reference docs the persona draws on and
  promotes terms to the glossary), [`teach-research`](#teach-research) (stocks the digests
  the personas cite).
- **Notes:** typed-only (`disable-model-invocation: true`). Voice needs the voicemode
  plugin's services running (`/voicemode:status`); two failed turns fall back to text
  automatically. Writes only `recall-log.md` and, when earned, one learning record; never
  the glossary.

### Then

Run `cd ~/Projects/claude-config && python3 scripts/check-doc-sync.py` and paste its output in your report. Fix anything it flags in the row or card (never in the checker). Commit once:

git -C ~/Projects/claude-config add skills/mock-call docs/command-skill-reference.md docs/usage-playbook.md
git -C ~/Projects/claude-config commit -m "feat(mock-call): add the mock-call drill skill, reference row, and playbook card

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"

Report back: the commit SHA, `git -C ~/Projects/claude-config show --stat HEAD`, and the doc-sync output. Do not push. Do not touch any other file. If anything in this brief contradicts what you find in the repo (a row already present, a heading that doesn't exist), stop and report instead of improvising.
````

- [ ] **Step 3: Note the dispatch in one line to Kyle** ("mock-call skill build dispatched to a background subagent on claude-config feat/a2c-learning-system"), then proceed to Phase B without waiting.

### Task A.2: Land the skill (on the subagent's completion notice, whenever it arrives)

- [ ] **Step 1: Verify the commit**

Run: `git -C ~/Projects/claude-config log --oneline -3 && git -C ~/Projects/claude-config show --stat HEAD | tail -8 && cd ~/Projects/claude-config && python3 scripts/check-doc-sync.py`
Expected: a `feat(mock-call)` commit touching exactly four files; doc-sync passes. Anything else → send the subagent a follow-up via `SendMessage` naming what is off, or re-dispatch with the same brief.

- [ ] **Step 2: Push and open the PR**

```bash
git -C ~/Projects/claude-config push origin feat/a2c-learning-system
cd ~/Projects/claude-config && gh pr create --base main --head feat/a2c-learning-system --title "feat(mock-call): drill skill + A2C learning system spec and plan" --body "$(cat <<'EOF'
Adds the `mock-call` skill (SKILL.md + PERSONA-FORMAT.md) with its reference row and playbook card, plus the approved design spec and implementation plan for the A2C learning system.

The learning workspace itself (`~/Learning/a2c-auctions/`) is a separate local repo built by `/orchestrate`; nothing from it lands here.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_019Vvvp4r1jp7kE6zrPfZLiN
EOF
)"
```

- [ ] **Step 3: Review-gate proposal, then STOP for Kyle**

Print: *Review gate for the mock-call PR: `skills/**` is a behavioral file. Preflight: `scripts/check-doc-sync.py` clean (cited above); no other gate in this repo sees a skill diff. Recommendation: **single round**, reviewer focus on (a) whether the persona-selection rule and the recall-log write rule can be followed literally, (b) any step where the skill could write outside the workspace, (c) the voice fallback. Skip / single / full?* Then end the turn.

- [ ] **Step 4: After Kyle's call**

Single or full → `cd ~/Projects/claude-config` and invoke the `adversarial-review` skill on branch `feat/a2c-learning-system` against `main` at the chosen scope; fix blocking findings via a follow-up to the same subagent (or a fresh one with the finding text), re-verify, comment the summary on the PR. Clean → `gh pr merge <n> --merge --delete-branch`, then `git -C ~/Projects/claude-config checkout main && git -C ~/Projects/claude-config pull -q`. Brief Kyle in one line: PR number, merge SHA. Skip → merge directly, same brief.

---

## Phase B: `/orchestrate` the workspace tickets

### Task B.1: Start orchestration

- [ ] **Step 1: Load the cross-session tools and learn your name**

`ToolSearch` with `select:ListAgents,SendMessage`, then `ListAgents`; the first line names this session. Workers reply to that name.

- [ ] **Step 2: Invoke**

```
/orchestrate a2c-learning-system --seats 3
```

Facts the skill cannot infer, to hold in mind while it runs:
- Milestone 2 (auto-launched seats via `/launch`) was verified live in the 2026-09-07 pilot (`~/Projects/claude-config/docs/reports/2026-09-07-orchestrate-pilot.md`); treat M2 as live unless Kyle says otherwise. Workers launch as `claude --model claude-opus-5 --effort high` per the skill.
- The repo has **no remote**, so workers commit to their branch and send `Done: ticket <NN> — branch <name>`; you merge with `git merge --no-ff` into `feat/a2c-learning-system`.
- The test command is `make test` (Makefile detected in Setup step 4). Workers run it from their worktree root.
- Frontier on the first pass is three tickets (01, 02, 03), one per seat. Ticket 04 waits for all three. That width is real: the three digest tickets write disjoint files and never touch `RESOURCES.md`, so they cannot conflict. Do not manufacture a fourth seat for 04; do not serialize 01–03.
- Workers read `~/Desktop/A2CAuctions/` read-only. If a worker reports anything written there, stop and tell Kyle.

### Task B.2: Review gates per ticket (propose, then STOP for Kyle; he did not delegate)

Kyle's words in the planning session: *"deploy review agents if appropriate / necessary"*. That is a request to propose, not a delegation. At each Done, verify per the skill, then print the proposal and end the turn.

| Ticket | Recommendation | Reviewer focus |
|---|---|---|
| 01 digests: pitch, signals, competitors | single round | Every claim traceable to the named source headings; every stale/superseded claim in the sources appears under Retired claims; no contact details; no name of a referral source |
| 02 digests: receivership cases | single round | Same, plus: the timeline dates match the sources; nothing asserted about a named receiver beyond what the files say is public record |
| 03 digests: restructuring cases | single round | Same, plus: the landlord-default claim is retired with the corrected fact; the competitor auction's site list and the third Denver site match the 9/9 correction |
| 04 personas | single round | No real person as a fictional persona; Zack persona only asks; no equipment values; each persona's curveballs test the terms it lists |

Run each review from the ticket worktree with base `feat/a2c-learning-system`, as the skill says. Critical and should-fix findings block the merge until fixed and self-verified, closed or downgraded by the judge, or waived by Kyle by name; nice-to-haves go in the ticket's `## Comments`.

### Task B.3: After the fourth merge

- [ ] **Step 1: Strict contract check on the feature branch**

Run: `cd ~/Learning/a2c-auctions && git branch --show-current && make strict`
Expected: `feat/a2c-learning-system`, then `OK (digests not yet written: 0)`. A FAIL here is a real defect; send a Follow-up to the ticket's worker (the worktree still exists until `git worktree remove` ran; if it is gone, dispatch a fresh worker for a one-line fix ticket, or ask Kyle).

- [ ] **Step 2: Land the feature branch on `main`**

```bash
cd ~/Learning/a2c-auctions && git checkout main && git merge --no-ff feat/a2c-learning-system -m "Merge feat/a2c-learning-system: digests and personas" && make strict && git log --oneline | head -12 && git worktree list
```
Expected: strict OK; `git worktree list` shows only the main checkout.

- [ ] **Step 3: Confirm the build wrote nothing teach owns**

Run: `cd ~/Learning/a2c-auctions && ls -d lessons reference learning-records assets GLOSSARY.md 2>&1 | grep -c 'No such file'`
Expected: `5`.

---

## Phase C: the A2C folder edits and the Sunday hour

### Task C.1: Edit the `day` skill, its hook template, and `day.md` (one `general-purpose` subagent, model `sonnet`)

**Files:** modify `~/Desktop/A2CAuctions/.claude/skills/day/SKILL.md`, `~/Desktop/A2CAuctions/.claude/skills/day/references/hook-template.md`, `~/Desktop/A2CAuctions/.claude/day.md`

- [ ] **Step 1: Dispatch with this brief verbatim**

````text
Four exact edits across three files in ~/Desktop/A2CAuctions (not a git repo; use absolute paths). Each is an insertion or a replacement of text quoted below. If any quoted "old" text is not found exactly once, stop and report; do not improvise.

Edit 1: ~/Desktop/A2CAuctions/.claude/skills/day/SKILL.md, Phase 1 brief list.
Old (two consecutive lines):
5. **Parking lot** — the prior day's unworked items, one line each.
6. One question: **which one to three of these make today a win?**
New:
5. **Parking lot** — the prior day's unworked items, one line each.
6. **Bite** — only when the hook has a `## Bite` section: follow it. One term, one recall
   question, nothing more. No section → no line.
7. One question: **which one to three of these make today a win?**

Edit 2: same file, end of the Phase 2 "Log" subsection.
Old (two consecutive lines):
Questions get answers, not log lines. **Done when:** every outcome in the message has a
log line and an applied action, or a question back.
New (the old two lines, then a blank line, then):
A reply to the bite's recall question is confirmed in one line and recorded exactly as the
hook's `## Bite` section says. It is never a log line and never touches Todoist.

Edit 3: ~/Desktop/A2CAuctions/.claude/skills/day/references/hook-template.md, inside the fenced template.
Old (two consecutive lines):
## Extra morning sources
- <source, what to read, what counts as an overnight item>
New:
## Extra morning sources
- <source, what to read, what counts as an overnight item>

## Bite
workspace: <absolute path to a teach learning workspace>
- <how to pick today's term, what to print, and where to record the recall answer>

Also in hook-template.md, after the closing fence of the template block, append this paragraph:
`## Bite` adds one term-of-the-day line to the brief (Phase 1, item 6); leave it out for projects with no learning workspace.

Edit 4: ~/Desktop/A2CAuctions/.claude/day.md. Insert a new section directly before the line `## Outcome vocabulary (Kyle says → what to do)`:

## Bite
workspace: ~/Learning/a2c-auctions/
- Sources, in order: `GLOSSARY.md` terms; then the cheat sheets in `reference/`. If neither exists yet, skip the bite silently.
- Match the contact types on today's list: receiver or fiduciary → receivership and court terms; lender, landlord, banker → collateral terms; operator or corporate → equipment and deal terms; no match → the A2C deal terms.
- Within the match, pick the least-recently-recalled term per `recall-log.md`; never the same term two days running.
- Print: **Bite** · the term · two sentences at most · then `Recall:` one question about the previous bite's term, no options, no hints in the formatting.
- Kyle answers alongside his must-do pick. Confirm in one line (right, or the correct answer in one sentence). Append `YYYY-MM-DD · <term> · hit|miss · bite` to `~/Learning/a2c-auctions/recall-log.md`. Nothing else changes.

Report back with `grep -n 'Bite' <each file>` output for all three files.
````

- [ ] **Step 2: Verify**

Run: `grep -n 'Bite' ~/Desktop/A2CAuctions/.claude/skills/day/SKILL.md ~/Desktop/A2CAuctions/.claude/skills/day/references/hook-template.md ~/Desktop/A2CAuctions/.claude/day.md | wc -l`
Expected: `9` or more (2 in SKILL.md, 2 in the template, 5 in day.md). Then `grep -n '^7\. One question' ~/Desktop/A2CAuctions/.claude/skills/day/SKILL.md` prints one line.

### Task C.2: The Sunday learning hour (Kyle's veto)

- [ ] **Step 1: Ask once**

`AskUserQuestion`: "Create a recurring Sunday calendar event 'A2C — Learning hour' (60 min, color 9, description carries the two commands)? Pick a start time." Options: 9:00 AM Central, 10:00 AM Central, 4:00 PM Central, Don't create it. (Other is always available.)

- [ ] **Step 2: On yes, create it**

Load `mcp__claude_ai_Google_Calendar__create_event` via `ToolSearch`. Fields: calendar `primary`; summary `A2C — Learning hour`; start = the coming Sunday (2026-09-20 if the run is before then) at the chosen time, `America/Chicago`; end = start + 60 min; recurrence `["RRULE:FREQ=WEEKLY;BYDAY=SU"]`; `colorId` `9`; description exactly:

```
Learning hour. From a terminal:
cd ~/Learning/a2c-auctions && claude
1. /teach          (one lesson, 5 to 10 min, then its quiz)
2. /mock-call      (one drill, about 10 min; voice if the headset is on)
Workspace: ~/Learning/a2c-auctions/ · recall-log.md is the score sheet.
```

Then `get_event` on the returned id and confirm the description round-trips. Brief Kyle in one line with the event's first occurrence. On "Don't create it": record the decision in the closing brief and move on.

### Task C.3: Final verification and the closing brief

- [ ] **Step 1: Run the checklist and paste the results**

```bash
cd ~/Learning/a2c-auctions && make strict && git status --short | wc -l && git branch --show-current && ls research personas && wc -l research/*.md personas/*.md | tail -1
```
Expected: strict OK; `0`; `main`; seven digests and five personas listed.

```bash
git -C ~/Projects/claude-config log --oneline main -3 && ls ~/.claude/skills/mock-call/
```
Expected: the mock-call merge on `main`; `PERSONA-FORMAT.md SKILL.md`.

- [ ] **Step 2: Closing brief to Kyle**, in this order: what landed (workspace commit SHAs, the claude-config PR and merge SHA, the calendar event or the veto), every review's outcome in one line each, anything left out and why, then **Kyle's next steps**:

1. `cd ~/Learning/a2c-auctions && claude`, then `/teach-research` (no topic needed; it reads MISSION.md, confirms it, and hunts the `## Gaps` lanes in top-up mode; curate the table when it appears). Snapshot first: `cp RESOURCES.md /tmp/RESOURCES.before.md`, and diff afterward to confirm every internal entry survived verbatim.
2. `/teach` for lesson one (the A2C deal itself is the suggested first lesson).
3. Smoke-test the drill: `/mock-call receiver --text --turns 6` from the workspace, and `/mock-call` from `~/Desktop/A2CAuctions` to see the guard stop. Then one two-turn voice run.
4. Next weekday morning, `/day` in the A2C folder: the bite line appears only once `reference/` exists, so expect no change until after the first `/teach`.
5. After `/teach-research`, ask a session to draft `zack-questions.md` from what `## Gaps` still lists (candidate list in spec §5.3).

---

## Self-review (run before handing off)

**Spec coverage.** §3 workspace contract → Tasks 0.1–0.3 and tickets 01–04; §4 mission → Task 0.2; §5.1 digests → tickets 01–03; §5.2 public lanes → RESOURCES.md `## Gaps` in Task 0.2 (Kyle runs `/teach-research`); §5.3 Zack → closing brief step 5 (deferred by design); §6 lesson arc → Kyle's `/teach` (not a build item); §7 mock-call → Phase A; §7.4 personas → ticket 04; §8 bite → Task C.1; §9 Sunday → Task C.2; §10 audio → out of scope (phase 3); §12 verification → Tasks B.3, C.1 step 2, C.3, and the runtime checks handed to Kyle; §14 landing → Task A.2 and B.3.

**Placeholder scan.** No TBD/TODO. Every file has its full content in the step that creates it.

**Consistency.** Persona file names (`01-receiver.md` … `05-zack.md`) match in ticket 04, PERSONA-FORMAT, the mock-call slug rule, and the spec (amended). The seven digest slugs match in RESOURCES.md, tickets 01–03, and the spec. `make test` expected counts: 7 after seed, 4 / 5 / 5 in tickets 01 / 02 / 03 (each worktree has only its own digests), 0 in ticket 04. The `/day` item numbers (Bite = 6, question = 7) match the spec (amended) and the template note.

---

**Run-config note (for the orchestrator session):** Fable 5.1 · `high`. The session coordinates, proposes review scopes, and handles wake events; the building is done by Opus 5 workers and subagents. Launch it in the workspace directory (it must exist first; an empty folder is enough) so `/orchestrate` finds the repo it creates in Phase 0:

```
mkdir -p ~/Learning/a2c-auctions && cd ~/Learning/a2c-auctions && claude --model claude-fable-5-1 --effort high --name a2c-learning-orchestrator
```
