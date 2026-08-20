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

A `wayfinder:research` ticket is AFK by construction, so the whole thing runs without Kyle. Two extra obligations:

- Capture the findings on a throwaway `research/<name>` branch rather than the working branch, and leave a context pointer (the branch name plus the file path) on the ticket.
- Resolve the ticket with the **answer to its question**, not a link to the file. The map's Decisions-so-far gets a one-line gist; the detail stays in the ticket and the file.

Research is the one wayfinder ticket type that may be resolved several to a session, because none of them costs Kyle a conversation.

## Unattended runs

This skill is already AFK by design — no gate, nothing to wait for. Run it end to end and report where the file landed.
