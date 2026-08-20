---
name: youtube-breakdown
description: >-
  Process a YouTube transcript or URL into a structured breakdown in one of four modes:
  Study Notes (deep retention), Quick Reference (skimmable triage), Critique (steelman-then-
  dismantle), or Actionable Insights (operator's takeaways). Always asks which mode before
  processing. Accepts a pasted transcript, a YouTube URL (fetched via the youtube-transcript
  skill), or a file path. Displays inline, then offers to save under ~/Learning. Trigger on
  "youtube breakdown", "break down this video", "analyze this video", "summarize this
  transcript", "study notes for this video", "critique this video", "what should I do with
  this video", "transcript breakdown", or any request to turn video content into structured
  notes.
---

# YouTube Breakdown

Turn a YouTube transcript into one of four structured breakdowns. The four modes are
genuinely different tools, not reshuffled versions of the same output — Study Notes wants
depth and hierarchy, Quick Reference wants ruthless compression, Critique wants adversarial
engagement, Actionable Insights wants a plan. Picking wrong wastes the run.

So: **always ask which mode before generating.** Never auto-pick.

---

## Mode Selection

Present the four options:

```
Which mode?
1. Study Notes — deep, hierarchical, for videos worth retaining long-term
2. Quick Reference — ruthless distillation, for triage or recall-at-a-glance
3. Critique — steelman then dismantle, for skeptical engagement
4. Actionable Insights — actions + frameworks separated, for tactical content
```

When the trigger phrase implies a mode ("critique this video" → Mode 3, "what should I do
with this video" → Mode 4, "study notes for this" → Mode 1), still confirm rather than
assume: *"Sounds like Critique mode — confirm or pick a different one?"* One turn is cheap;
a 900-word breakdown in the wrong register is not.

> **Auto-router (deliberately off).** A pre-flight classifier that reads the first ~500
> words and recommends a mode is specced under [Future Extensions](#future-extensions).
> Kyle's standing preference is explicit choice. Revisit only if mode-picking starts to
> feel like friction.

---

## Input Handling

| Input | How to handle |
|---|---|
| **Pasted transcript text** | Use directly. No fetching. |
| **YouTube URL** | Invoke the **`youtube-transcript`** skill — it handles caption discovery, the manual → auto → Whisper fallback chain, and overlap cleanup. Keep its output in the scratchpad; it's an intermediate here, not a deliverable. |
| **File path** | Read it directly. |

Don't hand-roll URL fetching. `WebFetch` against a third-party transcript site was the old
approach and it fails silently — those sites rate-limit, restructure, and return a page of
boilerplate that looks like a short transcript. `youtube-transcript` goes to the source.

If the input is ambiguous — a non-YouTube URL, or text too short to plausibly be a
transcript — ask one clarifying question. Don't guess.

**Long transcripts (>30k words):** say so up front and offer to chunk-process — run the
mode against sections, then stitch — rather than quietly producing a breakdown that thins
out toward the end.

---

## Output Handling

1. **Display the breakdown inline.** Full output, properly formatted. This always happens
   and works anywhere, including cloud sessions with no filesystem.

2. **Append the mode's handoff line** (each mode below names its own). It is an offer:
   never *act* on it without a yes. "Don't act on it" is not "end the turn" — keep going to
   step 3 in the same turn, and let Kyle answer both the handoff and the save question
   together.

3. **Offer to save, and ask where.** Kyle wants the choice every time, so propose a default
   and list the alternatives in one turn:

   > Save this? Default is `~/Learning/youtube-notes/2026-08-19-<title>-study-notes.md`.
   > You also have teach workspaces at `~/Learning/party-line/`,
   > `~/Learning/gearhead-products/`, `~/Learning/prime-agent/` — or name another path.

   Read `~/Learning/` before offering, so the workspaces you list are the ones that
   actually exist rather than the three named above, which are only an example of the
   shape. Filing a breakdown into a teach workspace puts it where `/teach` and
   `/teach-research` will find it, which is often the point.

4. **If Kyle declines, leave it inline.** Don't push, don't ask twice.

### Filename and frontmatter

Slug: `YYYY-MM-DD-{kebab-case-video-title}-{mode}.md` — e.g.
`2026-08-19-andrej-karpathy-on-llms-study-notes.md`. If the title is unknown, use
`YYYY-MM-DD-youtube-breakdown-{mode}.md` and offer to rename once the title is known.

```yaml
---
title: "[video title]"
source: "[URL if available, else: pasted transcript]"
speaker: "[if identifiable, else: unknown]"
date_processed: [today, YYYY-MM-DD]
mode: study-notes | quick-reference | critique | actionable-insights
tags: [youtube, breakdown, {mode}]
---
```

**The three free-text fields are quoted, and that is not cosmetic.** Talk titles are full
of colons — "Andrej Karpathy: Software Is Changing Again" — and a bare `title: Andrej
Karpathy: Software Is Changing Again` is a YAML parse error, not a quirk. The whole
frontmatter block then reads as nothing to every parser that touches it. Any `"` inside the
value gets escaped as `\"`.

The `mode` value is one of those four kebab-case strings exactly — not capitalized, not
pluralized. It's what makes a folder of breakdowns sortable later, and a folder where half
the files say `study-notes` and half say `Study Notes` doesn't sort.

---

## Mode 1: Study Notes

**For:** videos worth retaining long-term — technical lectures, deep educational content,
frameworks to reference later.

````text
You are an expert study-notes generator. Internalize the transcript
deeply enough to teach it, then produce a hierarchical outline
optimized for learning and retention.

# PHASE 1: COMPREHENSION (internal, do not output)
1. Identify the video's domain, the speaker's expertise, and the
   core thesis.
2. Map the logical structure: what claims are made, what evidence
   supports each, and how ideas connect.
3. Flag areas where the speaker glosses over nuance, makes
   unsupported claims, or omits obvious counterpoints.

# PHASE 2: OUTPUT
Use a strict hierarchical outline (H1 → H2 → H3 → bullets). Be
concise but thorough — depth without fluff.

## 1. Snapshot
- **Title/Topic:** [inferred]
- **Speaker & credibility signals:** [who, why qualified or not]
- **Core thesis (1 sentence):** [the single defended claim]
- **Who this is for:** [audience / prerequisite knowledge]

## 2. Key Arguments & Claims
For each major claim (3–7):
- **Claim:** [clear proposition]
  - **Supporting evidence/reasoning:** [how defended]
  - **Illustrative quote or example:** [short quote in "…" or
    paraphrased example]
  - **Strength rating:** [Strong / Moderate / Weak] — and why

## 3. Mental Model / Framework
If the video introduces a framework, render it as a clean hierarchy
with definitions. If none, write "No explicit framework — see Key
Arguments."

## 4. Counterpoints & Gaps
- **Unstated assumptions:** [what's taken for granted]
- **Missing counterarguments:** [obvious objections not addressed]
- **Oversimplifications:** [where nuance was sacrificed]
- **Claims I'd verify independently:** [worth fact-checking]

## 5. Action Items & Takeaways
- **Top 3 insights worth retaining long-term:** [ranked]
- **Things to actually do:** [concrete actions, not vague advice]
- **How this connects to adjacent domains I likely know:**
  [analogies or bridges]

## 6. Further Reading & Next Steps
- **Sources the speaker cites:** [books, papers, people, tools]
- **Natural next rabbit holes:** [3–5 with one-line "why"]
- **If I wanted to go deeper, I would:** [single highest-leverage
  next step]

# RULES
- Never invent citations, quotes, or facts not in the transcript.
- If something is unclear, flag it rather than guessing.
- Prioritize clarity over comprehensiveness — cut anything that
  doesn't earn its place.
- Use plain language. Define jargon the first time it appears.
````

**Handoff** (inline only, never inside the saved file):

```
💡 The "Further Reading" above is good seed material — want me to run /teach-research to
turn it into a stocked learning workspace, or add this video to a NotebookLM notebook as a
source via notebook-assist?
```

---

## Mode 2: Quick Reference

**For:** triaging videos, deciding what deserves deeper attention, recall-at-a-glance for
videos already watched.

````text
You are a transcript distiller. Produce a scannable reference
document — something Kyle could re-read in under 60 seconds and
recall the video's contents.

# PHASE 1: COMPREHENSION (internal, do not output)
1. Identify the thesis and the 2–5 ideas that actually matter.
2. Cut throat-clearing, anecdote without payoff, or elaboration of
   already-clear points.

# PHASE 2: OUTPUT
Scale length to transcript density. A 10-min opinion video might
warrant 150 words; a 90-min technical lecture might warrant 600.
Err toward shorter — if in doubt, cut.

## Snapshot
- **Topic:** [one line]
- **Thesis:** [one sentence]
- **Verdict on watching the full video:** [Worth it / Skim it /
  Skip it] — and why in one line

## The Core Ideas
Bullet list. Each bullet is one idea, fewest words that preserve
meaning. No sub-bullets unless absolutely necessary.

## Memorable Specifics
Only if genuinely memorable: a statistic, turn of phrase, concrete
example. 3–5 max. Skip if nothing qualifies.

## If You Remember Only One Thing
[One sentence. The single idea worth carrying forward.]

# RULES
- No filler. No "the speaker discusses…" framing — just state the
  content.
- No invention. If the transcript doesn't support it, don't write
  it.
- Short sentences. Active voice. Cut adjectives.
````

**Handoff:** none. This mode's whole point is that it ends fast — a suggestion to do more
work fights the purpose. If the verdict is "Worth it", Kyle can rerun in another mode.

---

## Mode 3: Critique

**For:** bold or contrarian claims, frameworks under consideration, advice worth
pressure-testing before acting on.

````text
You are a rigorous intellectual critic. Engage with the speaker's
argument seriously — first by strengthening it, then by dismantling
it where warranted.

# PHASE 1: COMPREHENSION (internal, do not output)
1. Identify the speaker's core thesis and argument structure
   (premises → reasoning → conclusion).
2. Separate what is claimed from what is actually supported.
3. Note credibility signals, incentives, and rhetorical moves doing
   work the logic isn't.

# PHASE 2: OUTPUT

## 1. The Argument, Charitably Reconstructed
Steelman the speaker. In 3–6 bullets, render the strongest possible
version — including premises they implied but didn't state. If the
steelman is stronger than what was actually said, note that.

## 2. What They Got Right
- **Claims that hold up:** [which, and why]
- **Genuine contributions:** [what's novel or well-argued]
- **Where the speaker is more right than the audience might
  realize:** [non-obvious strengths]

## 3. Where the Argument Breaks Down
For each significant weakness:
- **The problem:** [logical gap, unsupported claim, bad evidence,
  motivated reasoning]
- **Why it matters:** [side point or core thesis?]
- **The stronger counter-position:** [what someone with the
  opposite view would say — and why it might be right]

## 4. Unexamined Assumptions
What is the speaker taking for granted that a thoughtful skeptic
would question? List 3–5.

## 5. The Verdict
- **Is the core thesis correct?** [Yes / Partially / No / Can't
  tell from this video] — with one paragraph of reasoning
- **What this video does well:** [one line]
- **What to distrust:** [one line]
- **Who should watch it anyway, and why:** [one line]

## 6. Deeper Reading
- **To pressure-test the speaker's view:** [2–3 sources that
  challenge it]
- **To understand the strongest version:** [2–3 sources that
  defend it better than the speaker does]
- **Adjacent thinkers worth engaging:** [who else is working in
  this space]

# RULES
- Steelman before critiquing. Non-negotiable.
- Distinguish "I disagree" from "this argument is weak." Critique
  the reasoning, not the conclusion.
- No manufactured disagreement. If the argument is good, say so.
- No invented sources. If you recommend a book, it must exist.
````

**Handoff** (inline only):

```
💡 The "Deeper Reading" above is good seed material — want me to run /teach-research on
this thread, or add the video to a NotebookLM notebook via notebook-assist?
```

---

## Mode 4: Actionable Insights

**For:** how-to content, productivity/business advice, tactical videos — when the goal is a
plan, not understanding.

````text
You are an implementation-focused analyst. Extract what Kyle can
actually use — separated cleanly into individual actions and
frameworks he can adopt as systems.

# PHASE 1: COMPREHENSION (internal, do not output)
1. Identify every claim, technique, heuristic, or framework.
2. For each, ask: "Is this actionable, or just interesting?"
   Discard the merely interesting.
3. Distinguish one-time actions from repeatable systems.

# PHASE 2: OUTPUT

## Snapshot
- **Topic:** [one line]
- **Core premise:** [one sentence]
- **Implementation difficulty:** [Low / Medium / High] — and why

## 1. Personal Action Items
Concrete things Kyle should do, ranked by leverage (highest first).
Each item must be:
- **Specific:** "Set up X" not "think about X"
- **Actionable this week:** if it takes >1 week to start, break it
  down
- **Tied to an outcome:** what changes when he does it

Format: **[Action]** — [why it matters] — [first step]

## 2. Frameworks & Systems to Adopt
Repeatable mental models or processes, not one-off actions.
For each:
- **Name:** [what to call it]
- **The framework itself:** [steps, principles, or structure —
  rendered as a clean hierarchy]
- **When to use it:** [trigger condition]
- **When it fails:** [where it breaks down — speaker probably
  didn't mention this, so infer it]

## 3. Heuristics Worth Internalizing
Short rules-of-thumb in one sentence each. 3–7 max. The "if X,
then Y" compressions worth memorizing.

## 4. What to Skip
Claims that sound actionable but aren't — too vague,
context-dependent, or wouldn't survive contact with reality.
Calling these out protects Kyle from wasted effort.

## 5. Implementation Sequence
If Kyle adopted everything worth adopting, what's the order?
Number them with a one-line rationale. Start with highest-leverage,
lowest-cost.

## 6. Further Resources
- **To go deeper on the frameworks:** [2–3 specific sources]
- **Tools or templates mentioned (or implied):** [what to look up]
- **The single highest-leverage next step beyond this video:**
  [one recommendation]

# RULES
- Separate actions from frameworks cleanly. Don't mix them.
- No vague advice. "Be more strategic" is not an action.
- If the video contains nothing actionable, say so — don't
  manufacture takeaways.
- Rank ruthlessly. The point is leverage, not completeness.
````

**Handoff** (inline only, and only when some action items genuinely look like tasks):

```
💡 Want me to push the top action items to Todoist?
```

On yes, use the Todoist MCP tools. Send only the items Kyle names or confirms — a
breakdown's action list is a menu, and dumping all of it into his inbox turns one useful
task into six he has to triage.

---

## Workflow Summary

1. **Ask or confirm the mode** — never auto-pick silently.
2. **Get the transcript** — paste, `youtube-transcript` for a URL, or read a file path.
3. **Run that mode's prompt** against it.
4. **Display the breakdown inline**, in full.
5. **Append the mode's handoff line** — an offer, never acted on unprompted.
6. **Offer to save** in the same turn, proposing `~/Learning/youtube-notes/{slug}.md` and
   listing the real teach workspaces under `~/Learning/` as alternatives. This step runs on
   every mode, including Mode 2, which has no handoff line.
7. **If saved**, confirm the path and offer to open it.

---

## Key Guardrails

- **Always ask which mode**, even when the trigger phrase implies one.
- **Never invent content.** Every mode prompt carries a no-invention rule; honor it. Mode 3
  is the sharpest case — a recommended book that doesn't exist is worse than no
  recommendation.
- **Don't auto-save, and ask where every time.** The destination is a real choice: a
  general note pile versus a teach workspace that `/teach` will read.
- **One mode per run.** For the same transcript in multiple modes, run them sequentially
  with separate save prompts. Don't batch outputs into one file.
- **Handoffs are offers.** Append the line and carry on to the save offer in the same turn.
  Never *chain into* `/teach-research`, `notebook-assist`, or Todoist without an explicit
  yes — that's what the offer is protecting against, not the save prompt.
- **Frontmatter precision** — the four kebab-case `mode` values exactly.

---

## Related

- **`youtube-transcript`** — supplies the text when the input is a URL.
- **`teach-research`** / **`teach`** — where a Study Notes or Critique "Further Reading"
  section naturally leads, if the topic is worth a real learning workspace.
- **`notebook-assist`** — adds the video to a NotebookLM notebook as a tracked source.

---

## Future Extensions

### Auto-mode router (currently disabled)

A pre-flight prompt that reads the first ~500 words and recommends a mode. Documented for
future activation; **not active**.

**To enable:** replace *Mode Selection* above with this routing logic, and ask only when
confidence is low.

```
Read the first ~500 words of the transcript and classify it:

- Tactical / how-to / advice → recommend Mode 4 (Actionable Insights)
- Strong opinion / contrarian thesis → recommend Mode 3 (Critique)
- Educational / technical / reference-worthy → recommend Mode 1 (Study Notes)
- Short / conversational / low-density → recommend Mode 2 (Quick Reference)

Confidence ≥ 80% → propose the mode and proceed if Kyle doesn't object.
Confidence < 80% → ask which mode, presenting the top 2 candidates first.
```

**Why it's off:** Kyle prefers explicit choice, and mode is high-leverage enough that the
one-turn cost is cheap insurance. Revisit if mode-picking starts to feel repetitive.

### Anki flashcard chain

A second pass over any breakdown (especially Study Notes) generating cloze-deletion cards
for spaced repetition. Deferred until there's a spaced-repetition system to feed.

### Multi-mode batch

Quick Reference plus one deeper mode in a single run for high-value videos. Useful, but it
doubles output length — deferred.

---

_Originally created 2026-04-22 as a vault-native skill; forked for home-base's Learning Hub
2026-06-06. Merged into this repo 2026-08-19 as the global version: the four mode prompts
are unchanged, while save handling moved to `~/Learning` with a per-run destination prompt,
URL input routes through `youtube-transcript` instead of `WebFetch`, and the `learn-next` /
`add-task` handoffs were repointed at `teach-research`, `notebook-assist`, and the Todoist
MCP. The home-base fork stays separate — it writes to the hub's own stores._
