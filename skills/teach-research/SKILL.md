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
  worth remembering — by the user, or by the skipped gate in auto mode — and every failed
  fetch lands in the `## Gaps` section of `RESOURCES.md`. Silent omission is the failure
  mode this invariant exists to prevent.
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
   for a brief confirm (in auto mode, an existing mission is taken as confirmed). If it does
   not exist, run a mission interview in the style the teach skill prescribes — push back on
   vagueness, concrete over abstract, one question at a time — and write `MISSION.md` per
   [../teach/MISSION-FORMAT.md](../teach/MISSION-FORMAT.md). In a truly unattended run
   (subagent, cron, cloud one-shot) with no `MISSION.md`, stop and report instead: a mission
   cannot be invented on the user's behalf (*mission-grounded*).
4. **Detect top-up mode.** If `RESOURCES.md` exists, this run is a top-up: read every existing
   entry and the current `## Gaps` section. Finders will receive both, hunt only for what is
   missing, and results will merge (*never-clobber*).
5. **Discovery fan-out.** Dispatch six finder subagents in parallel, one per modality:
   official docs / primary sources · books · structured courses · video · papers &
   high-signal blogs · communities. Each finder's brief contains: the mission (verbatim
   `Why` and `Success looks like` sections), its single modality, the already-held sources to
   exclude (top-up mode), and the required return shape — for each candidate: title, URL,
   type, author plus one line on why they are trustworthy, what it covers, one line on
   mission fit, and whether it is one of the finder's top 2–3 picks. Each finder must fetch
   every URL it proposes and drop any that does not resolve, returning it as a gap line
   instead (*verified-links*, *honest-gaps*); it reports a thin modality honestly rather than
   padding with weak sources (*honest-gaps*).
6. **Curation gate.** Merge the finders' returns, dedup by URL and by near-identical title,
   and present one table grouped by modality — columns: #, title (linked to the URL), type, why
   trusted, mission fit, keep/cut recommendation. The user trims, swaps, or says "take all";
   wait for that answer. In auto mode (*gate-only-auto*): keep exactly the finders' top picks,
   cut the rest, record the auto-cut candidates (title + URL, one line each) as gaps
   deferred by the skipped gate — step 8 writes them into `## Gaps` — and record in the
   closing summary that the gate was skipped.
7. **Caching fan-out.** Batch the kept sources three to four per cacher subagent. Each cacher
   fetches its sources and writes one digest per source at `research/<slug>.md` per
   [RESEARCH-FORMAT.md](./RESEARCH-FORMAT.md) (*digest-not-dump*). A fetch that fails
   mid-run downgrades that source to a metadata-only digest plus a gap note — it never aborts
   the run (*honest-gaps*). Each cacher returns, per source: the exact path it wrote, the
   `Fetched` date (or the not-fetched reason), and any gap note.
8. **Write `RESOURCES.md`** per
   [../teach/RESOURCES-FORMAT.md](../teach/RESOURCES-FORMAT.md), with two additions this
   skill owns: each entry ends with a line `Cached: ./research/<slug>.md` — using the exact
   path its cacher returned, never a re-derived slug — and a single line sits directly under
   the title: `Entries marked "Cached:" have local digests in ./research/ — read the digest
   before searching the web.` Write the `## Gaps` section from everything *honest-gaps*
   collected. In top-up mode, merge new entries into the existing sections and rewrite
   `## Gaps` to reflect what is still open (*never-clobber* for entries; Gaps is the one
   section this skill rewrites wholesale, because a filled gap is not history worth keeping).
9. **Verify the contract.** Confirm: every `RESOURCES.md` entry's `Cached:` path exists; every
   file in `research/` is linked from some entry; no file outside `MISSION.md`,
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
