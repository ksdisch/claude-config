---
name: teach-research
description: Research companion for the teach skill — interviews for the mission, fans out parallel finder agents across six source modalities, gates the candidate list through the user, then caches approved sources as digests, leaving MISSION.md, RESOURCES.md, and research/ ready for /teach to consume. The teach skill itself is never modified. Typed-only entry point (/teach-research <topic>) — run it from a dedicated learning directory, not inside a project repo, since it writes workspace files at the root of wherever it runs. Append --auto to skip the interactive pauses (mission confirm + curation gate) for unattended runs.
disable-model-invocation: true
argument-hint: "What topic should be researched? (append --auto to skip the interactive pauses)"
---

The user wants a learning workspace stocked with vetted sources before (or between) `/teach`
sessions — so that lesson one is a lesson, not a search. This skill front-loads the
resource-finding work the teach skill would otherwise do inline during teaching sessions.

## Relationship to the teach skill

This skill writes exactly three things at the root of the current directory: `MISSION.md`,
`RESOURCES.md`, and `research/`. The first two are files the teach skill already reads, in
formats the teach skill owns — read [../teach/MISSION-FORMAT.md](../teach/MISSION-FORMAT.md)
and [../teach/RESOURCES-FORMAT.md](../teach/RESOURCES-FORMAT.md) before writing either.
`research/` digests follow [RESEARCH-FORMAT.md](./RESEARCH-FORMAT.md), owned here.

## Invariants

Referenced by name below. Each invariant holds on every path, whether or not a step cites it.

- **teach-untouched** — never edit the teach skill's files, and never write any workspace file
  other than the three above. `lessons/`, `reference/`, `learning-records/`, `assets/`,
  `GLOSSARY.md`, and `NOTES.md` belong to the teach skill.
- **mission-grounded** — no discovery begins until `MISSION.md` exists and has been confirmed
  this run — by the user interactively, or implicitly in auto mode, where an existing mission
  counts as confirmed. Every finder brief carries the mission.
- **never-clobber** — existing `MISSION.md` content and existing `RESOURCES.md` entries are
  merged into, never overwritten or removed. Pruning is the user's move, not this skill's.
- **verified-links** — no URL reaches the candidate table unless the finder that proposed it
  confirmed the URL resolves. A source that cannot be verified is reported as a gap, not
  listed as a source.
- **digest-not-dump** — cache files are digests with select attributed quotes, never verbatim
  copies. Unfetchable sources get metadata-only digests; content is never fabricated.
- **honest-gaps** — every modality no finder could cover, every candidate cut for a reason
  worth remembering, and every failed fetch lands in the `## Gaps` section of `RESOURCES.md`.
  Candidates the skipped gate cut unseen in auto mode land in `## Deferred candidates`
  instead: they are verified sources awaiting a decision, not missing coverage, and `## Gaps`
  is what drives future search. Silent omission is the failure mode this invariant exists to
  prevent.
- **gate-only-auto** — `--auto` removes exactly two pauses: the mission confirm (step 3, and
  only when `MISSION.md` already exists) and the curation gate (step 6). It never skips the
  workspace guard, the mission interview, or verification.

## Workspace Guard

Before any other step — including the mission step — check that the current directory is a
dedicated learning workspace:

- If `MISSION.md` already exists here, this is an established workspace: proceed.
- Otherwise, if the directory shows signs of being a software project or other pre-existing
  content (`.git`, `package.json`, `CLAUDE.md`, source code, an existing `assets/` or
  `NOTES.md`), or is the user's home directory, **stop before writing anything**: report the
  resolved current directory and the exact paths this skill would write (`MISSION.md`,
  `RESOURCES.md`, `research/`), suggest a dedicated directory instead (e.g.
  `~/Learning/<topic>/`), and wait for the user to confirm this location or point at another.
  Never create the first workspace file until the location is confirmed. In an unattended
  run, an unconfirmed location is a stop-and-report, never a wait.
- Otherwise — nothing above matched: an empty directory, or one holding only content this
  skill wrote — proceed.

## Procedure

1. **Parse the invocation.** The argument is the topic; the literal token `--auto` anywhere in
   it sets auto mode (*gate-only-auto*) and is stripped from the topic text before the topic
   is used anywhere. No topic and no existing `MISSION.md` → ask for one (in an unattended
   run, stop and report instead).
2. **Run the Workspace Guard** above.
3. **Mission.** If `MISSION.md` exists, summarize it back to the user in two sentences and ask
   for a brief confirm (in auto mode, an existing mission is taken as confirmed). A topic
   argument supplied alongside an existing mission is this run's narrowing focus, not a new
   mission: say so in the summary and carry it into step 5's briefs, so the finders hunt that
   corner of the mission rather than all of it. If the argument plainly names a different
   subject than the mission, stop and report instead — one mission per workspace, so a
   different subject means a different workspace
   ([../teach/MISSION-FORMAT.md](../teach/MISSION-FORMAT.md)). If `MISSION.md` does
   not exist, run a mission interview in the style the teach skill prescribes — push back on
   vagueness, concrete over abstract, one question at a time — and write `MISSION.md` per
   [../teach/MISSION-FORMAT.md](../teach/MISSION-FORMAT.md). In a truly unattended run
   (subagent, cron, cloud one-shot) with no `MISSION.md`, stop and report instead: a mission
   cannot be invented on the user's behalf (*mission-grounded*).
