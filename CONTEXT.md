# claude-config

Kyle's Claude Code configuration: skills, commands, agents, and the quality-gate machinery they share. This glossary is the ubiquitous language for that machinery.

## Language

**Gate**:
A deterministic, machine-runnable check with a binary pass/fail verdict and a loop rule (what must happen until it passes). The orchestrating session runs it itself — its verdict is never taken on an agent's word — and only gates may block work.
_Avoid_: check, quality bar, verifier

**Instrument**:
An observability aid for a human auditor — a map, dashboard, or commentary. It informs judgment; it never blocks work.
_Avoid_: gate (for anything non-blocking), report
