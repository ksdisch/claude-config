# Glossary bootstrap: mine the ubiquitous language from an existing codebase

**Status:** Idea — not committed. Mined from ""Software Fundamentals Matter More Than Ever" — Matt Pocock" (https://www.youtube.com/watch?v=v4F1gFy-hqg) by `cc-yt-idea-mine` on 2026-08-21.

## Premise

Pocock's ubiquitous-language skill "scans your code base, looks for terminology," and
generates a markdown file of term tables — the DDD ubiquitous language, bootstrapped
from what the code already calls things. He keeps it loaded in every AI conversation and
reports it "has absolutely been a powerhouse… unbelievably good": planning improves, the
AI's thinking gets *less* verbose, and implementations align better with plans.

## The bet

The gap is real: `domain-modeling` sharpens a glossary *while designing* and explicitly
declares that merely reading/creating one wholesale is not its lane; `spec-miner` mines
behavior, not vocabulary. Three consumers already exist (`domain-modeling`, `wait-what`,
the engineering flow read `CONTEXT.md` when present) but nothing creates the file for a
brownfield repo. A batch bootstrap — skill or `spec-miner`-style agent — fills it.

## Decisions / open questions

- Skill vs. agent (`spec-miner` is the worked precedent for a repo-scanning,
  single-file-writing agent with an overwrite guard).
- Output must target `domain-modeling`'s `CONTEXT-FORMAT.md` so the maintenance skill
  can take over from day one.
- Overwrite posture when a `CONTEXT.md` already exists (spec-miner's report-don't-write
  default is the likely model).

## Credible first step

Check whether mattpocock/skills already ships this skill (the talk says it does) and
evaluate vendoring it per the #103/#105 pattern before building from scratch.

## Dependencies

Nothing version-sensitive — file conventions plus `domain-modeling`'s CONTEXT-FORMAT.md.
Verification at capture (2026-08-21): no Claude Code capability claims in play; nothing
to check against docs.

## Explicitly out of scope

Ongoing glossary maintenance (that stays `domain-modeling`'s job) and any enforcement
that skills *read* the glossary (that is the separate
[`load-context-md-before-planning`](load-context-md-before-planning.md) capture).

## Source segment

> "So I made a skill. This skill is the ubiquitous language skill. Basically just scans
> your code base, looks for terminology, and then um creates a markdown file. Creates
> the ubiquitous language markdown file, a bunch of markdown tables with all of the
> terminology."

Context: his fix for the "AI is way too verbose" failure mode — a shared language closes
the gap the way it does with human domain experts; "conversations among developers, and
expressions of the code, and conversations with domain experts are all derived from the
same domain model."
