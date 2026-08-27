---
description: Runs the target repo's own wired CRAP tooling and presents the ranked worst-functions report — discovering the command from that repo's "Wired gates (Preflight)" note rather than assuming a filename. Report-only: it never blocks, never installs or generates tooling, and says plainly when a repo has nothing wired.
argument-hint: [repo path — empty = current directory]
allowed-tools: Bash, Read, Glob, Grep
---

# /crap-check — run this repo's wired CRAP ranking and read it back

A CRAP score is `complexity² × (1 − coverage)³ + complexity` per function: high
complexity that nothing tests. You are here to **run the tooling the repo already
has** and present the ranking. You are not here to build it.

Target repo: **$ARGUMENTS** (empty → the current working directory).

## Step 1 — discover the command (never assume a filename)

Read the target repo's `CLAUDE.md` and find its **"Wired gates (Preflight)"**
section. That note is the contract: it names the exact commands, what their exit
codes mean, and how to read their output. Take the CRAP-ranking command **verbatim
from the note** — script names and runners differ per repo, and a guessed path is
how this command silently reports on the wrong thing.

If the repo has no such note, or the note lists no CRAP-ranking gate:

> **Nothing wired.** `<repo>` has no CRAP tooling in its "Wired gates (Preflight)"
> note, so there is no ranking to run.

Then **stop**. Do not write a script, install a coverage provider, add an npm
script, or improvise an equivalent — wiring a gate into a repo is a deliberate,
separately-reviewed change (see claude-config's
[`docs/adr/0001-gates-earn-the-veto.md`](../docs/adr/0001-gates-earn-the-veto.md)),
not a side effect of asking for a report. Offer to do it as its own piece of work if
Kyle wants it.

## Step 2 — run it

Run the discovered command exactly as the note writes it, from the repo root.
It usually regenerates coverage first, so it can take a minute.

**Exit codes are not uniform across gates and the note says which applies here.** A
ranking has no pass/fail, so its command may always exit 0 — that is by design, not
a bug, and it does not mean "clean". Conversely a non-zero exit from a gate whose
note says non-zero means "violated" is a *finding*, not broken tooling. If the
command genuinely fails to run (missing coverage file, missing dependency, crash),
report that plainly as **no report produced** and stop — never present a partial or
stale ranking as a fresh one.

## Step 3 — present the ranking

Show the worst functions, worst first, as a table: **function · file:line ·
complexity · coverage · CRAP**. Flag every score above the threshold the note
states (**> 6** where it doesn't say otherwise — agent calibration; humans
conventionally run under 4, per the agent-tuned-thresholds sentence in the global
`CLAUDE.md`).

Apply any reading guidance the note gives. Repos commonly have whole classes of
code that are 0%-covered *by their own convention* (UI components, game scenes,
anything playtest- or e2e-gated), and for those the score degenerates to a pure
complexity ranking that will dominate the top of the list. When the note names such
a class, **split the table** — flagged-by-convention vs. real complexity-vs-coverage
signal — and say which half is worth acting on. Don't average them together.

Close with 2–4 lines: how many functions cleared the threshold, which one or two are
genuinely worth attention and why, and — if this was run as part of a merge proposal
— one line usable as Preflight evidence.

## Boundaries

- **Report-only.** This command has no veto. It does not gate a merge, fail a
  build, or block a commit. Promotion of a gate to blocking is Kyle's explicit
  per-repo call, recorded in that repo's `CLAUDE.md`.
- **It never writes to the target repo** — no scripts, no config, no thresholds, no
  coverage settings. It runs a command and reads the output.
- **It never lowers a threshold to make a report look better.** The number is
  the point.
