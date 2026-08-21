# Architecture-improvement sweep: shallow modules → deep modules, end to end

**Status:** Idea — not committed. Mined from ""Software Fundamentals Matter More Than Ever" — Matt Pocock" (https://www.youtube.com/watch?v=v4F1gFy-hqg) by `cc-yt-idea-mine` on 2026-08-21.

## Premise

Pocock's "improve codebase architecture" skill: "explore the codebase, look for
opportunities where there's code that's kind of… related, and wrap all of that in a deep
module" — "quite complicated to do, but a set of steps that you can reusably do again
and again." His argument for why it pays: shallow-module sprawl is "really hard for the
AI to explore," while a deep-module codebase is testable at its interfaces and rewards
TDD.

## The bet

The setup has the *vocabulary* (`codebase-design`), the *per-cluster method*
(DEEPENING.md's dependency-category playbook), and the *map* (`architecture-viewer`'s
arch-graph with a file:line behind every edge) — but no skill runs the loop across a
repo and lands refactors. An orchestrated sweep — map → rank deepening candidates →
apply DEEPENING per cluster → one branch/PR per deepening — turns two reference skills
into an executable one.

## Decisions / open questions

- Relationship to [`deep-modules-for-agent-legibility`](deep-modules-for-agent-legibility.md)
  (Uncle Bob mine, 2026-08-20): that capture is the *convention* (prefer deep modules);
  this is the *mechanism* (actively restructure toward them). They should land as a pair
  or merge.
- Candidate ranking: reuse architecture-viewer's findings banner (cycles, hubs,
  layering violations) as the candidate source, or a fresh analysis pass?
- Batch size: one deepening per PR is the safe default; is a multi-cluster mode ever
  worth the review surface?

## Credible first step

Check mattpocock/skills for the talk's own "improve codebase architecture" skill and
evaluate vendoring before building; if building, wire architecture-viewer's arch-graph
JSON as the candidate-finding stage.

## Dependencies

`architecture-viewer`'s `arch-graph/v1` JSON contract and `codebase-design`/DEEPENING.md
— both internal to this repo, no Claude Code API surface. Verification at capture
(2026-08-21): no external capability claims to check.

## Explicitly out of scope

Whole-repo rewrites (per-cluster, per-PR only), and defect hunting (bug-hunt's lane —
this sweep restructures, it doesn't fix bugs).

## Source segment

> "So, how do you turn a codebase that looks like this into a codebase that looks like
> that? Well, I've got a skill for that. Improve codebase architecture. … You just sort
> of explore the codebase, look for opportunities where there's code that's kind of…
> related, and wrap all of that in a deep module. And this is a testable codebase
> because the boundaries around this code are so so simple."
