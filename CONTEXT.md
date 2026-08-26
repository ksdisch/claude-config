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
