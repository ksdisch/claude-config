# Grilling-before-plan-mode convention

**Status:** Idea — not committed. Mined from ""Software Fundamentals Matter More Than Ever" — Matt Pocock" (https://www.youtube.com/watch?v=v4F1gFy-hqg) by `cc-yt-idea-mine` on 2026-08-21.

## Premise

Pocock — author of the `grilling` skill this repo vendors — prefers it to plan mode:
"Plan mode is extremely eager to create an asset. It really wants to just create a plan
and start working. Whereas I think it's a lot nicer to reach a shared design concept
first" (Brooks' *Design of Design*: the design concept is "not an asset… it is the
invisible theory of what you're building").

## The bet

For design-heavy work, a convention routes through `grilling` before (or instead of)
plan mode. The superpowers flowchart already gates EnterPlanMode behind
*brainstorming*; the open question this capture exists to force: should `grilling` sit
in that gate too — one gate, two gates, or routed by work type (divergent idea →
brainstorm; convergent plan with a real design tree → grill)?

## Decisions / open questions

- **The gate decision above** — this is the capture's whole point.
- Relationship to [`anti-plan-maxing`](anti-plan-maxing.md) (Uncle Bob mine): it pulls
  the opposite direction — plan *less*, iterate. Pocock says interview *more* before
  the plan exists. Both attack plan mode's eagerness to produce an asset; adjudicating
  them is part of this decision, not two separate ones.
- Where the convention lives: global CLAUDE.md vs. the superpowers flowchart (which is
  plugin-owned and updates upstream — a local rule is safer).

## Credible first step

Write the candidate rule text and try it for a week of design-heavy sessions before
committing anything to CLAUDE.md.

## Dependencies

Plan mode — **verified current 2026-08-21** via the claude-code-guide agent against
code.claude.com/docs/en/permission-modes.md: plan mode exists (Shift+Tab / `/plan` /
`--permission-mode plan`), its documented flow is explore → write plan → present for
approval, and **no hook can gate before the plan is written** — so this convention can
only live at the prompt/skill-routing layer, which is exactly the proposed shape.

## Explicitly out of scope

Modifying plan mode itself (impossible per the verification), and changing `grilling`'s
own behavior.

## Source segment

> "Don't at me on this, but I personally believe this is better than the default plan
> mode in the tool that I use, which is [Claude] Code. Plan mode is extremely eager to
> create an asset. It really wants to just create a plan and start working. Whereas I
> think it's a lot nicer to reach a shared design concept first."
