# Architecture viewer: clickable module/dependency map of a repo

**Status:** **Built 2026-08-20** as [`skills/architecture-viewer/`](../../skills/architecture-viewer/SKILL.md) — v0 exactly as the "Credible first step" below describes it. The "Decisions / open questions" section is kept as the record of what was open; every one of them is settled, and the settled answer is noted inline. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob had his agents build him an architecture viewer: a UML-ish diagram of the system's
modular structure and dependency flow, clickable — module → submodules → the actual
code on screen. It's what let him stop reading code and start reading structure: he
interrogates the architecture at whatever level, gets "scared to death," then redesigns
and hands the agents an implementation plan.

## The bet

Strategic review needs a structural surface, and nothing in the inventory provides one —
`project-guide` covers architecture in prose, not as a navigable map. The rendering
muscle already exists in-house (`paper-gloss` hand-authors self-contained interactive
HTML; Artifacts render mermaid natively), so only the extraction half is new.

## Decisions / open questions — all settled 2026-08-20

- Output surface: self-contained HTML file (house `paper-gloss` pattern, works offline,
  annotatable) vs. published Artifact (shareable URL, native mermaid) vs. both.
  → **Settled: self-contained HTML file.** Artifact publishing is opt-in via `--publish`,
  because a repo's internal structure is Kyle's to share.
- Extraction: parse imports directly (per-language) vs. have an Explore-type agent map
  modules and emit the graph data. Agent-mapped is polyglot on day one; parsed is
  reproducible. Probably agent-mapped first, parser later.
  → **Settled: agent-mapped.** It is also the only way the **runtime** edges get found —
  a WebSocket dial, a spawned process — which an import parser structurally cannot see.
  Reproducibility is bought back by the validator instead: it opens every cited file.
- Drill-down depth: module → submodule → file is Bob's three levels; linking "open the
  code" can be `file:line` references rather than embedding source.
  → **Settled: one drill level for v0**, and "open the code" is a click-to-copy
  `file:line`. The parent pointer in the schema already allows a third level later.
- Pairs with [`module-dependency-rules-checker.md`](module-dependency-rules-checker.md):
  the viewer shows the graph, the checker enforces it — one data model should feed both.
  → **Settled: `arch-graph/v1`**, specified in
  [`skills/architecture-viewer/references/graph-schema.md`](../../skills/architecture-viewer/references/graph-schema.md),
  whose closing section states the four guarantees the checker is designed against. The
  checker itself is still unbuilt.

## Credible first step

A skill that runs on one repo and emits a single HTML page: modules as nodes, dependency
arrows, one level of click-to-expand, no code embedding. Judge whether the map changes
any real review before adding depth.

## Dependencies

- Artifact tool native mermaid rendering — **verified 2026-08-20** (documented Artifact
  capability); self-contained-HTML fallback has no dependency at all.

## Explicitly out of scope

- Live/watch mode; enforcing the dependency rules (the checker's job); IDE integration.

## Source segment

> "I also had my agents build me an architecture viewer so I can pop up on the screen a
> nice little UML diagram"

Context: "…that shows me the modular structure of the system and where the dependencies
run and I can click on a module and I can see inside it to the submodules and I can
click on the submodules and it'll actually pop the code up on the screen for me. So I
can drill down as much as I want and view the system architecture at any level."
