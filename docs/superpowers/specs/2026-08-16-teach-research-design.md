# `teach-research` — design spec

**Written:** 2026-08-16 · **Status:** approved by Kyle 2026-08-16 (brainstorm → design → this spec)
**Deliverable:** a new global skill at `skills/teach-research/` (SKILL.md + RESEARCH-FORMAT.md),
plus its reference-doc row and usage-playbook card. The `teach` skill is **not edited**.

---

## 1. The problem

The `teach` skill (vendored from Matt Pocock's repo, landed 2026-08-12) treats resource-finding as
a prerequisite — *"Before the `RESOURCES.md` is well-populated, your focus should be to find
high-quality resources… Never trust your parametric knowledge"* — but it does that work **inline,
during the interactive teaching session**, where it competes with lesson time in a single context.
The result: the first sessions of any new topic are spent searching instead of teaching, coverage
is only as broad as one context allows, and lesson-building later re-fetches the web for anything
it wants to cite.

`teach-research` front-loads that step into a dedicated research pass: point it at a topic, it
interviews for the mission, researches broadly in parallel, and leaves behind a workspace where
`/teach` drops straight into lesson-building.

## 2. Settled decisions (from the brainstorm)

| Decision | Choice | Why |
|---|---|---|
| Shape | Companion skill; teach untouched | Stays cleanly diffable against Pocock's upstream; research can run long/unattended while teach stays interactive |
| Outputs | Curated `RESOURCES.md` + cached digests in `research/` | RESOURCES.md is consumed by teach with zero changes; digests make later lessons citable without re-fetching |
| Syllabus / seeded glossary | **Out of scope** | Teach computes next steps from learning records; glossary grows as Kyle learns |
| Mission timing | Companion interviews first, writes `MISSION.md` | One seamless pipeline; `/teach` later finds the mission answered |
| Engine | Gated two-phase fan-out (Approach B) | Curation is a ten-second judgment call for Kyle vs. an expensive guess for an agent; `--auto` skips the gate for unattended runs |

## 3. Identity & invocation

- Global skill at `skills/teach-research/SKILL.md`, typed-only (`disable-model-invocation: true`),
  `argument-hint` for the topic. Invoked as `/teach-research <topic>`.
- Same posture as teach: run from a **dedicated learning directory**, never inside a project repo.
  Inherits teach's workspace guard verbatim — if the directory shows signs of being a software
  project (`.git`, `package.json`, `CLAUDE.md`, source code) or is `$HOME`, stop before writing
  anything, report the resolved directory and intended paths, and suggest `~/Learning/<topic>/`.
- Flags: `--auto` — skip the curation gate (unattended/overnight mode); finders' top picks are
  kept automatically.

## 4. Flow

1. **Mission.** If `MISSION.md` exists, confirm it briefly and reuse it. Otherwise run the same
   push-back-on-vagueness interview teach would run and write `MISSION.md` in teach's
   MISSION-FORMAT. Everything downstream filters through it. (In `--auto` mode with no existing
   `MISSION.md`, the interview still runs — mission capture is the one step that cannot be
   automated away; `--auto` only skips the *curation* gate.)
2. **Discovery fan-out.** Six parallel finder agents, one per modality, each blind to the others:
   official docs / primary sources · books · structured courses · video · papers & high-signal
   blogs · communities. Each finder:
   - verifies its URLs actually resolve before returning them;
   - annotates every candidate: title, URL, type, author + why trusted, what it covers, mission fit;
   - marks its top 2–3 picks.
3. **Curation gate.** Merge and dedup in the main context; present one table grouped by modality —
   title, type, why-trusted, mission fit, keep/cut recommendation. Kyle trims or says "take all."
   With `--auto`, the top picks are kept without asking.
4. **Caching fan-out.** Parallel agents fetch each kept source and write a digest to
   `research/<slug>.md` per RESEARCH-FORMAT.md — key concepts, structure/TOC, select quotes with
   locations, why it's trusted — **not** verbatim dumps. Unfetchable sources (books, paywalls) get
   a metadata-only digest: what it covers, where to get it.
5. **Write outputs & hand off.** `RESOURCES.md` in teach's exact RESOURCES-FORMAT (Knowledge /
   Wisdom communities / Gaps), each entry keeping its one-line annotation plus a
   `Cached: ./research/<slug>.md` link. Anything no finder could cover, and any fetch that failed,
   lands explicitly in `## Gaps`. Closing message: summary of what was found, the gaps, and
   "run `/teach` from this directory."

## 5. Workspace contract

The companion writes exactly three things: `MISSION.md`, `RESOURCES.md`, `research/`.

- `MISSION.md` and `RESOURCES.md` are files teach already reads, in formats teach already defines —
  `/teach` finds the mission answered and resources "well-populated" and drops straight into
  lesson-building. **No edit to teach is needed or made.**
- The cached digests are discoverable because every `RESOURCES.md` entry links to its own; teach's
  instruction to ground lessons in resources naturally pulls them in.
- `research/` collides with nothing in teach's workspace layout (`lessons/`, `reference/`,
  `learning-records/`, `assets/`, `NOTES.md`, `GLOSSARY.md`).
- `RESEARCH-FORMAT.md` beside the SKILL.md pins the digest format, mirroring how teach documents
  its own formats (MISSION-FORMAT.md, RESOURCES-FORMAT.md, …).

## 6. Re-runs & edge cases

- **Top-up mode.** Running `/teach-research` where `RESOURCES.md` already exists: finders receive
  the existing entries plus the `## Gaps` section and hunt only for what's missing; results merge,
  never clobber.
- **Fetch failures** mid-run downgrade a source to a metadata-only digest plus a `Gaps` note —
  never abort the run.
- **Scale.** The fan-out stays inside the medium workflow guideline (~15 agents) by batching cache
  fetches (one agent per 3–4 sources) when the kept list is long.

## 7. Landing it

- Branch `feat/teach-research-skill` in claude-config; skill + RESEARCH-FORMAT.md; reference-doc
  row and usage-playbook card in the same commit; adversarial review before merge.
- Per the shell-snippets lesson (see memory: 21 review rounds of evidence), SKILL.md is written as
  numbered steps and named invariants — no copy-paste shell blocks.
- **Verification:** live smoke run — point it at a real topic in a scratch `~/Learning/` directory
  and confirm (a) the workspace files match teach's formats, (b) `/teach` picks up the workspace
  and goes straight to lesson-building.

## 8. Out of scope

- Editing the `teach` skill in any way (including the "tiny hook" variant — explicitly declined).
- Proposed syllabus / lesson roadmap output.
- Seeding `GLOSSARY.md`.
- NotebookLM integration (the notebook/curriculum chain is a separate ecosystem with its own
  skills).
