# reweave — design spec

**Date:** 2026-07-21
**Status:** proposed design, pre-implementation
**Deliverable:** one new skill at `skills/reweave/SKILL.md` (auto-invocable as `/reweave` via the `~/.claude/skills` symlink). No other files change.
**Lineage:** a port of Kyle's existing Claude.ai `reweave` slash command (a chat-only re-integration skill) into a Claude Code skill that also handles on-disk artifacts.

## Purpose

The user got a substantive response, then asked a follow-up about one part of it.
Now they want the ORIGINAL response back — rewritten as if the follow-up's answer
had been part of it all along — so they don't pay the "scroll up, find the answer,
mentally splice it in" tax themselves. Reweave regenerates that earlier target with
the follow-up folded in **at the source**, and returns one clean standalone version.

This is a *re-integration* task, distinct from summarizing the thread, compressing a
response, expanding a single point, or rewriting from scratch. The whole value is in
*how* the merge is done — integrate at the source, thread the idea forward, hold the
length — not in the mere fact that the new material appears somewhere.

## What Claude Code adds over the chat original

The Claude.ai version only ever reweaves a prior chat message. In a Claude Code
session, the "earlier response" comes in two shapes, and reweave handles both:

1. **A chat response** (in the transcript) — a code walkthrough, an architecture
   rundown, a plan, a tradeoff analysis, a debugging write-up, a recommendation.
   Reweave re-emits it to chat, standalone, with the follow-up folded in.
2. **An on-disk artifact** a prior turn wrote — `docs/plan.md`, a design doc, a
   README section, a spec, a PR/commit description draft. Reweave rewrites that file
   **in place**, threading a later decision or discovery through every section that
   now depends on it.

The second shape is the Claude Code–specific extension and the reason a naive
one-line edit is *not* what's wanted (see "Reweave vs. a normal edit").

## Triggering

Frontmatter description triggers on: `/reweave`, "reweave" / "reweave that",
"fold that in" / "bake that in" / "work that in" / "integrate that", "rewrite that
[explanation/plan/answer] with X baked in", "regenerate that with the clarification
folded in", "update the plan with that decision threaded through" — **even when the
word "reweave" is never used.**

Disambiguation carried in the description (this is the main misfire risk in Claude
Code): NOT a normal code/behavior edit ("add error handling to that function"), NOT
summarizing/compressing the thread, NOT expanding a single point, NOT rewriting a
target from scratch.

## Input (`$ARGUMENTS`)

The argument is optional and, when present, is used to pin down the target and the
new material — never to override the merge discipline:

- **Nothing** → use the defaults in "Pick the target" below.
- **A pointer to the target** — "the API-flow explanation", "docs/plan.md", "your
  second message" → that's the response/artifact to reweave.
- **A pointer to what to fold in** — "with the SQLite decision", "including the
  rate-limit finding" → that's the follow-up material to integrate.
- **A register/scope note** — "keep it tight", "in place" → honored where it doesn't
  conflict with the merge rules.

## Pick the target

- **Default:** the most recent substantive response before the follow-up exchange —
  chat message or the file a prior turn wrote, whichever the follow-up is about.
- **For a file target, the file on disk is the target**, not any chat rendering of
  it — reweave reads the current file and rewrites it, so it never regresses edits
  made since.
- **Reweaves stack.** If you've already reweaved once this session, target the
  LATEST reweave (the newest chat version, or the current on-disk file).
- **If which response is genuinely unclear, ask before writing.** One question, then
  proceed.

## Where the output goes (don't move the target)

The reweave lands wherever the original lived:

- **Chat target → chat.** Output the full reworked response inline, standalone.
- **File target → that same file, in place** (Edit/Write), then a 2–3 line note in
  chat on what threaded through. Do not dump a file's reweave into chat, and do not
  silently spin a chat explanation out into a new file — that's a different request.

## How to merge (this is the whole skill)

In priority order — these are what separate integration from a useless copy-paste:

