---
name: reweave
description: Regenerate an earlier response with a follow-up's answer folded into it at the source, so you get one clean standalone version instead of mentally splicing the follow-up back in yourself. Handles two target shapes in a Claude Code session — a prior CHAT response (code walkthrough, plan, tradeoff analysis, debugging write-up, recommendation), re-emitted to chat; and an on-disk PROSE/PLAN artifact a prior turn wrote (docs/plan.md, a design doc, a README section, a spec, a PR/commit draft), rewritten in place with the new decision threaded through every dependent section. Use whenever Kyle types /reweave, says "reweave" / "reweave that", or asks to "fold that in" / "bake that in" / "work that in" / "integrate that" / "rewrite that explanation with X baked in" / "update the plan with that decision threaded through" — even without the word "reweave". This is re-integration, NOT summarizing the thread, NOT compressing or expanding a point, NOT rewriting from scratch, and NOT changing what source code does (a behavior change is an ordinary edit — hand it off).
---

# Reweave — fold a follow-up's answer back into the response it belongs in

The user asked a substantive question, got a response, then asked a follow-up about
one part of it. Now they want the ORIGINAL target back — rewritten as if the
follow-up's answer had been part of it all along — so they don't pay the "scroll up,
find the answer, mentally splice it in" tax themselves. Regenerate the target with
the follow-up folded in **at the source** and return one clean standalone version.

This is a *re-integration* task. It is NOT summarizing the thread, NOT compressing or
expanding a point, NOT rewriting from scratch, and NOT changing what source code
*does*. The value is entirely in *how* the merge is done — integrate at the source,
thread the idea forward, hold the length — not in the mere fact that the new material
appears somewhere. Appending it at the bottom is exactly what the user could do
themselves, and exactly what this skill exists to prevent.

## Two target shapes — and the output lands where the target lived

| Target | Reweave to | After |
|---|---|---|
| A prior **chat response** (walkthrough, plan, analysis, debug write-up, rec) | **chat**, standalone, inline | — |
| An on-disk **prose/plan artifact** a prior turn wrote (`docs/plan.md`, design doc, README section, spec, PR/commit draft, docstring) | **that same file, in place** (Read → Edit/Write) | a 2–3 line note in chat on what threaded through |

Don't move the target: never dump a file's reweave into chat, and never silently spin
a chat explanation out into a new file — that's a different request.

## Pick the target

- **Default:** the most recent substantive response before the follow-up exchange —
  chat message or the file a prior turn wrote, whichever the follow-up is about.
- **For a file, the file on disk is the target** — Read it and rewrite from that, so
  you never regress edits made since it was written.
- **Reweaves stack.** Already reweaved once this session? Target the LATEST reweave
  (the newest chat version, or the current on-disk file).
- **Genuinely unclear which response?** Ask once, then proceed.

## How to merge (this is the whole skill)

In priority order — these are the difference between integration and a useless
copy-paste:

1. **Integrate at the source, don't append.** Find where the target FIRST touches the
   relevant concept and place the new material there. Dumping the follow-up answer at
   the bottom is the failure mode this skill prevents.
2. **Compress to what the target needs.** Distill the follow-up answer down — don't
   paste it wholesale. The unabridged version still lives above in the thread; this is
   the digestible cut, not a second copy.
3. **Thread it forward.** Update later sections/paragraphs to USE the new concept
   where it makes them stronger — a reframing, a callback, a sharper term. In a file,
   every section that referenced the old assumption now reflects the new one. That
   rippling is what makes it read native rather than patched.
4. **Hold the length.** Tighten or cut elsewhere as you add, so the result stays
   roughly as long as the original. This is hardest — and matters most — when the
   follow-up is a *decision or scope-add* ("use SQLite instead"), which drags in
   genuinely new consequences that resist compression; a follow-up that merely
   *clarifies* something the target already gestured at compresses cleanly. So when
   you're folding in a decision, expect the creep and pay it back by cutting hardest.
   Files get reweaved repeatedly — a thrice-reweaved `plan.md` must still read lean,
   not 3× its size.
5. **Preserve voice, structure, and closers.** Keep the original's tone, section
   shape, heading hierarchy, formatting habits, and any closing blocks (a Q1/Q2/Q3 +
   TLDR pattern, a "Next steps" list, a status line).
6. **Stand alone.** The result must read top-to-bottom with no knowledge of the
   follow-up exchange required.

## Reweave vs. a normal edit (the Claude Code line)

For a file target, reweave and a plain edit can look similar, so hold the line:

- **A normal edit** changes one thing where you're told — "make plan.md say SQLite."
  One line moves; nothing else is reconciled.
- **A reweave** folds a decision *through* the document: first mention → compress the
  rationale in → thread the consequence into every dependent section → hold length →
  preserve structure, leaving a standalone doc that reads as if the decision had been
  there all along. The threading is the point.

**Hard boundary: reweave never re-architects functional source code.** Changing what
code *does* is ordinary development, governed by correctness and tests, not by "reads
native." Reweave's on-disk targets are *explanatory/planning prose* — plans, design
docs, READMEs, specs, notes, PR/commit text, doc comments and docstrings. If the
follow-up is "change the behavior," say so and hand it off as an edit; don't reweave.

## A tiny illustration of #1 + #2

Original had: "A token is a subword chunk mapped to an integer ID." The follow-up
asked what BPE is; the answer explained the merge algorithm.

- **Integrated (good):** right after that sentence — "...mapped to an integer ID
  (produced by Byte-Pair Encoding, which repeatedly merges the most frequent adjacent
  character pairs into a frozen vocabulary)." One compressed clause, at the source.
- **Appended (bad):** the original returned untouched, with a full BPE section bolted
  onto the end. That's concatenation; the user gains nothing.

## When it doesn't fit

If the follow-up info genuinely has no natural home in the target, say so rather than
forcing it. Don't strip something important to make room — find the cut elsewhere, or
flag the tension and let the user decide. If the follow-up isn't a clarification of
something the target already touches but genuinely new scope, it's not a reweave —
flag that too.

## Red flags — stop and reconsider

| Drift / rationalization | Reality |
|---|---|
| Bolting the follow-up answer onto the end of the target | Concatenation, not integration — the exact tax this skill removes. Go to the first mention. |
| Pasting the follow-up answer in full | It already lives above in the thread. Compress to the digestible cut. |
| Changing only the one line, leaving later sections stale | That's a normal edit. Reweave threads the consequence through every dependent section. |
| Reweaving what code *does* | Behavior changes are ordinary edits, governed by tests. Hand it off; reweave is for prose/plans. |
| Letting the target grow — worst when folding in a *decision/scope-add* (new consequences resist compression), less so for a clarification | Hold the length: expect the creep, pay it back by cutting hardest elsewhere. Repeatedly-reweaved files especially. |
| Emitting a file's reweave into chat (or a chat answer into a new file) | Land where the target lived. Moving it is a different request. |
| Forcing material that has no home | Say it doesn't fit, or flag it as new scope — don't mangle the target to absorb it. |
