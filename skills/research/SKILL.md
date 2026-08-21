---
name: research
description: Delegate reading legwork to a background agent and capture the findings as a cited Markdown file in the repo. Use when a decision is blocked on a fact that lives outside the working directory — third-party API behavior, library or framework docs, a spec, a standard, a pricing or limits table — and Kyle wants the reading done without it landing in his session. Triggers on "research X", "go read the docs on X", "find out how X actually works", "what does the X API do when", "dig into X and report back". NOT for: source discovery for a `/teach` learning workspace (use teach-research), sweeping arXiv for a next research project (use seed-hunt), rewriting a paper Kyle already has (use paper-eli5), or facts already answerable from this repo's own code (just read it).
---

Spin up a **background agent** to do the research, so the session keeps working while it reads, and so the reading itself never lands in the session's context. Its report is the deliverable.

## The agent's job

1. **Investigate against primary sources** — official docs, source code, specs, first-party APIs, the vendor's own changelog. Not a secondary write-up of them. Follow every claim back to the source that owns it.
2. **Write findings to a single Markdown file**, citing each claim's source with a URL or a `file:line` pointer. A claim with no citation does not go in the file.
3. **Save it where the repo already keeps such notes** — match the existing convention. If there is none, put it somewhere sensible and say where.

## Never fabricate a source

If a fact can't be traced to a primary source, the finding is **"not established"**, written down as such with what was searched and what came back empty. A plausible-looking citation to a page the agent didn't open is worse than no answer, because the whole point of delegating the reading is that nobody re-reads it downstream.

Version and date matter: record which version of the library, API, or spec the finding is true of, and when it was checked. A fact with no version is a fact with an expiry date nobody can see.

## When a wayfinder map dispatched this

A `wayfinder:research` ticket is AFK by construction, so the whole thing runs without Kyle. One obligation, and it is a boundary rather than a checklist:

**Investigate only.** Read, and write your own findings file. Touch nothing else — **no git operations, and no writes to the tracker at all**: no resolution comment, no closing the ticket, no line on the map. Then **return** three things: the findings file's path, a one-line gist of the answer, and the answer itself. The dispatching session resolves the ticket and commits your file. This is invariant `subagents-investigate-only` in the wayfinder skill, and it overrides that skill's Resolve procedures — those describe what your *parent* does with what you return.

Why the line sits there: several of you run at once inside **one shared working tree**. A branch checkout is process-global, so a subagent doing git drags its siblings and its parent off their branch. The map's Decisions-so-far is a single shared file, so concurrent appends lose lines. And a subagent that closed its ticket and then died before returning would leave a decision recorded on a closed ticket that never reaches the map — invisible, because the map is the only index anyone loads. Investigate-only removes all three: a subagent that dies has changed nothing, and its ticket is simply still open.

Research is the one wayfinder ticket type that may be worked several to a session, because none of them costs Kyle a conversation.

## Unattended runs

This skill is already AFK by design — no gate, nothing to wait for. Run it end to end and report where the file landed.

---

Vendored from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock), adapted to house conventions. Full notice: `THIRD-PARTY.md` in the claude-config repo.
