# The Coliseum: commands earn their keep on lived-invocation evidence

**Status:** Idea — not committed. Added by `/brainstorm` (`moonshot` mode) on 2026-06-18.
**Lens:** futurist · **Fit:** stretch · **Boldness:** audacious

## Premise

A prose-only, no-tests/no-CI config (A3) can still have a measurable correctness
surface — not unit tests, but **lived-invocation evidence**. The cheapest honest
signal already exists in the transcript log and is thrown away every session. A
config that reads its own usage can curate itself: keep what's used, merge what
overlaps, patch the spec lines that keep getting hand-corrected, and retire what
nobody invokes — turning a library that only grows into one that earns and loses
its commands.

## The bet

The one thing that must be true: **crude lived-invocation data** — command, branch,
timestamp, whether the very next human turn was a correction — is a sharper signal
about which prose specs are weak/dead/redundant than Kyle's recall is, **and Kyle
will actually act on a verdict that names names.** (Targets **A3** — correctness only
surfaces at runtime, never captured — and **A4** — discoverability-by-memory.)

Veteran reaction: *"You're building analytics for a 29-file personal config one guy
uses — the trace will rot the day after you build it, and you'll have a `/retro` you
run twice."* The answer: the bet is **not** the hook fidelity (deliberately dumb,
append-only, can't drift) — it's that a config which can say *"reframe-orchestrator:
0 invocations in 90 days; handoff and wrap fire back-to-back 80% of the time"* changes
what Kyle builds next. Evidence replaces gut as the curator.

**Why now:** 18 commands + 11 skills = 29 specs, and the library grows per-commit with
no counter-pressure (A6) — nothing ever tells Kyle a command is dead weight (a deprecated
`/moonshot` alias was just removed by hand). The substrate is free: the session transcript
JSONL already records every `<command-name>/foo</command-name>`, and `settings.json` already
runs a Stop prompt-hook + PreToolUse Bash hooks, so instrumentation is an in-idiom pattern.

## Credible first step

Two real files. (1) A Stop-hook entry in `~/.claude/settings.json` (sibling to the existing
hooks) that greps the session transcript for `<command-name>` lines and appends one JSONL row
per fired command to `~/.claude/traces/usage.jsonl` — fields: timestamp, command, branch,
sessionId. ~10 lines of jq+grep, append-only, gitignored like `projects/` already is. (2) A new
`commands/retro.md` (pure prose, modeled on the read-state-then-write-artifact idiom of
`brainstorm.md`/`wrap.md`) that tallies `usage.jsonl` over the last N days and emits a
per-command verdict table with drafted edits (prune / merge / patch / leave). **Ship the
`/retro` reader first** against a hand-seeded trace file so the value is provable before the
hook is trusted.

## Decisions / open questions

- **Correction-detection fidelity:** v1 logs only objective facts and lets `/retro` read the
  transcript for correction signals at report time, so the hook can't drift. Is even a crude
  "next human turn looked corrective" flag worth it, or pure noise?
- **Unit of a verdict:** per-command counts only, or also co-occurrence (handoff+wrap together)
  and gate-adherence (did the run hit the spec's STOP/approval steps)? Co-occurrence is cheap
  and high-signal; gate-adherence needs transcript parsing.
- **Auto-apply?** Does `/retro` ever apply an edit, or strictly draft-and-propose? Act-vs-assess
  + the live-symlink blast radius argue draft-only — but that risks `/retro` becoming the unused
  command it warns about.
- **Cloud/vendored usage:** cloud/web + vendored repos won't write to local `~/.claude/traces/`.
  Is `/retro` deliberately a local-only, Kyle-only curator, or does it eventually ingest
  vendored-repo usage too?
- **Threshold honesty:** with one user, N is small — a verdict must weight "last used" and
  "irreplaceable" (e.g. `envsetup`), not just raw count, so it never retires a rare-but-load-bearing
  command.

## Dependencies

- `settings.json` Stop-hook slot (already populated — confirms multi-hook + jq-on-tool-input is
  a supported, in-use pattern).
- Session transcript JSONL under `~/.claude/projects/<slug>/` — confirmed to record
  `<command-name>/foo</command-name>` per invocation (verified this session).
- jq + grep (already relied on by existing hooks).
- `.gitignore` already excludes `projects/` and `history.jsonl` — `traces/` follows the same
  machine-local, never-committed rule.
- The read-state-then-write-artifact command idiom (`brainstorm.md`, `wrap.md`, `handoff.md`) as
  the template for `retro.md`.

## Explicitly out of scope (revisit later)

- Any model training, embeddings, or ML — verdicts are counts + co-occurrence + spec text.
- A telemetry service, dashboard, or daemon — it's a flat JSONL file and a prose command, full stop.
- Auto-editing/auto-deleting specs without Kyle merging — the config proposes, Kyle disposes.
- Cross-machine / cross-collaborator usage aggregation in v1 — local, single-user curator first.
- Replacing Kyle's memory or the one-line descriptions as the index — usage is an additional index.
- Instrumenting non-config tool use (raw Bash/Edit/Read) — only slash-command + skill invocations.

## Identity/positioning note

Shifts what claude-config IS from "a set of prose specs Kyle authors and remembers" to "a set of
prose specs that observes its own use and argues for its own pruning." The author stays human —
Claude never silently rewrites a spec — but the repo gains a second voice: the evidence. That's a
real identity move (the config acquires an opinion about itself), which is why it's stretch, not
tethered. The boldness is the Coliseum framing — commands must earn their keep or get voted off —
not the hook plumbing, which is deliberately the dumbest part.
