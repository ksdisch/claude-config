---
name: teach-research
description: Research companion for the teach skill — interviews for the mission, fans out parallel finder agents across six source modalities, gates the candidate list through the user, then caches approved sources as digests, leaving MISSION.md, RESOURCES.md, and research/ ready for /teach to consume. The teach skill itself is never modified. Typed-only entry point (/teach-research <topic>) — run it from a dedicated learning directory, not inside a project repo, since it writes workspace files at the root of wherever it runs. Append --auto to skip the curation gate for unattended runs.
disable-model-invocation: true
argument-hint: "What topic should be researched? (append --auto to skip the curation gate)"
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

Every procedure step below names the invariants it must uphold. Reference them by name.

- **teach-untouched** — never edit the teach skill's files, and never write any workspace file
  other than the three above. `lessons/`, `reference/`, `learning-records/`, `assets/`,
  `GLOSSARY.md`, and `NOTES.md` belong to the teach skill.
- **mission-grounded** — no discovery begins until `MISSION.md` exists and the user has
  confirmed it this run. Every finder brief carries the mission.
- **never-clobber** — existing `MISSION.md` content and existing `RESOURCES.md` entries are
  merged into, never overwritten or removed. Pruning is the user's move, not this skill's.
- **verified-links** — no URL reaches the candidate table unless the finder that proposed it
  confirmed the URL resolves. A source that cannot be verified is reported as a gap, not
  listed as a source.
- **digest-not-dump** — cache files are digests with select attributed quotes, never verbatim
  copies. Unfetchable sources get metadata-only digests; content is never fabricated.
- **honest-gaps** — every modality no finder could cover, every candidate the user cut for a
  reason worth remembering, and every failed fetch lands in the `## Gaps` section of
  `RESOURCES.md`. Silent omission is the failure mode this invariant exists to prevent.
- **gate-only-auto** — `--auto` skips exactly one thing: the curation gate (step 6). It never
  skips the workspace guard, the mission step, or verification.

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
  Never create the first workspace file until the location is confirmed.

## Procedure

1. **Parse the invocation.** The argument is the topic; the literal token `--auto` anywhere in
   it sets auto mode (*gate-only-auto*). No topic and no existing `MISSION.md` → ask for one.
2. **Run the Workspace Guard** above.
3. **Mission.** If `MISSION.md` exists, summarize it back to the user in two sentences and ask
   for a brief confirm (in auto mode, an existing mission is taken as confirmed). If it does
   not exist, run a mission interview in the style the teach skill prescribes — push back on
   vagueness, concrete over abstract, one question at a time — and write `MISSION.md` per
   [../teach/MISSION-FORMAT.md](../teach/MISSION-FORMAT.md). In a truly unattended run
   (subagent, cron, cloud one-shot) with no `MISSION.md`, stop and report instead: a mission
   cannot be invented on the user's behalf (*mission-grounded*, *never-clobber*).
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
   every URL it proposes and drop any that does not resolve (*verified-links*); it reports a
   thin modality honestly rather than padding with weak sources (*honest-gaps*).
6. **Curation gate.** Merge the finders' returns, dedup by URL and by near-identical title,
   and present one table grouped by modality — columns: title, type, why trusted, mission
   fit, keep/cut recommendation. The user trims, swaps, or says "take all"; wait for that
   answer. In auto mode (*gate-only-auto*): keep exactly the finders' top picks, cut the
   rest, and record in the closing summary that the gate was skipped.
7. **Caching fan-out.** Batch the kept sources three to four per cacher subagent. Each cacher
   fetches its sources and writes one digest per source at `research/<slug>.md` per
   [RESEARCH-FORMAT.md](./RESEARCH-FORMAT.md) (*digest-not-dump*). A fetch that fails
   mid-run downgrades that source to a metadata-only digest plus a gap note — it never aborts
   the run (*honest-gaps*).
8. **Write `RESOURCES.md`** per
   [../teach/RESOURCES-FORMAT.md](../teach/RESOURCES-FORMAT.md): `## Knowledge` and
   `## Wisdom (Communities)` sections, every entry annotated with its one-line
   what-it-covers/when-to-reach-for-it note plus a final line `Cached: ./research/<slug>.md`
   pointing at its digest. Write the `## Gaps` section from everything *honest-gaps*
   collected. In top-up mode, merge new entries into the existing sections and rewrite
   `## Gaps` to reflect what is still open (*never-clobber* for entries; Gaps is the one
   section this skill rewrites wholesale, because a filled gap is not history worth keeping).
9. **Verify the contract.** Confirm: every `RESOURCES.md` entry's `Cached:` path exists; every
   file in `research/` is linked from some entry; no file outside `MISSION.md`,
   `RESOURCES.md`, `research/` was created or modified (*teach-untouched*).
10. **Close.** Report to the user: sources found per modality, what was cached, the open gaps,
    whether the gate was skipped — and finish with: run `/teach` from this directory; the
    mission is answered and the resources are stocked.

## Unattended runs

Auto mode makes steps 4–10 fully unattended, so `/teach-research <topic> --auto` can run
overnight **in a workspace whose `MISSION.md` already exists** (or interactively, where the
mission interview runs first and everything after is automatic). Unattended with no mission =
stop and report, per step 3.
