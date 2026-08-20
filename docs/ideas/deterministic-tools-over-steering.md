# Deterministic tools over steering instructions

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob started with 5–10 pages of steering prose and watched agents treat the rules "in
the Pirates of the Caribbean sense — more like guidelines," because of lost-in-the-middle:
everything past the first few sentences loses salience. His replacement: deterministic
tools after the fact, which "don't disappear that way."

## The bet

**Already covered** — this is the `hooks-over-prompts` convention adopted 2026-07-27
(auto-memory) and embodied in the settings.json hooks block. Captured per Kyle's
capture-all instruction; the open residual is small: the convention lives in an
auto-memory, not in a durable tracked file.

## Decisions / open questions

- Is coverage complete, or should hooks-over-prompts graduate from auto-memory to a
  written CLAUDE.md rule so it survives memory pruning and reaches vendored repos?
  (Run 1 of this mine flagged the same gap.) That's the only actionable delta.

## Credible first step

If the delta is wanted: one paragraph in CLAUDE.md citing the memory, same-day PR.
Otherwise close this stub as confirmed-covered.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20**.

## Explicitly out of scope

- Re-litigating the convention itself; converting any specific prose rule to a hook
  (each is its own change).

## Source segment

> "they treat those rules in the uh Pirates of the Caribbean sense. They're more like
> guidelines, you know, might follow"

Context: the lost-in-the-middle explanation — "the stuff at the very beginning and the
stuff at the very end have more prominence than the stuff in the middle… deterministic
tools don't disappear that way."
