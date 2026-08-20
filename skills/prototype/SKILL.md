---
name: prototype
description: Build throwaway code that answers a design question — either a single-file shareable HTML demo that drives a state model, or several radically different UI variations switchable on one route. Use when a question can't be settled by talking it through and needs something concrete to react to: "does this state model feel right", "what should this page look like", "show me a few options before I commit", "let me click through it", "mock up some variations", "prototype this". NOT for: implementing a UI against a target you already have (use match-the-mock or /screenshot-iterate), starting a real project (use kickoff or mini), or building the actual feature — a prototype is thrown away by construction.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered, using Kyle's prompt, the surrounding code, or by asking if he's around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a single shareable HTML file (free-play buttons plus tabbed guided walkthroughs) that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"** → [UI.md](UI.md). Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

The two branches produce very different artifacts, so getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and Kyle isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## The verdict is Kyle's, never yours

**Build the options. Do not choose between them.** This is the failure mode this skill exists to avoid: generating three variants, silently picking one, and reporting the question as settled. The whole value of a prototype is that a human reacts to something concrete — an agent reacting to its own artifact has learned nothing that talking wouldn't have produced more cheaply.

So: present every variant, name what each one trades away, say which you'd pick **and why**, then stop. A recommendation is welcome; a decision is not yours to record. The same holds for a logic demo — "I ran the walkthroughs and the model looks right" is not the answer to the question the demo was built to ask.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious, but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner: `pnpm <name>`, `python <path>`, `bun <path>`, etc. A logic demo is a single HTML file Kyle double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE, wipe me" name.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so the change is visible.
6. **Capture it when done.** Fold the validated decision into the real code, then capture the prototype itself as a **primary source**: commit it to a throwaway branch, out of `main`, and leave a context pointer to that branch on the implementation issue. Capture the answer too (the verdict and the question it settled) in the issue or a commit. The `main` branch keeps only the validated decision.

## When a wayfinder map dispatched this

A `wayfinder:prototype` ticket is **HITL**: it resolves through Kyle's reaction to the artifact and no other way. Build the prototype, link it from the ticket as an asset, hand it over, and **stop** — the ticket stays open and claimed until he's actually looked. Closing it on your own read of your own prototype is the single most-reported way this ticket type goes wrong.

## Unattended runs

Nobody is there to react, so the artifact is the entire deliverable. Build it, write the question it's asking at the top of it, list the variants and their tradeoffs, and stop. Never record a verdict, close a prototype ticket, or fold a variant into real code from an unattended run.