4. **Read the workspace.** Read whichever of `RESOURCES.md` and `NOTES.md` exist, both
   read-only (*teach-untouched* forbids writing `NOTES.md`, not reading it). If either records that the
   user has opted out of joining communities, skip the communities finder in step 5 and say so
   in the close: a recorded opt-out is durable, and re-proposing communities every run is the
   outcome that rule exists to prevent. If `RESOURCES.md` exists, this run is a top-up: read
   every existing entry, the current `## Gaps` section, and the current `## Deferred
   candidates` section. Finders receive all three and use them differently — gaps are what to
   hunt for, entries and deferred candidates are what not to propose again — and results will
   merge (*never-clobber*).
5. **Discovery fan-out.** Dispatch one finder subagent per modality in parallel, six in all:
   official docs / primary sources · books · structured courses · video · papers &
   high-signal blogs · communities (dropped when step 4 found a recorded opt-out). Each
   finder's brief contains: `MISSION.md` verbatim and whole — all four sections, so that
   `Constraints` and `Out of scope` reach the finder along with `Why` and `Success looks like`
   (*mission-grounded*); this run's narrowing focus if step 3 established one; its single
   modality; the already-held sources and deferred candidates to exclude (top-up mode); and
   the required return shape — for each candidate: title, URL, type, author plus one line on
   why they are trustworthy, what it covers, one line on mission fit, and whether it is one of
   the finder's top 2–3 picks. A candidate that breaks a `Constraints` bound — budget, time,
   equipment, stated learning preference — or falls under `Out of scope` is dropped by the
   finder, not proposed for the gate to catch. Each finder must fetch every URL it proposes
   and drop any that does not resolve, returning it as a gap line instead (*verified-links*,
   *honest-gaps*); it reports a thin modality honestly rather than padding with weak sources
   (*honest-gaps*).
6. **Curation gate.** Merge the finders' returns, dedup by URL and by near-identical title,
   and present one table grouped by modality — columns: #, title (linked to the URL), type, why
   trusted, mission fit, keep/cut recommendation. In top-up mode, anything already sitting in
   `## Deferred candidates` joins the table marked as deferred by an earlier run, so the user
   can pull one in — the finders were told not to re-propose it. The user trims, swaps, or says
   "take all"; wait for that answer. In auto mode (*gate-only-auto*): keep exactly the finders' top picks,
   cut the rest, record the auto-cut candidates (title + URL, one line each) as candidates
   deferred by the skipped gate — step 8 writes them into `## Deferred candidates`, never into
   `## Gaps`, because they are verified sources the user has not yet seen rather than coverage
   nobody could find — and record in the closing summary that the gate was skipped.
7. **Caching fan-out.** Batch the kept sources three to four per cacher subagent. Each cacher
   fetches its sources and writes one digest per source at `research/<slug>.md` per
   [RESEARCH-FORMAT.md](./RESEARCH-FORMAT.md) (*digest-not-dump*). A fetch that fails
   mid-run downgrades that source to a metadata-only digest plus a gap note — it never aborts
   the run (*honest-gaps*). Cachers run in parallel and in a `research/` earlier runs may
   already have filled, so no cacher can see another's writes: each one checks its target path
   first and never overwrites a file it did not write — on a taken path it appends `-2` (then
   `-3`, …) per [RESEARCH-FORMAT.md](./RESEARCH-FORMAT.md) and reports the collision. Each
   cacher returns, per source: the exact path it wrote, the `Fetched` value (a date, or the
   not-fetched reason), any collision it hit, and any gap note.
8. **Write `RESOURCES.md`** per
   [../teach/RESOURCES-FORMAT.md](../teach/RESOURCES-FORMAT.md), with three additions this
   skill owns: each entry ends with a line `Cached: ./research/<slug>.md` — using the exact
   path its cacher returned, never a re-derived slug; a single line sits directly under the
   title: `Entries marked "Cached:" have local digests in ./research/ — read the digest
   before searching the web.`; and, in auto mode, a `## Deferred candidates` section holding
   the candidates the skipped gate cut unseen, one line each with title and URL, under a
   sentence saying they were never shown to the user. Write the `## Gaps` section from the
   genuine absences *honest-gaps* collected — modalities no finder could cover, failed fetches,
   candidates cut for a reason worth remembering — and nothing else. In top-up mode, merge new
   entries into the existing sections, rewrite `## Gaps` to reflect what is still missing, and
   rewrite `## Deferred candidates` to hold only what is still deferred — a candidate the user
   pulled in at step 6 drops out of it, now that it is an entry (*never-clobber* for entries;
   those two are the sections this skill rewrites wholesale, because a filled gap and an
   adopted candidate are not history worth keeping).
9. **Verify the contract.** Confirm: every `RESOURCES.md` entry's `Cached:` path exists; every
   file in `research/` is linked from some entry; the number of entries carrying a `Cached:`
   line equals the number of files in `research/` — two entries pointing at one digest is a
   slug collision that overwrote a source, which the first two checks both pass; no file
   outside `MISSION.md`,
   `RESOURCES.md`, `research/` was created or modified (*teach-untouched*). Any check that
   fails is reported in the close, not repaired: never delete a `research/`
   file and never rewrite a pre-existing entry (*never-clobber*). The one exception is a
   `Cached:` line this run wrote that points nowhere — drop that line and note it in
   `## Gaps` before the close.
10. **Close.** Report to the user: sources found per modality, what was cached, the open gaps,
    whether the gate was skipped — and finish with: run `/teach` from this directory; the
    mission is answered and the resources are stocked.

## Unattended runs

Auto mode makes steps 4–10 fully unattended — steps 1–3 can still stop and report (wrong
directory, no mission) but never wait — so `/teach-research <topic> --auto` can run
overnight **in a workspace whose `MISSION.md` already exists** (or interactively, where the
mission interview runs first and everything after is automatic). Unattended with no mission =
stop and report, per step 3.
