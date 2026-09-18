# claude-config

Kyle's Claude Code configuration: skills, commands, agents, and the quality-gate machinery they share. This glossary is the ubiquitous language for that machinery.

## Language

**Gate**:
A deterministic, machine-runnable check with a binary pass/fail verdict and a loop rule (what must happen until it passes). The orchestrating session runs it itself — its verdict is never taken on an agent's word — and only gates may block work.
_Avoid_: check, quality bar, verifier

**Instrument**:
An observability aid for a human auditor — a map, dashboard, or commentary. It informs judgment; it never blocks work.
_Avoid_: gate (for anything non-blocking), report

**Preflight**:
The evidence pass before a merge proposal: every Gate and measurement wired into the repo is run over the diff, and the results are cited in the propose-first review-scope recommendation. A clean Preflight argues the scope down (full loop → single round → skip); it never blocks by itself.
_Avoid_: pre-check, CI

**Promotion**:
Granting a proven check the merge veto in one repo, after a report-only proving period shows real signal and no false blocks. The veto is earned per-repo, never granted globally or on day one.
_Avoid_: enabling, turning on

**Demotion**:
The kill rule for a noisy Gate: zero actionable signal plus one or more false blocks in its first month costs it the veto — it becomes an Instrument. Demoted, never tuned.
_Avoid_: disabling, tuning

## Steering lifecycle

**Steering surface**:
Everything a session loads before the first prompt that shapes how it interprets asks, routes to skills, plans, or builds — `CLAUDE.md` sections, skill and command descriptions, agents, plugins, MCP servers, hooks. Two costs ride on it: behavioral steering and token weight.
_Avoid_: memory (for anything but `CLAUDE.md` and auto-memory), config, context

**Retire**:
Removing an item from the steering surface for good, with a ledger line recording why and how to restore it. Git history or a backup is the archive; nothing stays on disk as a stub.
_Avoid_: delete, disable, prune, cleanse

**Pause**:
Keeping an item on disk but out of the steering surface because it is likely coming back. A paused item is not retired and gets no ledger line.
_Avoid_: disable, archive, retire

**Relocate**:
Keeping an item's content but moving it out of the always-loaded surface so it loads on demand. Relocation is `/trim-context`'s verb, never `retire`'s.
_Avoid_: trim, defer, retire