1. **Integrate at the source, don't append.** Find where the target FIRST touches
   the relevant concept and place the new material there. Bolting the follow-up
   answer onto the bottom is the exact failure mode this skill exists to prevent —
   it's what the user could do themselves.
2. **Compress to what the target needs.** Distill the follow-up answer down; don't
   paste it wholesale. The unabridged version still lives above in the thread — this
   is the digestible cut, not a second copy.
3. **Thread it forward.** Update later sections/paragraphs to USE the new concept
   where it makes them stronger — a reframing, a callback, a sharper term. For a
   file, this means every section that referenced the old assumption now reflects
   the new one. That rippling is what makes it read native rather than patched.
4. **Hold the length.** Tighten or cut elsewhere as you add, so the result stays
   roughly as long as the original. Without this, every reweave bloats — and file
   targets get reweaved repeatedly, so a thrice-reweaved `plan.md` must still read
   lean, not 3× its original size.
5. **Preserve voice, structure, and closers.** Keep the original's tone, section
   shape, heading hierarchy, formatting habits, and any closing blocks (a Q1/Q2/Q3 +
   TLDR pattern, a "Next steps" list, a status line).
6. **Stand alone.** The result must read top-to-bottom with no knowledge of the
   follow-up exchange required.

## Reweave vs. a normal edit (the key Claude Code distinction)

For a file target, reweave and a plain edit can look superficially similar, so the
line matters:

- **A normal edit** changes one thing where you're told to change it — "make plan.md
  say SQLite." One line moves; nothing else is reconciled.
- **A reweave** folds a decision *through* the document: it finds the first mention,
  compresses the rationale in, threads the consequence into every dependent section,
  holds the length, and preserves structure — leaving a standalone doc that reads as
  if the decision had been there all along. The threading is the point.

And the hard boundary: **reweave never re-architects functional source code.**
Changing what code *does* is ordinary development, governed by correctness and
tests, not by "reads native." Reweave's on-disk targets are *explanatory/planning
prose* — plans, design docs, READMEs, specs, notes, PR/commit text, doc comments and
docstrings. If the follow-up is "change the behavior," that's an edit/dev task, not a
reweave; say so and hand it off.

## A tiny illustration of #1 + #2

Original chat response had: "A token is a subword chunk mapped to an integer ID."
The follow-up asked what BPE is; the answer explained the merge algorithm.

- **Integrated (good):** right after that sentence — "...mapped to an integer ID
  (produced by Byte-Pair Encoding, which repeatedly merges the most frequent
  adjacent character pairs into a frozen vocabulary)." One compressed clause, at the
  source.
- **Appended (bad):** the original returned untouched, with a full BPE section
  bolted onto the end. That's concatenation; the user gains nothing.

## When it doesn't fit

If the follow-up info genuinely has no natural home in the target, say so rather than
forcing it. Don't strip something important from the target to make room — find the
cut elsewhere, or flag the tension and let the user decide. If the follow-up isn't a
clarification of something the target already touches but genuinely new scope, it's
not a reweave — flag that too.

## Out of scope (YAGNI)

No thread summarization, no compression/expansion modes, no rewriting source-code
behavior, no creating a new file for a chat target (or vice versa) unless explicitly
asked, no multi-file cascade beyond the single named target. Reweave re-integrates
one target; that's it.

## Testing note

Per `superpowers:writing-skills`, the highest-risk behavior to verify is triggering
and disambiguation — specifically that reweave (a) fires on "fold that in / bake
that in" without the word "reweave", and (b) does NOT fire (or hand off) when the
user actually wants a behavior change to source code or a thread summary. A short
subagent pressure-test on those two cases before merge is recommended but optional;
call it if you want the extra confidence.

## Definition of done (for the skill itself)

`skills/reweave/SKILL.md` exists with house-style frontmatter (name + rich trigger
description carrying the NOT-fors) and a body encoding: target selection (chat vs
file, defaults, stacking), output destination (land where the target lived), the six
merge rules, the reweave-vs-edit distinction with the source-code boundary,
hold-the-length/anti-bloat, when-it-doesn't-fit, and a red-flags rationalization
table — all consistent with this spec.
