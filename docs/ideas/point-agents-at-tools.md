# "Point your agents at my tools and build one for you": study-and-rebuild adoption

**Status:** Idea — not committed. Mined from "LIVE: Uncle Bob on Software Fundamentals in the Age of AI" (https://www.youtube.com/watch?v=zcLPGC-tvgk) by `cc-yt-idea-mine` on 2026-08-20.

## Premise

Bob publishes his tools (CRAP runners, mutation tester, agent harness) but tells people
not to download them: "point your agents at them, have the agents look at them, and then
build one for you." The external tool is a *specification of the essence*; the agent
rebuilds it customized to your stack, so you own and understand the result.

## The bet

A reusable adoption pattern for this config: when a video/repo/blog offers a tool, the
default move becomes study-and-rebuild rather than install-and-configure — trading a
build cost that agents made cheap for zero dependency surface and perfect fit. Uncertain
bet: sometimes installing is simply correct (yt-dlp), so the pattern needs a boundary.

## Decisions / open questions

- Convention line vs. a small skill ("given a tool URL/repo, extract its essence and
  propose a house version")? Start as a convention; the skill form is
  `cc-yt-idea-mine`-shaped and only earns building if the pattern fires often.
- Boundary: rebuild when the tool is small/opinionated/close to the config's core;
  install when it's commodity infrastructure.

## Credible first step

Apply it once deliberately — the CRAP gate ([`crap-score-gate.md`](crap-score-gate.md))
is the perfect candidate: point an agent at an existing CRAP implementation and build the
house version — then judge whether the pattern deserves a written rule.

## Dependencies

- Nothing version-sensitive — **verified 2026-08-20**.

## Explicitly out of scope

- License questions of studying source (note: respect upstream licenses when the rebuild
  is more port than reimplementation).

## Source segment

> "don't download those. I wrote them for me. What you should do is point your agents at
> them, have the agents look at them, and then build one for you"

Context: "I think that's a far better way of specifying the essence of something and
then customizing it to your particular need."
