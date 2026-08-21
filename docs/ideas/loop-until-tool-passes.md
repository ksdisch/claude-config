# Loop-until-the-tool-says-okay as the core agent contract

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob frames every deterministic tool as a loop condition: "you must change the code until
this tool says that it's okay." The agent grinds — split functions, add tests, cut
complexity — until conformance, trading raw speed for quality while staying 2–4× faster
than a human.

## The bet

The *contract framing* is worth adopting explicitly: gates aren't reports, they're loop
conditions. Partially covered — the `ralph-loop` plugin loops a prompt until done, and
the settings.json Stop-hook evaluator already loops on *response quality* — but no gate
in the config loops on a *code* metric yet.

## Decisions / open questions

- This is the connective tissue between [`crap-score-gate.md`](crap-score-gate.md),
  [`module-dependency-rules-checker.md`](module-dependency-rules-checker.md), and the
  gauntlet — likely absorbed by whichever ships first rather than built alone.
- Bob's own warning is the design constraint: "eventually you will slow the agents down
  to the point where they're slower than humans. And at that point you've lost the game."
  Every loop needs an escape valve (max iterations → report and stop).

## Credible first step

None standalone — fold into the first shipped gate; this stub exists so the framing (and
the escape-valve requirement) isn't lost.

## Dependencies

- Stop hook can force continuation — **verified 2026-08-20**
  (code.claude.com/docs/en/hooks.md); `ralph-loop` plugin enabled — **verified** (settings.json).

## Explicitly out of scope

- A generic loop framework; anything the specific gates don't need.

## Source segment

> "you must change the code until this tool says that it's okay"

Context: "you're putting them into a loop… you are sacrificing productivity for higher
quality and at some point that's got to give way. But I haven't found the end point of
that yet."
