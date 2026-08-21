# Load CONTEXT.md before any planning or grilling session

**Status:** Idea — not committed. Mined from ""Software Fundamentals Matter More Than Ever" — Matt Pocock" (https://www.youtube.com/watch?v=v4F1gFy-hqg) by `cc-yt-idea-mine` on 2026-08-21.

## Premise

Pocock keeps his ubiquitous-language file "open all the time when I'm grilling with the
AI and planning," and reading the model's thinking traces he found it "not only improves
the planning, but it allows the AI to think in a less verbose way" with implementations
"more aligned with what you actually planned."

## The bet

One global CLAUDE.md line — *when the repo has a `CONTEXT.md` glossary, read it before
grilling, planning, or spec-writing* — captures the cheap half of the
ubiquitous-language payoff in every repo that already has a glossary.
`domain-modeling` itself calls reading the glossary "a one-line habit any skill can do";
`wait-what` already does it. No rule makes planning skills do it.

## Decisions / open questions

- CLAUDE.md rule vs. one-line edits inside `grilling`/`to-spec`/`wayfinder` themselves —
  the rule is one place, the skill edits survive vendoring into other repos.
- Standing lesson tension: hooks-over-prompts says must-happen behaviors go in hooks —
  but a "read this file first" nudge has no hook event; prompt-layer is the honest home,
  worth stating in the rule's own text.

## Credible first step

Add the one-liner to the global CLAUDE.md; revisit as skill-level edits if vendored
copies elsewhere miss it in practice.

## Dependencies

Nothing version-sensitive. Verification at capture (2026-08-21): no capability claims
to check. Pairs with
[`glossary-bootstrap-ubiquitous-language-miner`](glossary-bootstrap-ubiquitous-language-miner.md),
which creates the file this rule consumes.

## Explicitly out of scope

Creating or maintaining the glossary (the bootstrap capture and `domain-modeling`
respectively), and any enforcement beyond the stated convention.

## Source segment

> "And this, then I pass it to the AI, and I'm able to read it, too. And I actually have
> it open all the time when I'm grilling with the AI and planning and that. What I
> noticed by reading the thinking traces of the AI, it not only improves the planning,
> but it allows the AI to think in a less verbose way."
